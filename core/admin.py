from django.contrib import admin
from .models import Cours

@admin.register(Cours)
class CoursAdmin(admin.ModelAdmin):
    list_display = ('jour', 'horaire', 'intitule', 'type_cours', 'niveau', 'enseignant')
    list_filter = ('jour', 'type_cours', 'niveau')
    search_fields = ('intitule', 'enseignant', 'salle')
    ordering = ('-jour', 'horaire')
