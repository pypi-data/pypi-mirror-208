from django.urls import path

from .views import (
    add_entry,
    delete_entry,
    edit_entry,
    list_entries,
    scroll_entries,
    view_about,
    view_entry,
)

app_name = "entries"
urlpatterns = [
    path("entries/scroll", scroll_entries, name="scroll_entries"),
    path("entries/list", list_entries, name="list_entries"),
    path("create/add", add_entry, name="add_entry"),
    path("edit/<slug:slug>", edit_entry, name="edit_entry"),
    path("delete/<slug:slug>", delete_entry, name="delete_entry"),
    path("view/<slug:slug>", view_entry, name="view_entry"),
    path("about/", view_about, name="view_about"),
]
