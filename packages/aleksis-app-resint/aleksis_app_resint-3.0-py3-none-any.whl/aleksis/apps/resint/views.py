from typing import Any, Dict, List, Type

from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet
from django.forms import BaseModelForm, modelform_factory
from django.http import FileResponse, Http404, HttpRequest
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import ListView

from django_tables2 import SingleTableView
from guardian.shortcuts import get_objects_for_user
from oauth2_provider.views.mixins import ScopedResourceMixin
from reversion.views import RevisionMixin
from rules.contrib.views import PermissionRequiredMixin

from aleksis.core.mixins import AdvancedCreateView, AdvancedDeleteView, AdvancedEditView
from aleksis.core.util.auth_helpers import ClientProtectedResourceMixin

from .forms import PosterGroupForm, PosterUploadForm
from .models import LiveDocument, Poster, PosterGroup
from .tables import LiveDocumentTable


class PosterGroupListView(PermissionRequiredMixin, ListView):
    """Show a list of all poster groups."""

    template_name = "resint/group/list.html"
    model = PosterGroup
    permission_required = "resint.view_postergroups_rule"

    def get_queryset(self) -> QuerySet:
        qs = super().get_queryset()
        if self.request.user.has_perm("resint.view_postergroup"):
            return qs
        return get_objects_for_user(self.request.user, "resint.view_postergroup", qs)


class PosterGroupCreateView(PermissionRequiredMixin, AdvancedCreateView):
    """Create a new poster group."""

    model = PosterGroup
    success_url = reverse_lazy("poster_group_list")
    template_name = "resint/group/create.html"
    success_message = _("The poster group has been saved.")
    form_class = PosterGroupForm
    permission_required = "resint.create_postergroup_rule"


class PosterGroupEditView(PermissionRequiredMixin, AdvancedEditView):
    """Edit an existing poster group."""

    model = PosterGroup
    success_url = reverse_lazy("poster_group_list")
    template_name = "resint/group/edit.html"
    success_message = _("The poster group has been saved.")
    form_class = PosterGroupForm
    permission_required = "resint.edit_postergroup_rule"


class PosterGroupDeleteView(PermissionRequiredMixin, AdvancedDeleteView):
    """Delete a poster group."""

    model = PosterGroup
    success_url = reverse_lazy("poster_group_list")
    success_message = _("The poster group has been deleted.")
    template_name = "core/pages/delete.html"
    permission_required = "resint.delete_postergroup_rule"


class PosterListView(PermissionRequiredMixin, ListView):
    """Show a list of all uploaded posters."""

    template_name = "resint/poster/list.html"
    model = Poster
    permission_required = "resint.view_posters_rule"

    def get_queryset(self) -> QuerySet:
        qs = Poster.objects.all().order_by("-year", "-week")

        if self.request.user.has_perm("resint.view_poster"):
            return qs

        allowed_groups = get_objects_for_user(
            self.request.user, "resint.view_poster_of_group", PosterGroup
        )
        posters = get_objects_for_user(self.request.user, "resint.view_poster", qs)
        return qs.filter(group__in=allowed_groups) | posters

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["poster_groups"] = PosterGroup.objects.all().order_by("name")
        return context


class RequestMixin:
    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


class PosterUploadView(RequestMixin, PermissionRequiredMixin, AdvancedCreateView):
    """Upload a new poster."""

    model = Poster
    success_url = reverse_lazy("poster_index")
    template_name = "resint/poster/upload.html"
    success_message = _("The poster has been uploaded.")
    form_class = PosterUploadForm
    permission_required = "resint.upload_poster_rule"


class PosterEditView(RequestMixin, PermissionRequiredMixin, AdvancedEditView):
    """Edit an uploaded poster."""

    model = Poster
    success_url = reverse_lazy("poster_index")
    template_name = "resint/poster/edit.html"
    success_message = _("The poster has been changed.")
    form_class = PosterUploadForm
    permission_required = "resint.edit_poster_rule"


