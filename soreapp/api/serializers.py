from rest_framework import serializers
from .models import SparqlResult

class ProfileSerializer(serializers.Serializer):
    property = serializers.CharField()
    value = serializers.CharField()
    tag = serializers.CharField()

class PersonSerializer(serializers.Serializer):
    person = serializers.CharField()
    data = serializers.ListField()