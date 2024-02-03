from rest_framework import serializers
from .models import SparqlResult

class ProfileSerializer(serializers.Serializer):
    property = serializers.CharField()
    value = serializers.CharField()
    tag = serializers.CharField()

class ProfilesSerializer(serializers.Serializer):
    person = serializers.CharField()
    username = serializers.CharField()
    data = serializers.ListField()