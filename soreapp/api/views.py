from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.models import UserProfile
from .serializers import *
from SPARQLWrapper import SPARQLWrapper, JSON


class ProfileAPIView(APIView):
    def get_profile_data(self, username):
        sparql_endpoint = "http://localhost:3030/ds/query"
        query = f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX schema: <https://schema.org/>
            PREFIX myont: <http://www.semanticweb.org/tudoronofrei/ontologies/2024/0/untitled-ontology-7/>

            SELECT ?property ?value ?tag
            WHERE {{
                myont:\#{username} ?property ?value.
                BIND(strafter(str(?property), str(myont:)) AS ?tag)
            }}
        """

        sparql = SPARQLWrapper(sparql_endpoint)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        serializer_data = []

        for result in results['results']['bindings']:
            if result['tag']['value'] is None or len(result['tag']['value']) == 0:
                continue
            serializer_data.append({
                'property': result['property']['value'],
                'value': result['value']['value'],
                'tag': result['tag']['value'],
            })

        serializer = ProfileSerializer(data=serializer_data, many=True)

        if serializer.is_valid():
            return serializer.data, status.HTTP_200_OK
        return serializer.errors, status.HTTP_400_BAD_REQUEST

    def get(self, request, *args, **kwargs):
        try:
            if not request.user.is_authenticated:
                raise UserProfile.DoesNotExist
            
            current_user = UserProfile.objects.get(user=request.user)
            username = current_user.user.username

            api_data, response_status = self.get_profile_data(username)

            return Response(api_data, status=response_status)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ProfilesAPIView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            if not request.user.is_authenticated:
                raise UserProfile.DoesNotExist
            
            current_user = UserProfile.objects.get(user=request.user)
            username = current_user.user.username

            sparql_endpoint = "http://localhost:3030/ds/query"
            query = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX schema: <https://schema.org/>
                PREFIX myont: <http://www.semanticweb.org/tudoronofrei/ontologies/2024/0/untitled-ontology-7/>

                SELECT ?person ?property ?value ?tag
                WHERE {
                    ?person rdf:type schema:Person.
                    ?person ?property ?value.
                    BIND(strafter(str(?property), str(myont:)) AS ?tag)
                }
            """
            sparql = SPARQLWrapper(sparql_endpoint)
            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()

            serializer_data = {}

            for result in results['results']['bindings']:
                person_uri = result['person']['value']

                if person_uri not in serializer_data:
                    serializer_data[person_uri] = {
                        'person': person_uri,
                        'data': [],
                    }

                serializer_data[person_uri]['data'].append({
                    'property': result['property']['value'],
                    'value': result['value']['value'],
                    'tag': result['tag']['value'],
                })

            serializer_list_data = list(serializer_data.values())
            serializer = PersonSerializer(data=serializer_list_data, many=True)

            if serializer.is_valid():
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=400)
        
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)