class PosterDeleteView(PermissionRequiredMixin, AdvancedDeleteView):
    """Delete an uploaded poster."""

    model = Poster
    success_url = reverse_lazy("poster_index")
    success_message = _("The poster has been deleted.")
    template_name = "core/pages/delete.html"
    permission_required = "resint.delete_poster_rule"


class PosterCurrentView(PermissionRequiredMixin, SingleObjectMixin, View):
    """Show the poster which is currently valid."""

    model = PosterGroup
    permission_required = "resint.view_poster_pdf"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> FileResponse:
        group = self.get_object()
        current_poster = group.current_poster
        file = current_poster.pdf if current_poster else group.default_pdf
        return FileResponse(file, content_type="application/pdf")


class LiveDocumentListView(PermissionRequiredMixin, SingleTableView):
    """Table of all live documents."""

    model = LiveDocument
    table_class = LiveDocumentTable
    permission_required = "resint.view_livedocuments_rule"
    template_name = "resint/live_document/list.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["document_types"] = [
            (ContentType.objects.get_for_model(m, False), m) for m in LiveDocument.__subclasses__()
        ]
        return context


@method_decorator(never_cache, name="dispatch")
class LiveDocumentCreateView(PermissionRequiredMixin, AdvancedCreateView):
    """Create view for live documents."""

    def get_model(self, request, *args, **kwargs):
        app_label = kwargs.get("app")
        model = kwargs.get("model")
        ct = get_object_or_404(ContentType, app_label=app_label, model=model)
        return ct.model_class()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["model"] = self.model
        return context

    def get(self, request, *args, **kwargs):
        self.model = self.get_model(request, *args, **kwargs)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.model = self.get_model(request, *args, **kwargs)
        return super().post(request, *args, **kwargs)

    fields = "__all__"
    model = LiveDocument
    permission_required = "resint.add_livedocument_rule"
    template_name = "resint/live_document/create.html"
    success_url = reverse_lazy("live_documents")
    success_message = _("The live document has been created.")


@method_decorator(never_cache, name="dispatch")
class LiveDocumentEditView(PermissionRequiredMixin, AdvancedEditView):
    """Edit view for live documents."""

    def get_form_class(self) -> Type[BaseModelForm]:
        return modelform_factory(self.object.__class__, fields=self.fields)

    model = LiveDocument
    fields = "__all__"
    permission_required = "resint.edit_livedocument_rule"
    template_name = "resint/live_document/edit.html"
    success_url = reverse_lazy("live_documents")
    success_message = _("The live document has been saved.")


@method_decorator(never_cache, name="dispatch")
class LiveDocumentDeleteView(PermissionRequiredMixin, RevisionMixin, AdvancedDeleteView):
    """Delete view for live documents."""

    model = LiveDocument
    permission_required = "resint.delete_livedocument_rule"
    template_name = "core/pages/delete.html"
    success_url = reverse_lazy("live_documents")
    success_message = _("The live document has been deleted.")


class LiveDocumentShowBaseView(SingleObjectMixin, View):
    """Base view for showing live documents."""

    model = LiveDocument

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> FileResponse:
        live_document = self.get_object()
        file = live_document.get_current_file()
        if not file:
            raise Http404
        return FileResponse(file, content_type="application/pdf")


class LiveDocumentShowView(PermissionRequiredMixin, LiveDocumentShowBaseView):
    """Show the current version of the live document."""

    permission_required = "resint.view_livedocument_rule"


class LiveDocumentShowAPIView(
    ScopedResourceMixin, ClientProtectedResourceMixin, LiveDocumentShowBaseView
):
    """Show the current version of the live document in API."""

    def get_scopes(self, *args, **kwargs) -> List[str]:
        """Return the scope needed to access the PDF file."""
        return [self.get_object().scope]
