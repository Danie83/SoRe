from datetime import datetime, timedelta
from faker import Faker
import random
import pandas as pd
import numpy as np
import json

fake = Faker()

# CONFIG
minimum_age = 18
maximum_age = 70
minimum_follower_count = 0
maximum_follower_count = 10_000_000

education = pd.read_csv('datasets/education.csv')
emotions = pd.read_csv('datasets/emotion.csv')
hobbies = pd.read_csv('datasets/hobbylist.csv')
descriptions = pd.read_csv('datasets/combined_data.csv')

def validate_birthdate(date):
    current_date = datetime.now()
    upperbound = current_date - timedelta(days=365 * minimum_age)
    lowerbound = current_date - timedelta(days=365 * maximum_age)

    date = datetime(date.year, date.month, date.day)
    
    if lowerbound <= date <= upperbound:
        return date
    
    if lowerbound >= date:
        lower_year = lowerbound.year
        date_year = date.year
        dif_year = abs(lower_year - date_year)
        date += timedelta(days=dif_year * 365)
        date += timedelta(days=random.randint(minimum_age - 1, maximum_age - 1) * 365)
        return date
    
    if upperbound <= date:
        upper_year = upperbound.year
        date_year = date.year
        dif_year = abs(upper_year - date_year)
        date -= timedelta(days=dif_year * 365)
        date -= timedelta(days=random.randint(minimum_age - 1, maximum_age - 1) * 365)
        return date
    
def create_template_education():
    institutions = education['institution'].tolist()

    highschools = list()
    colleges = list()
    universities = list()
    leftovers = list()

    for institution in institutions:
        lower_institution = institution.lower()
        if "highschool" in lower_institution or "high school" in lower_institution:
            highschools.append(institution)
            institution_copy = institution.replace('Highschool', 'College') if "highschool" in lower_institution else institution.replace('High School', 'College')
            colleges.append(institution_copy)
            institution_copy = institution.replace('Highschool', 'University') if "highschool" in lower_institution else institution.replace('High School', 'University')
            universities.append(institution_copy)
            continue
        if "college" in lower_institution:
            colleges.append(institution)
            institution_copy = institution.replace('College', 'Highschool')
            highschools.append(institution_copy)
            institution_copy = institution.replace('College', 'University')
            universities.append(institution_copy)
            continue
        if "university" in lower_institution:
            universities.append(institution)
            institution_copy = institution.replace('University', 'Highschool')
            highschools.append(institution_copy)
            institution_copy = institution.replace('University', 'College')
            colleges.append(institution_copy)
            continue
        leftovers.append(institution)
    return highschools, colleges, universities

def get_age_based_random_education(birthdate, highschools, colleges, universities):
    current_date = datetime.now()
    age = current_date.year - birthdate.year - ((current_date.month, current_date.day) < (birthdate.month, birthdate.day))
    
    highschool = random.choice(highschools)
    college = random.choice(colleges)
    
    return highschool, college

def get_random_emotion():
    feelings = emotions['emotion'].tolist()

    return random.choice(feelings)

def get_random_hobbies():
    mapped_hobbies = dict()
    for _, row in hobbies.iterrows():
        key = row['Type']
        value = row['Hobby-name']

        if key not in mapped_hobbies:
            mapped_hobbies[key] = list()
        mapped_hobbies[key].append(value)

    personal_hobbies = list()
    for key, value in mapped_hobbies.items():
        personal_hobbies.append(random.choice(value))
    
    return personal_hobbies

def get_random_follower_count():
    probabilities = [0.8, 0.1, 0.05, 0.05]
    values = [random.randint(1, 10_000), random.randint(10_001, 100_000), random.randint(100_001, 1_000_000), random.randint(1_000_001, 10_000_000)]
    follower_count = np.random.choice(values, p=probabilities)
    real_count = follower_count

    if follower_count >= 1_000_000:
        formatted_count = f'{follower_count/1_000_000:.1f}M'
    elif follower_count >= 1_000:
        formatted_count = f'{follower_count/1_000:.1f}k'
    else:
        formatted_count = str(follower_count)

    return { 'formatted_count': formatted_count, 'count': real_count }

def get_random_post_count(follower_count):
    values = [0, random.randint(1, 100), random.randint(101, 1_000), random.randint(1_001, 10_000)]
    if follower_count <= 100:
        probabilities = [0.9, 0.1, 0, 0]
        return np.random.choice(values, p=probabilities)
    if follower_count <= 1_000:
        probabilities = [0.01, 0.79, 0.20, 0]
        return np.random.choice(values, p=probabilities)
    probabilities = [0, 0.1, 0.2, 0.7]
    return np.random.choice(values, p=probabilities)

def get_random_relationship_status(birthdate):
    current_date = datetime.now()
    age = current_date.year - birthdate.year - ((current_date.month, current_date.day) < (birthdate.month, birthdate.day))

    statuses = ['in a relationship', 'single', 'married', 'divorced', 'widow']
    if age <= 21:
        return random.choice(statuses[:2])
    return random.choice(statuses)

with open('datasets/users.json', 'w') as file:
    descriptions_list = descriptions['Description'].tolist()
    for description in descriptions_list:
        highschools, colleges, universities = create_template_education()
        profile = fake.profile()

        birthdate = validate_birthdate(profile['birthdate'])
        profile['birthdate'] = birthdate.isoformat()
        profile.pop('residence', None)
        profile.pop('ssn', None)
        profile.pop('current_location', None)
        profile['username'] = profile['name'].replace(" ", "").lower()
        profile['name'] = { 'first_name': profile['name'].split(' ')[1], 'last_name': profile['name'].split(' ')[0], 'full_name': profile['name'] }
        profile['address'] = profile['address'].replace("\n", ", ")
        profile['job'] = profile['job'].title()
        profile['education'] = dict()
        profile['education']['highschool'], profile['education']['college'] = get_age_based_random_education(birthdate, highschools, colleges, universities)
        profile['status'] = f'Feeling {get_random_emotion().lower()}'
        profile['hobbies'] = get_random_hobbies()
        # profile['follower_count'] = get_random_follower_count()
        # profile['post_count'] = get_random_post_count(profile['follower_count']['count'])
        profile['phone_number'] = fake.phone_number()
        profile['relationship_status'] = get_random_relationship_status(birthdate)
        profile['description'] = description

        json.dump(profile, file, indent=None)
        file.write('\n')

