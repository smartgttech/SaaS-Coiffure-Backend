# apps/journal/serializers.py
from rest_framework import serializers
from .models import JournalAction


class JournalActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalAction
        fields = [
            'id', 'utilisateur_email', 'type_action', 'ressource',
            'ressource_id', 'details_avant', 'details_apres', 'date',
        ]