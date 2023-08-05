from django import forms
from django.http import HttpRequest

from guardian.shortcuts import get_objects_for_user
from material import Layout, Row

from .models import Poster, PosterGroup


class PosterGroupForm(forms.ModelForm):
    """Form to manage poster groups."""

    layout = Layout(
        Row("slug"),
        Row("name"),
        Row("publishing_day", "publishing_time"),
        Row("default_pdf"),
        Row("show_in_menu", "public"),
    )

    class Meta:
        model = PosterGroup
        fields = [
            "slug",
            "name",
            "publishing_day",
            "publishing_time",
            "default_pdf",
            "show_in_menu",
            "public",
        ]


class PosterUploadForm(forms.ModelForm):
    """Form for uploading new posters."""

    class Meta:
        model = Poster
        fields = ["group", "week", "year", "pdf"]

    def __init__(self, request: HttpRequest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        qs = PosterGroup.objects.all()
        if not request.user.has_perm("resint.view_postergroup"):
            qs = get_objects_for_user(request.user, "resint.upload_poster_to_group", qs)
        self.fields["group"].queryset = qs
