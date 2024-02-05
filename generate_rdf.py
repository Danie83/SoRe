from rdflib import Graph, Literal, Namespace, RDF, XSD
from datetime import datetime
import json

rdf_file_path = 'LikeDislike.rdf'
with open(rdf_file_path, 'r') as file:
    rdf_xml_content = file.read()

g = Graph()
g.parse(data=rdf_xml_content, format="xml")

ns = Namespace("http://www.semanticweb.org/tudoronofrei/ontologies/2024/0/untitled-ontology-7/")
schema = Namespace("https://schema.org/")

user_list = []
with open('datasets/unique_users.json', 'r', encoding='utf-8') as file:
    for line in file:
        user_data = json.loads(line)
        if '.' in user_data['accountName']:
            continue
        user_list.append(user_data)

count = 0
for user in user_list:
    individual_uri = ns[f"#{user['accountName']}"]
    g.add((individual_uri, RDF.type, schema['Person']))
    for key, value in user.items():
        if isinstance(value, list):
            for i, item in enumerate(value):
                property_uri = ns[key.replace(' ', '_')]
                g.add((individual_uri, property_uri, Literal(item, datatype=XSD.string)))
        elif isinstance(value, datetime):
            property_uri = ns[key.replace(' ', '_')]
            g.add((individual_uri, property_uri, Literal(value.strftime('%Y-%m-%dT'), datatype=XSD.dateTime)))
        else:
            property_uri = ns[key.replace(' ', '_')]
            g.add((individual_uri, property_uri, Literal(value, datatype=XSD.string)))
    count += 1
    if count % 15000 == 0:
        rdf_result = g.serialize(format="xml", encoding='utf-8').decode("utf-8")
        g = Graph()
        g.parse(data=rdf_xml_content, format="xml")
        with open(f'rdfdata/data-{count}.rdf', 'w', encoding='utf-8') as file:
            file.write(rdf_result)

rdf_result = g.serialize(format="xml", encoding='utf-8').decode("utf-8")
with open(f'rdfdata/data-{count}.rdf', 'w', encoding='utf-8') as file:
    file.write(rdf_result)