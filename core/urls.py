from django.urls import path
from .views import EmploiDuTempsDuJourAPIView

urlpatterns = [
    # 1. Emploi du temps du jour (défaut)
    path('aujourdhui/', EmploiDuTempsDuJourAPIView.as_view(), name='emploi-jour'),
    
    # 2. Emploi du temps par date (jour/mois/annee)
    path('<int:jour>/<int:mois>/<int:annee>/', EmploiDuTempsDuJourAPIView.as_view(), name='emploi-date'),
]