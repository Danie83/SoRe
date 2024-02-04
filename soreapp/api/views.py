from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.models import UserProfile
from .serializers import *
from SPARQLWrapper import SPARQLWrapper, JSON

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

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

    def create_profile(self, username, data):
        sparql_endpoint = "http://localhost:3030/ds/"
        query = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX schema: <https://schema.org/>
PREFIX myont: <http://www.semanticweb.org/tudoronofrei/ontologies/2024/0/untitled-ontology-7/#>

INSERT DATA
{{
    myont:{} rdf:type schema:Person ;
{} .
}}
        """

        complete_string = ""
        for key, value in data.items():
            if isinstance(value, list):
                current = f"schema:{key} "
                current + ', '.join([f'"{value}"' for value in value])
                current + " ;\n"
            else:
                current = f"schema:{key} " + f'"{value}" ;\n'
            complete_string += current
        last_semicolon_index = complete_string.rfind(';')

        if last_semicolon_index != -1:
            result = complete_string[:last_semicolon_index] + complete_string[last_semicolon_index + 1:]
        else:
            result = complete_string

        query = query.format(username, result.strip('\n'))

        sparql = SPARQLWrapper(sparql_endpoint)
        sparql.method = "POST"

        sparql.setQuery(query)

        try:
            sparql.query()
            return "Profile created successfully.", 200
        except Exception as e:
            error_message = f"Error creating profile: {str(e)}"
            return {'error': error_message}, 500
        
    def update_profile(self, username, data):
        sparql_endpoint = "http://localhost:3030/ds/update"
        query_prepare = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX schema: <https://schema.org/>
PREFIX myont: <http://www.semanticweb.org/tudoronofrei/ontologies/2024/0/untitled-ontology-7/>
        """

        copy = query_prepare[:]
        unique_fields = ["firstName", "lastName", "name", "gender", "birthdate", "Country", "alumniOf", "MarryAction", "Occupation", "Organization", "email", "WebSite", "status", "description"]
        if any(element in data.keys() for element in unique_fields):
            delete_statement = """
                DELETE {{
                    {} .
                }}
                WHERE {{
                    {} .
                }}
            """
            delete = ""
            first = False
            for key in data.keys():
                if key in unique_fields:
                    if not first:
                        tmpstr = f"myont:\#{username} myont:{key} ?{key} ;\n"
                        delete += tmpstr
                        first = True
                    else:
                        tmpstr = f"myont:{key} ?{key} ;\n"
                        delete += tmpstr
            if len(delete) > 0:
                last_semicolon_index = delete.rfind(';')
                if last_semicolon_index != -1:
                    result = delete[:last_semicolon_index] + delete[last_semicolon_index + 1:]
                else:
                    result = delete
                query_prepare += delete_statement.format(result.strip('\n'), result.strip('\n'))

                sparql = SPARQLWrapper(sparql_endpoint)
                sparql.setMethod("POST")

                sparql.setQuery(query_prepare.strip('\n'))
                try:
                    sparql.query()
                    print("Profile created successfully.", 200)
                except Exception as e:
                    error_message = f"Error creating profile: {str(e)}"
                    print(error_message, 500)
        
        insert_statement = """
            INSERT DATA
            {{
                myont:\#{} {} .
            }}
        """
        complete_string = ""
        for key, value in data.items():
            if isinstance(value, list):
                current = f"myont:{key} "
                current + ', '.join([f'"{value}"' for value in value])
                current + " ;\n"
            else:
                current = f"myont:{key} " + f'"{value}" ;\n'
            complete_string += current
        last_semicolon_index = complete_string.rfind(';')

        if last_semicolon_index != -1:
            result = complete_string[:last_semicolon_index] + complete_string[last_semicolon_index + 1:]
        else:
            result = complete_string
        copy += insert_statement.format(username, result.strip('\n'))

        sparql1 = SPARQLWrapper(sparql_endpoint)
        sparql1.method = "POST"

        sparql1.setQuery(copy.strip('\n'))
        try:
            sparql1.query()
            return "Profile updated successfully.", 200
        except Exception as e:
            error_message = f"Error creating profile: {str(e)}"
            return {'error': error_message}, 500

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
    def get_profiles_data(self):
        sparql_endpoint = "http://localhost:3030/ds/query"
        query = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX schema: <https://schema.org/>
            PREFIX myont: <http://www.semanticweb.org/tudoronofrei/ontologies/2024/0/untitled-ontology-7/>

            SELECT ?person ?property ?value ?tag ?username
            WHERE {
                ?person rdf:type schema:Person.
                ?person ?property ?value.
                BIND(strafter(str(?property), str(myont:)) AS ?tag)
                BIND(REPLACE(strafter(str(?person), str(myont:)), "#", "") AS ?username)
            }
        """

        sparql = SPARQLWrapper(sparql_endpoint)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        serializer_data = {}

        for result in results['results']['bindings']:
            person_uri = result['person']['value']
            username = result['username']['value']

            if person_uri not in serializer_data:
                serializer_data[person_uri] = {
                    'person': person_uri,
                    'username': username,
                    'data': [],
                }

            serializer_data[person_uri]['data'].append({
                'property': result['property']['value'],
                'value': result['value']['value'],
                'tag': result['tag']['value'],
            })

        serializer_list_data = list(serializer_data.values())
        serializer = ProfilesSerializer(data=serializer_list_data, many=True)

        if serializer.is_valid():
            return serializer.data, status.HTTP_200_OK
        return serializer.errors, status.HTTP_400_BAD_REQUEST

    def get_unrated_profiles(self, username):
        data, sc = RateAPIView().get_profile_ratings(username)
        profiles, sc1 = ProfilesAPIView().get_profiles_data()
        to_remove = list()
        for profile in profiles:
            for d in data:
                if profile['username'] == d['value']:
                    to_remove.append(profile)
                    continue
        if len(to_remove) > 0:
            profiles = [profile for profile in profiles if profile not in to_remove]
        return profiles, sc1

    def get_full_profiles(self, username):
        data, sc = RateAPIView().get_profile_ratings(username)
        profiles, sc1 = ProfilesAPIView().get_profiles_data()
        all_profiles = profiles.copy()
        to_remove = list()
        for profile in profiles:
            for d in data:
                if profile['username'] == d['value']:
                    to_remove.append(profile)
                    continue
        unrated_profiles = list()
        rated_profiles = list()
        if len(to_remove) > 0:
            rated_profiles = to_remove.copy()
            unrated_profiles = [profile for profile in profiles if profile not in to_remove]
        else:
            unrated_profiles = all_profiles
        return all_profiles, unrated_profiles, rated_profiles, sc1
    
    def get(self, request, *args, **kwargs):
        try:
            if not request.user.is_authenticated:
                raise UserProfile.DoesNotExist
            
            api_data, response_status = self.get_profiles_data()

            return Response(api_data, status=response_status)
        
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class RateAPIView(APIView):
    def rate_profile(self, username, like, other_user):
        like_string = "LikeAction" if like else "DislikeAction"
        sparql_endpoint = "http://localhost:3030/ds/"
        query = f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX schema: <https://schema.org/>
            PREFIX myont: <http://www.semanticweb.org/tudoronofrei/ontologies/2024/0/untitled-ontology-7/>

            INSERT DATA
            {{
                myont:\#{username} myont:{like_string} "{other_user}" .
            }}
        """

        sparql = SPARQLWrapper(sparql_endpoint)
        sparql.method = "POST"

        sparql.setQuery(query)

        try:
            sparql.query()
            return "Profile created successfully.", 200
        except Exception as e:
            error_message = f"Error creating profile: {str(e)}"
            return {'error': error_message}, 500
        
    def get_profile_ratings(self, username):
        sparql_endpoint = "http://localhost:3030/ds/query"
        query = f"""
            PREFIX my: <http://www.mobile.com/model/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns>
            PREFIX schema: <https://schema.org/>
            PREFIX myont: <http://www.semanticweb.org/tudoronofrei/ontologies/2024/0/untitled-ontology-7/>

            SELECT ?property ?value ?type
            WHERE {{
                myont:\#{username} ?property ?value.
                FILTER (?property = myont:LikeAction || ?property = myont:DislikeAction)
                BIND(strafter(str(?property), str(myont:)) AS ?type)
            }}
        """

        sparql = SPARQLWrapper(sparql_endpoint)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        serializer_data = []

        for result in results['results']['bindings']:
            serializer_data.append({
                'property': result['property']['value'],
                'value': result['value']['value'],
                'type': result['type']['value'],
            })

        serializer = RatingSerializer(data=serializer_data, many=True)

        if serializer.is_valid():
            return serializer.data, status.HTTP_200_OK
        return serializer.errors, status.HTTP_400_BAD_REQUEST
    
    def get(self, request, *args, **kwargs):
        try:
            if not request.user.is_authenticated:
                raise UserProfile.DoesNotExist
            
            api_data, response_status = self.get_profile_ratings(request.user.username)

            return Response(api_data, status=response_status)
        
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class RecommenderAPIView(APIView):
    def get_recommendations(self, username):
        all_profiles, unrated_profiles, rated_profiles, sc = ProfilesAPIView().get_full_profiles(username)
        converted_all_profiles, accessible_all_profiles = convert_to_readable_profiles(all_profiles)
        converted_rated_profiles, accessible_rated_profiles = convert_to_readable_profiles(rated_profiles)
        converted_unrated_profiles, accessible_unrated_profiles = convert_to_readable_profiles(unrated_profiles)

        target_user = accessible_all_profiles[username]
        similar_users = get_similar_users(target_user, converted_all_profiles)
        for user, similarity in similar_users:
            print(user['username'], similarity)
        return all_profiles, sc

    def get(self, request, *args, **kwargs):
        try:
            if not request.user.is_authenticated:
                raise UserProfile.DoesNotExist
            
            api_data, response_status = self.get_recommendations(request.user.username)

            return Response(api_data, status=response_status)
        
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
def convert_to_readable_profiles(profiles):
    converted_profiles = list()
    accessible_profiles = dict()
    for profile in profiles:
        accessible_profiles[profile['username']] = profile
        profile_dict = dict()
        profile_dict['username'] = profile['username']
        for d in profile['data']:
            if d['tag'] not in profile_dict.keys():
                profile_dict[d['tag']] = d['value']
            else:
                existing_value = profile_dict[d['tag']]
                if not isinstance(existing_value, list):
                    existing_value = [existing_value]
                existing_value.append(d['value'])
                profile_dict[d['tag']] = existing_value
        converted_profiles.append(profile_dict)
    return converted_profiles, accessible_profiles

def calculate_similarity(target_user, user):
    target_liked_users = set(target_user.get('LikedAction', []))
    target_disliked_users = set(target_user.get('DislikedAction', []))
    user_liked_users = set(user.get('LikedAction', []))
    user_disliked_users = set(user.get('DislikeAction', []))

    common_liked_users = target_liked_users.intersection(user_liked_users)
    common_disliked_users = target_disliked_users.intersection(user_disliked_users)

    similarity = len(common_liked_users) - len(common_disliked_users)
    return similarity

def get_similar_users(target_user, all_users, top_n=10):
    similarities = []
    for user in all_users:
        if user != target_user:
            similarity = calculate_similarity(target_user, user)
            similarities.append((user, similarity))
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_n]