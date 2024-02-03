from django.db import models

# Create your models here.

class SparqlResult:
    subject = models.CharField(max_length=1024)
    predicate = models.CharField(max_length=1024)
    object = models.CharField(max_length=1024)