# SoRe (Social Recommender)
# Table of Contents

- [About the Project](#about-the-project)
  * [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
  * [Running Tests](#running-tests)
  * [Run Locally](#run-locally)
- [Usage](#usage)
- [Team Members](#team-members)
- [Acknowledgements](#acknowledgements)

## About the Project
SoRe (Social Recommender) is a Web modular system able to recommend certain connections according to a built-in knowledge graph expressed in RDF and automatically built for a specific user, based on her/his social media profile(s) and by considering multiple similar features/properties: skills (excellent knowledge of certain areas like Web technologies + open hardware), geographic location (i.e. from Romania and Chile only), technical preferences (e.g., using free software), background info (demographics, education, occupation history, driving license, other competencies), hobbies (i.e. horror movies + classical music), aversions (e.g., communication by phone, sport, politics), acquaintance and so on. The system should be “smart” enough to improve recommendations based on various methods such as user feedback, reasoning, and/or machine learning. The recommended items will be available via a SPARQL endpoint.

<!-- TechStack -->
### Tech Stack
<a href="https://www.djangoproject.com">Django</a>
<a href="https://flask.palletsprojects.com/en/3.0.x/">Flask</a>
<a href="https://getbootstrap.com">Bootstrap</a>

## Getting Started
### Prerequisites
<a href="https://www.python.org">Python</a>

### Instalation
```bash
git clone https://github.com/Danie83/SoRe.git
```

```bash
pip install -r requirements.txt
```

### Running Tests
```bash
cd soreapp && ./manage.py test
```

### Running Locally
```bash
git clone https://github.com/Danie83/SoRe.git
```
```bash
pip install -r requirements.txt
```
```bash
cd soreapp && python manage.py runserver
```
```bash
cd soreapiapp && flask --app soreapi run
```

## Usage
```bash
http://localhost:8000
```
The application consists of 4 pages: user login/registration, user profile form, homepage and a history. The user login/registration page allows an existing user to login or if the user doesn't have an account, to register. The functionalities of the application are not available to users that are not logged in. The user profile form page is automatically displayed to newly registered users to add necessary data about themselves which is then used to recommend other user profiles. It also acts as a page for editing existing information about the user. The homepage is the most important because it provides the main functionalities of the application, here the user can rate recommended user profiles, it will also display recommended items based on the rating that was accorded. The history provides a log where the profiles rates by the user appear and can be adjusted if wanted.

## Team Members
* Filimon Danut-Dumitru
* Onofrei Tudor-Cristian

## Acknowledgements
<a href="https://www.djangoproject.com">Django</a>
<a href="https://flask.palletsprojects.com/en/3.0.x/">Flask</a>
<a href="https://getbootstrap.com">Bootstrap</a>
<a href="https://www.w3.org/TR/rdf-sparql-query/">SPARQL Query Language for RDF</a>
