from django.contrib import admin

from .models import Poster, PosterGroup

admin.site.register(PosterGroup)
admin.site.register(Poster)
