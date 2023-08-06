# django-entries

## Overview

Basic create-read-update-delete (CRUD) functionality for an `Entry` model.

The base [template](./entries/templates/base.html) makes use of light css and javascript:

1. `starter.css` [stylesheet](./entries/static/css/starter.css)
2. `pylon` 0.1.1 for `<hstack>` and `<vstack>` layouts
3. `htmx` 1.6.1 for html-over-the-wire functionality, e.g. [infinite scrolling](./entries/docs/infinity_scroll.md)
4. `hyperscript` 0.9 for client-side reactivity
5. `simplemde` a simple markdown editor

## Quickstart

Install in your virtual environment:

```zsh
.venv> pip3 install django-entries # poetry add django-entries
```

Include package in main project settings file:

```python
# in project_folder/settings.py
INSTALLED_APPS = [..., "django_entries"]  # this is the new django-entries folder

# in project_folder/urls.py
from django.views.generic import TemplateView
from django.urls import path, include  # new

urlpatterns = [
    ...,
    path("entry/", include("django_entries.urls")),  # new
    path(
        "", TemplateView.as_view(template_name="home.html")
    ),  # (optional: if fresh project install)
]
```

Add to database:

```zsh
.venv> python manage.py migrate # adds the `Entry` model to the database.
.venv> python manage.py createsuperuser # (optional: if fresh project install)
```

Login to add:

```zsh
.venv> `python manage.py runserver`
# Visit http://127.0.0.1:8000/entry/entries/list
# Assumes _entry_ as folder in config/urls.py
# The `Add entry` button is only visible to logged in users.
# Can login via admin using the superuser account http://127.0.0.1:8000/admin/
# Visit the list page again at http://127.0.0.1:8000/entry/entries/list to see the `Add entry` button.
```

## Test

```zsh
.venv> pytest
```
