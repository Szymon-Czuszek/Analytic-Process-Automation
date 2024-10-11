from django.contrib import admin
from .models import DataSet

# Register your models here.

# Create a list or tuple of models
models = [DataSet]

# Register all models in the list
admin.site.register(models)