from django.contrib import admin

# Register your models here.
from devpro.core.models import Author, Book

admin.site.register([Author, Book])
