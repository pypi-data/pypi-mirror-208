from django import forms
from markdownify import markdownify as md

from .models import Entry


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ("title", "excerpt", "content")

    def clean_content(self):
        """Removed bad tags, e.g. <script>"""
        content = self.cleaned_data["content"]
        cleaned = md(content, strip=["script"])
        return cleaned
