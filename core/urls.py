from django.urls import path
from .views import (
    EmploiDuTempsDuJourAPIView,
    ZonesDisponiblesAPIView,
    StatistiquesAPIView,
    RechercheAPIView,
    SanteAPIView,
    SynchronisationAPIView
)

urlpatterns = [
    path('emploi-du-temps/dujours/', EmploiDuTempsDuJourAPIView.as_view(), name='emploi-du-temps-jour'),
    path('zones/', ZonesDisponiblesAPIView.as_view(), name='zones-disponibles'),
    path('statistiques/', StatistiquesAPIView.as_view(), name='statistiques'),
    path('recherche/', RechercheAPIView.as_view(), name='recherche'),
    path('sante/', SanteAPIView.as_view(), name='sante'),
    path('synchroniser/', SynchronisationAPIView.as_view(), name='synchroniser'),
]