# core/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db import transaction
from django.db.models import Count, Q
from datetime import datetime, date, timedelta
import logging

from .models import Cours
from .scraping import ExtracteurUPGC
from .serializers import (
    CoursSerializer,
    EmploiDuTempsJourResponseSerializer,
    EmploiDuTempsSemaineResponseSerializer,
    ErreurResponseSerializer
)

logger = logging.getLogger(__name__)

class EmploiDuTempsDuJourAPIView(APIView):
    """
    Endpoint principal pour l'emploi du temps.
    Gère : Jour, Date spécifique, Semaine, Actualisation.
    """
    
    def get(self, request, *args, **kwargs):
        try:
            zone = self._get_zone_param(request)
            date_cible = self._get_date_param(request)
            force_actualisation = self._get_bool_param(request, 'actualiser', False)
            semaine_complete = self._get_bool_param(request, 'semaine', False)
            
            if semaine_complete:
                resultat = self._recuperer_semaine_complete(zone, date_cible, force_actualisation)
                serializer = EmploiDuTempsSemaineResponseSerializer(data=resultat)
            else:
                resultat = self._recuperer_emploi_du_jour(zone, date_cible, force_actualisation)
                serializer = EmploiDuTempsJourResponseSerializer(data=resultat)
            
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return self._reponse_erreur(str(e), status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Erreur serveur: {e}", exc_info=True)
            return self._reponse_erreur(f"Erreur serveur: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_zone_param(self, request):
        return int(request.GET.get('zone', '2'))
    
    def _get_date_param(self, request):
        """Récupère et valide le paramètre date (QueryParam ou PathParam)."""
        # 1. Priorité aux paramètres de chemin (URL: /16/02/2026/)
        if 'jour' in self.kwargs and 'mois' in self.kwargs and 'annee' in self.kwargs:
            try:
                return date(self.kwargs['annee'], self.kwargs['mois'], self.kwargs['jour'])
            except ValueError:
                raise ValueError("Date invalide dans l'URL")

        # 2. Paramètre GET standard (?date=...)
        date_str = request.GET.get('date')
        
        if not date_str:
            return date.today()
        
        # Support de plusieurs formats
        for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'):
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
                
        raise ValueError("Le format de date doit être YYYY-MM-DD ou DD/MM/YYYY")
    
    def _get_bool_param(self, request, param, default):
        val = request.GET.get(param, str(default))
        return val.lower() in ['true', '1', 'yes', 'vrai']
    
    def _recuperer_emploi_du_jour(self, zone, date_cible, force):
        # Note: Le modèle Cours n'a pas de champ 'zone'. On ignore le filtrage par zone en DB.
        if not force:
            donnees = Cours.objects.filter(jour=date_cible).order_by('horaire')
            if donnees.exists():
                return self._construire_reponse_jour(donnees, date_cible, zone, 'cache')
        
        # Scraping
        extracteur = ExtracteurUPGC()
        # Le scraper retourne une liste de dicts
        nouvelles_donnees = extracteur.recuperer_emploi_du_temps(zone=zone, date_cible=date_cible)
        
        # Sauvegarde
        saved_objs = self._sauvegarder_evenements(nouvelles_donnees)
        # On filtre pour ne retourner que le jour demandé (au cas où le scraper a ramené la semaine)
        saved_objs_jour = [c for c in saved_objs if c.jour == date_cible]
        
        return self._construire_reponse_jour(saved_objs_jour, date_cible, zone, 'scraping')
    
    def _recuperer_semaine_complete(self, zone, date_ref, force):
        start = date_ref - timedelta(days=date_ref.weekday())
        semaine_data = []
        for i in range(7):
            d = start + timedelta(days=i)
            # Pour éviter 7 appels de scraping, on pourrait scraper une fois la semaine.
            # Mais ExtracteurUPGC.recuperer_emploi_du_temps récupère déjà la semaine (souvent).
            # Simplification: on appelle jour par jour (le cache optimisera les appels suivants si le scraper a tout rempli)
            res_jour = self._recuperer_emploi_du_jour(zone, d, force)
            semaine_data.append({
                'date': d.isoformat(),
                'jour_semaine': self._get_jour_semaine_fr(d),
                'nombre_evenements': res_jour['nombre_evenements'],
                'source': res_jour['source'],
                'evenements': res_jour['donnees']
            })
            # Après le premier jour, si le scraper a rempli la semaine, force=False devrait utiliser le cache
            force = False 
            
        return {
            'semaine': {
                'debut': start.isoformat(),
                'fin': (start + timedelta(days=6)).isoformat(),
                'numero': start.isocalendar()[1],
                'annee': start.year
            },
            'zone': zone,
            'nombre_total_evenements': sum(j['nombre_evenements'] for j in semaine_data),
            'jours': semaine_data,
            'timestamp': timezone.now()
        }
    
    def _sauvegarder_evenements(self, data_list):
        saved = []
        with transaction.atomic():
            # On ne supprime pas tout, on update_or_create
            # Pour éviter doublons, on pourrait supprimer par jour ?
            # Cours.objects.filter(jour=...).delete() ?
            # Le scraper précédent utilisait update_or_create. Gardons ça.
            for item in data_list:
                obj, _ = Cours.objects.update_or_create(
                    jour=item['jour'],
                    horaire=item['horaire'],
                    ressource=item['ressource'],
                    defaults={
                        'type_cours': item['type_cours'],
                        'enseignant': item['enseignant'],
                        'intitule': item['intitule'],
                        'niveau': item['niveau'],
                        'salle': item['salle']
                    }
                )
                saved.append(obj)
        return saved
    
    def _construire_reponse_jour(self, evenements, date_cible, zone, source):
        # evenements est une liste d'objets Cours ou QuerySet
        serializer = CoursSerializer(evenements, many=True)
        return {
            'date': date_cible.isoformat(),
            'jour_semaine': self._get_jour_semaine_fr(date_cible),
            'zone': zone,
            'source': source,
            'timestamp': timezone.now(),
            'nombre_evenements': len(evenements),
            'donnees': serializer.data
        }
    
    def _get_jour_semaine_fr(self, d):
        return ['Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi','Dimanche'][d.weekday()]
    
    def _reponse_erreur(self, msg, code, details=None):
        return Response({
            'erreur': msg, 'code': code, 'details': details or {}, 'timestamp': timezone.now()
        }, status=code)
