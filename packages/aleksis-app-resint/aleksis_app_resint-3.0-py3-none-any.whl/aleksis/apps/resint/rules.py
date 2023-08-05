from django.contrib.auth.models import User
from django.http import HttpRequest

from rules import add_perm, predicate

from aleksis.apps.resint.models import Poster, PosterGroup
from aleksis.core.util.predicates import (
    check_object_permission,
    has_any_object,
    has_global_perm,
    has_object_perm,
    has_person,
)


def has_poster_group_object_perm(perm: str):
    name = f"has_poster_group_object_perm:{perm}"

    @predicate(name)
    def fn(user: User, obj: Poster) -> bool:
        return check_object_permission(user, perm, obj.group, checker_obj=obj)

    return fn


def permission_validator(request: HttpRequest, perm: str, obj) -> bool:
    """Check whether the request user has a permission."""
    if request.user:
        return request.user.has_perm(perm, obj)
    return False


@predicate
def is_public_poster_group(user: User, obj: PosterGroup):
    return obj.public


@predicate
def show_poster_group_in_menu(user: User, obj: PosterGroup):
    return obj.show_in_menu


# View poster group list
view_poster_groups_predicate = has_person & (
    has_global_perm("resint.view_postergroup")
    | has_any_object("resint.view_postergroup", PosterGroup)
)
add_perm("resint.view_postergroups_rule", view_poster_groups_predicate)

# Add poster group
add_poster_group_predicate = view_poster_groups_predicate & has_global_perm(
    "resint.add_postergroup"
)
add_perm("resint.add_postergroup_rule", add_poster_group_predicate)

# Edit poster group
edit_poster_group_predicate = view_poster_groups_predicate & (
    has_global_perm("resint.change_postergroup") | has_object_perm("resint.change_postergroup")
)
add_perm("resint.edit_postergroup_rule", edit_poster_group_predicate)

# Delete poster group
delete_poster_group_predicate = view_poster_groups_predicate & (
    has_global_perm("resint.delete_postergroup") | has_object_perm("resint.delete_postergroup")
)
add_perm("resint.delete_postergroup_rule", delete_poster_group_predicate)

view_posters_predicate = has_person & (
    has_global_perm("resint.view_poster")
    | has_any_object("resint.view_poster", Poster)
    | has_any_object("resint.view_poster_of_group", PosterGroup)
)
add_perm("resint.view_posters_rule", view_posters_predicate)

# Upload poster
upload_poster_predicate = view_posters_predicate & (
    has_global_perm("resint.add_poster")
    | has_any_object("resint.upload_poster_to_group", PosterGroup)
)
add_perm("resint.upload_poster_rule", upload_poster_predicate)

# Edit poster
edit_poster_predicate = view_posters_predicate & (
    has_global_perm("resint.change_poster")
    | has_object_perm("resint.change_poster")
    | has_poster_group_object_perm("resint.change_poster_of_group")
)
add_perm("resint.edit_poster_rule", edit_poster_predicate)

# Delete poster
delete_poster_predicate = view_posters_predicate & (
    has_global_perm("resint.delete_poster")
    | has_object_perm("resint.delete_poster")
    | has_poster_group_object_perm("resint.delete_poster_of_group")
)
add_perm("resint.delete_poster_rule", delete_poster_predicate)

# View poster PDF file
view_poster_pdf_predicate = is_public_poster_group | (
    has_person
    & (has_global_perm("resint.view_postergroup") | has_global_perm("resint.view_poster"))
)
add_perm("resint.view_poster_pdf", view_poster_pdf_predicate)

# View poster PDF file in menu
view_poster_pdf_menu_predicate = has_person & (
    has_global_perm("resint.view_postergroup") | has_global_perm("resint.view_poster")
)
add_perm("resint.view_poster_pdf_menu", view_poster_pdf_menu_predicate)

# Show the poster manage menu
view_poster_menu_predicate = view_posters_predicate | view_poster_groups_predicate
add_perm("resint.view_poster_menu", view_poster_menu_predicate)


# View live document list
view_live_documents_predicate = has_person & has_global_perm("resint.view_livedocument")
add_perm("resint.view_livedocuments_rule", view_live_documents_predicate)

# View live document
view_live_document_predicate = has_person & (
    has_global_perm("resint.view_livedocument") | has_object_perm("resint.view_livedocument")
)
add_perm("resint.view_livedocument_rule", view_live_document_predicate)

# Add live document
add_live_document_predicate = view_live_documents_predicate & has_global_perm(
    "resint.add_livedocument"
)
add_perm("resint.add_livedocument_rule", add_live_document_predicate)

# Edit live document
edit_live_document_predicate = view_live_documents_predicate & has_global_perm(
    "resint.change_livedocument"
)
add_perm("resint.edit_livedocument_rule", edit_live_document_predicate)

# Delete live document
delete_live_document_predicate = view_live_documents_predicate & has_global_perm(
    "resint.delete_livedocument"
)
add_perm("resint.delete_livedocument_rule", delete_live_document_predicate)


# View menu
view_menu_predicate = (
    view_posters_predicate | view_poster_groups_predicate | view_live_documents_predicate
)
add_perm("resint.view_menu_rule", view_menu_predicate)
