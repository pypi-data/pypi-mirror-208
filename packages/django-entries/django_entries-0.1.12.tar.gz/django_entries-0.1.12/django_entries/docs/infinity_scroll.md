# Infinity Scroll with Django and HTMX

## Concept

Through django's [pagination](https://docs.djangoproject.com/en/4.0/topics/pagination/#using-paginator-in-a-view-function), a view can divide a queryset into different pages.

The first page holds a fixed number of model instances to be displayed.

When the last item in page one is `revealed` in the browser's DOM by scrolling, [htmx](https://htmx.org/examples/infinite-scroll/) can send a GET request to the original view, pulling page two.

Rinse and repeat until the view finds no subsequent page number.

## Requisites

### Load library

Load htmx in the `base` template so that it becomes accessible to subsequent calls:

```jinja
    <body>
        {% block body %}
            ...
            {% block base_js %}
                <script src="https://unpkg.com/htmx.org@1.6.1"></script>
                <script>document.body.addEventListener("htmx:configRequest", (e) => {e.detail.headers["X-CSRFToken"] = "{{ csrf_token }}";});</script>
            {% endblock base_js %}
        {% endblock body %}
    </body>
```

### Set common context

Declare a context that will be used in two views:

```python
# entries/views.py
def set_context(request: HttpRequest, loader: str) -> TemplateResponse:
    qs = Entry.objects.all()
    paginator = Paginator(qs, MAX_ITEMS_PER_PAGE)
    page_number = request.GET.get("next", 1)  # get next from url, else page 1
    page_obj = paginator.get_page(page_number)
    context = {"page_obj": page_obj, "template_for_item": ITEM_IN_PAGE}

    next_num = None
    if page_obj.has_next:
        try:
            next_num = page_obj.next_page_number()
        except EmptyPage:
            next_num = None
    if next_num:  # adds next page to url for infinity scrolling
        base_route = reverse("entries:scroll_entries")
        context["next_page_url"] = f"{base_route}?next={next_num}"
    return TemplateResponse(request, loader, context)
```

### Set the views

#### View 1: Initial template to load the first page

```python
# entries/views.py
def list_entries(request: HttpRequest) -> TemplateResponse:
    return set_context(request, FIRST_PAGE)
```

#### View 2: Scrolling template to load subsequent pages

```python
# entries/views.py
def scroll_entries(request: HttpRequest) -> TemplateResponse:
    return set_context(request, NEXT_PAGE)
```

### Add urls to the views

Add the two views above to the urlpatterns

```python
# entries/urls.py
urlpatterns = [
    path(
        "entries/scroll", scroll_entries, name="scroll_entries"
    ),  # note the reverse function declared in the context above
    path("entries/list", list_entries, name="list_entries"),
]
```

### Configure templates

#### Template 1: the 'first'

In the _first_ page we'll add an include to the _scroll_ page.

```jinja
<!-- templates/entries/entry_list.html -->
<main>{% include './entry_next.html' %}</main> <!-- This calls the template of the scroll page -->
```

#### Template 2: the 'scroll'

In the _scroll_ page we'll add an include to the _item_ page as well as the `htmx` trigger to add more pages, if possible.

```jinja
<!-- templates/entries/entry_next.html -->
{% for page_item in page_obj %}
    {% if forloop.last and next_page_url %}
        <div hx-get="{{next_page_url}}" hx-trigger="revealed" hx-swap="afterend"></div>
    {% endif %}
    {% include template_for_item with entry=page_item %}
{% endfor %}
```

#### Template 3: the 'item'

In the _item_ page, we can customize how each record in each page will look like:

```jinja
<!-- templates/entries/entry_item.html -->
<section>
    <a href="{% url 'entries:view_entry' entry.slug %}" style="text-decoration: none">{{ entry.title }}</a>
    <span style="font-style: italic;">{{entry.excerpt}}</span>
</section>
```
