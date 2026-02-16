# UPGC TimeSync API

Ce projet est une API Django conçue pour récupérer, stocker et servir l'emploi du temps de l'Université Peleforo Gbon Coulibaly (UPGC).

Il agit comme une interface entre le site web de l'université et vos applications (mobiles ou web), en offrant des données structurées (JSON) et fiables.

## 🚀 Fonctionnalités

*   **Scraping Intelligent** : Récupère automatiquement l'emploi du temps depuis le site officiel de l'UPGC.
*   **Base de Données Locale** : Stocke les cours pour un accès rapide et hors ligne (cache).
*   **API REST Simple** : Seulement deux points d'accès pour obtenir les cours.
*   **Support des Dates** : Accès à l'emploi du temps d'aujourd'hui ou de n'importe quelle date spécifique.

## 🛠 Prérequis

*   Python 3.8+
*   Pip

## 📦 Installation

1.  **Clonaer le projet**
    ```bash
    git clone <votre-repo-url>
    cd upgc
    ```

2.  **Installer les dépendances**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configuration de l'environnement**
    Créez un fichier `.env` à la racine du projet et ajoutez-y vos configurations (ou utilisez le modèle fourni) :
    ```env
    SECRET_KEY=votre_cle_secrete_django
    DEBUG=True
    ALLOWED_HOSTS=127.0.0.1,localhost
    ```

4.  **Préparer la base de données**
    ```bash
    python manage.py migrate
    ```

## ▶️ Démarrage

Lancez le serveur de développement :

```bash
python manage.py runserver
```

L'API sera accessible à l'adresse : `http://127.0.0.1:8000/`

## 🔗 Utilisation de l'API

L'application expose deux URLs principales :

### 1. Emploi du temps d'aujourd'hui
Retourne les cours prévus pour la date actuelle.

*   **URL** : `/aujourdhui/`
*   **Méthode** : `GET`
*   **Exemple** : `http://127.0.0.1:8000/aujourdhui/`

### 2. Emploi du temps par date
Retourne les cours pour une date spécifique.

*   **URL** : `/<jour>/<mois>/<annee>/`
*   **Méthode** : `GET`
*   **Exemple** : `http://127.0.0.1:8000/16/02/2026/` (pour le 16 février 2026)

## 📄 Structure des Données (Réponse)

```json
{
    "date": "2026-02-16",
    "jour_semaine": "Lundi",
    "zone": 2,
    "source": "scraping",
    "timestamp": "2026-02-16T18:30:00Z",
    "nombre_evenements": 2,
    "donnees": [
        {
            "horaire": "07:30 à 11:30",
            "type_cours": "CM",
            "enseignant": "Dr NOM Prenom",
            "intitule": "TITRE DU COURS",
            "niveau": "L1 BIO",
            "salle": "Amphi B",
            "jour": "2026-02-16",
            "ressource": "Amphi B"
        },
        ...
    ]
}
```

## 👤 Auteur

Projet développé pour faciliter l'accès à l'information des étudiants de l'UPGC.
