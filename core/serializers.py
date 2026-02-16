# emplois/serializers.py
from rest_framework import serializers
from .models import Cours

class CoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cours
        fields = '__all__'
        extra_kwargs = {
            'niveau': {'required': False, 'allow_blank': True},
            'salle': {'required': False, 'allow_blank': True},
            'enseignant': {'required': False, 'allow_blank': True},
            'type_cours': {'required': False, 'allow_blank': True},
            'intitule': {'required': False, 'allow_blank': True},
        }

class EmploiDuTempsJourResponseSerializer(serializers.Serializer):
    date = serializers.DateField()
    jour_semaine = serializers.CharField()
    zone = serializers.IntegerField()
    source = serializers.CharField()
    timestamp = serializers.DateTimeField()
    nombre_evenements = serializers.IntegerField()
    donnees = CoursSerializer(many=True)

class EmploiDuTempsSemaineResponseSerializer(serializers.Serializer):
    semaine = serializers.DictField()
    zone = serializers.IntegerField()
    nombre_total_evenements = serializers.IntegerField()
    jours = serializers.ListField()
    timestamp = serializers.DateTimeField()

class ErreurResponseSerializer(serializers.Serializer):
    erreur = serializers.CharField()
    code = serializers.IntegerField()
    details = serializers.DictField(required=False)
    timestamp = serializers.DateTimeField()

class InfoZoneSerializer(serializers.Serializer):
    zones_disponibles = serializers.ListField()
    zone_par_defaut = serializers.IntegerField()
    zones_avec_donnees = serializers.ListField()

class StatistiquesSerializer(serializers.Serializer):
    total_evenements = serializers.IntegerField()
    dernier_mise_a_jour = serializers.DateTimeField(allow_null=True)
    statistiques_par_type = serializers.ListField()
    zone_active = serializers.IntegerField()
    jours_avec_donnees = serializers.IntegerField()

class RechercheParametresSerializer(serializers.Serializer):
    matiere = serializers.CharField(required=False)
    enseignant = serializers.CharField(required=False)
    salle = serializers.CharField(required=False)
    type_activite = serializers.CharField(required=False)
    date_debut = serializers.DateField(required=False)
    date_fin = serializers.DateField(required=False)
    zone = serializers.IntegerField(required=False)

class RechercheResultatSerializer(serializers.Serializer):
    criteres_recherche = serializers.DictField()
    nombre_resultats = serializers.IntegerField()
    resultats = CoursSerializer(many=True)
    timestamp = serializers.DateTimeField()