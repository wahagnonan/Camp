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