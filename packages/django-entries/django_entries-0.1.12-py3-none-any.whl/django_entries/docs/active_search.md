# Active Search with Django and HTMX

## Concept

Through django's basic filter system in tandem with the the view for [Scrolling template to load subsequent pages](./infinity_scroll.md), can use htmx's [active search pattern](https://htmx.org/examples/active-search/)

## Display search form and result container

```jinja
<!-- search form -->
<input
    id="autocomplete-search"
    name="q" {% comment %} This is passed as a URL parameter on keyup trigger {% endcomment %}
    type="search"
    placeholder="Search"
    hx-get="{% url 'entries:scroll_entries' %}"
    hx-trigger="keyup changed delay:500ms"
    hx-target="#search-results"
>

...
<!-- result container -->
<section id="search-results">
    {% include 'entries/entry_next.html' with template_for_item='entries/entry_item.html' %}
</section>
```

## Use search form request's `q` to update result container

```python
# entries/views.py
def set_context(request: HttpRequest):
    ...
    url = reverse("entries:scroll_entries")  # base url for infinity scrolling
    query = request.GET.get("q", None)  # get query from url, else None
    qs = Entry.objects.all()
    if query:
        url = f"{url}?q={query}"
        qs = qs.filter(
            Q(title__icontains=query)
            | Q(excerpt__icontains=query)
            | Q(content__icontains=query)
        )
    ...
```
