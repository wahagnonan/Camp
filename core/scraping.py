# core/scraping.py
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
import logging
import re
from .models import Cours

logger = logging.getLogger(__name__)

class ExtracteurUPGC:
    """
    Extracteur adapté pour le modèle Cours.
    Parcourt le tableau par ligne pour associer chaque cours à sa ressource (salle).
    """
    
    URL_BASE = "https://upgc.mygrr.net/week_all.php"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.pattern_horaire = r'(\d{1,2}:\d{2})\s*à\s*(\d{1,2}:\d{2})'
        self.types_activites_connus = ['TD', 'DEVOIR', 'TP', 'COURS', 'CM', 'EXAMEN', 'PROJET', 'SOUTENANCE']

    def parse_date_from_url(self, url):
        import urllib.parse
        try:
            parsed = urllib.parse.urlparse(url)
            params = urllib.parse.parse_qs(parsed.query)
            if 'year' in params and 'month' in params and 'day' in params:
                date_str = f"{params['year'][0]}-{params['month'][0]}-{params['day'][0]}"
                return datetime.strptime(date_str, "%Y-%m-%d").date()
        except Exception as e:
            logger.warning(f"Erreur parsing date url {url}: {e}")
        return None

    def normaliser_texte(self, texte):
        if texte:
            texte = texte.replace('il:', '11:')
            return ' '.join(texte.strip().split())
        return None
    
    def extraire_horaires(self, ligne):
        try:
            match = re.search(self.pattern_horaire, ligne)
            if match:
                return f"{match.group(1)} à {match.group(2)}"
        except Exception:
            pass
        return None

    def determiner_type_activite(self, ligne):
        ligne_norm = ligne.strip().upper()
        for type_connu in self.types_activites_connus:
            if type_connu in ligne_norm:
                return type_connu
        return "ACTIVITE"

    def extraire_depuis_cellule(self, cellule_html):
        """
        Extrait les infos d'une cellule pour le modèle Cours.
        """
        try:
            lignes_brutes = cellule_html.get_text(separator='\n').split('\n')
            lignes_propres = [l for l in [self.normaliser_texte(x) for x in lignes_brutes] if l and l != '@']
            
            # Métadonnées dans <i>
            balises_i = cellule_html.find_all('i')
            niveau = ''
            salle = ''
            for balise in balises_i:
                texte = balise.get_text(strip=True)
                if 'Niveau :' in texte:
                    niveau = texte.replace('Niveau :', '').strip()
                elif 'Salle :' in texte:
                    salle = texte.replace('Salle :', '').strip()

            infos = {
                'horaire': '',
                'type_cours': '',
                'enseignant': '',
                'intitule': '',
                'niveau': niveau,
                'salle': salle
            }
            
            if not lignes_propres:
                return None

            # Analyse des lignes
            idx_horaire = -1
            for i, ligne in enumerate(lignes_propres):
                horaire = self.extraire_horaires(ligne)
                if horaire:
                    infos['horaire'] = horaire
                    idx_horaire = i
                    break
            
            if idx_horaire != -1:
                # La ligne suivante est souvent le type
                if idx_horaire + 1 < len(lignes_propres):
                    infos['type_cours'] = self.determiner_type_activite(lignes_propres[idx_horaire + 1])
                
                # Ensuite Enseignant / Matière
                # Heuristique simple: si '/' présent -> enseignant, sinon matière
                reste = lignes_propres[idx_horaire + 2:]
                for l in reste:
                    if l == infos['niveau'] or f"Niveau : {infos['niveau']}" in l: continue
                    if l == infos['salle'] or f"Salle : {infos['salle']}" in l: continue
                    
                    if not infos['enseignant'] and ('/' in l or 'Dr' in l or 'M.' in l or 'Mme' in l):
                        infos['enseignant'] = l
                    elif not infos['intitule']:
                        infos['intitule'] = l
            
            if infos['horaire']:
                return infos
            
        except Exception as e:
            logger.error(f"Erreur extraction cellule: {e}")
        return None

    def recuperer_emploi_du_temps(self, zone=2, date_cible=None):
        if date_cible is None:
            date_cible = date.today()
            
        url = f"{self.URL_BASE}?area={zone}"
        # Note: L'URL avec params day/month/year risque de ne montrer que le jour
        # On veut la semaine pour avoir la structure table.semaine
        # Mais le script précédent utilisait week_all.php sans date pour avoir la semaine courante.
        # Si on veut une date spécifique, il faut naviguer vers la semaine contenant cette date.
        # Pour simplifier, on cible la semaine contenant la date cible.
        
        params = {
            'area': zone,
            'year': date_cible.year,
            'month': date_cible.month,
            'day': date_cible.day
        }
        
        try:
            logger.info(f"Scraping UPGC: zone={zone}, date={date_cible}")
            response = self.session.get(url, params=params)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            main_table = soup.select_one('div#planning2 table.semaine')
            if not main_table:
                logger.error("Tableau principal non trouvé")
                return []

            # 1. Dates
            dates = []
            headers_row = main_table.find('thead').find('tr')
            if headers_row:
                for th in headers_row.find_all('th'):
                    link = th.find('a')
                    if link and link.get('href'):
                        d = self.parse_date_from_url(link.get('href'))
                        dates.append(d)
                    elif "Ressources" not in th.get_text():
                        dates.append(None)

            # 2. Lignes
            tbody = main_table.find('tbody')
            if not tbody: return []
            
            evenements_modeles = []
            
            rows = tbody.find_all('tr', recursive=False)
            for row in rows:
                cells = row.find_all('td', recursive=False)
                if not cells: continue
                
                # Ressource
                ressource_raw = cells[0].get_text(separator=' ').strip()
                ressource = " ".join(ressource_raw.split())
                
                # Jours
                for i, cell in enumerate(cells[1:]):
                    if i >= len(dates): break
                    jour = dates[i]
                    if not jour: continue
                    
                    # Si on ne veut que la date cible ? 
                    # La méthode demande date_cible, mais récupère la semaine.
                    # On filtre à la fin ou on prend tout.
                    # Le view demande `recuperer_emploi_du_jour` donc idéalement on filtre.
                    # Mais pour `synchroniser`, on veut tout.
                    # On va tout retourner, le view filtrera ou sauvegardera tout.
                    
                    # Tables imbriquées
                    nested_tables = cell.find_all('table', class_='pleine')
                    if not nested_tables:
                        # Essayer cellule directe ?
                        # Le nouveau scraper de l'user regardait directement les cellules.
                        # Mais la structure HTML montre des tables imbriquées class="pleine"
                        # On supporte les deux:
                        parent_tds = [cell]
                    else:
                        parent_tds = [t.find('td') for t in nested_tables if t.find('td')]

                    for td in parent_tds:
                        infos = self.extraire_depuis_cellule(td)
                        if infos:
                            # Création dict pour modèle Cours
                            evt = {
                                'jour': jour,
                                'horaire': infos['horaire'],
                                'type_cours': infos['type_cours'] or 'Autre',
                                'enseignant': infos['enseignant'] or 'Non spécifié',
                                'intitule': infos['intitule'] or 'Cours',
                                'niveau': infos['niveau'],
                                'salle': infos['salle'] or ressource,
                                'ressource': ressource
                            }
                            evenements_modeles.append(evt)
            
            return evenements_modeles

        except Exception as e:
            logger.error(f"Erreur scraping: {e}")
            return []

# Alias pour compatibilité avec l'ancien code si nécessaire, 
# mais les nouvelles vues utilisent ExtracteurUPGC
def recuperer_emploi_du_temps():
    extracteur = ExtracteurUPGC()
    evts = extracteur.recuperer_emploi_du_temps()
    count = 0
    for evt in evts:
        Cours.objects.update_or_create(
            jour=evt['jour'],
            horaire=evt['horaire'],
            ressource=evt['ressource'],
            defaults={
                'type_cours': evt['type_cours'],
                'enseignant': evt['enseignant'],
                'intitule': evt['intitule'],
                'niveau': evt['niveau'],
                'salle': evt['salle']
            }
        )
        count += 1
    print(f"Import {count} cours")
