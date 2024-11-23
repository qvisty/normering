# skole/forms.py
from django import forms

from .models import SchoolClass


class SchoolClassForm(forms.ModelForm):
    class Meta:
        model = SchoolClass
        fields = ["name", "team", "class_teachers", "class_group", "age_number"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "team": forms.Select(attrs={"class": "form-control"}),
            "class_teachers": forms.SelectMultiple(attrs={"class": "form-control"}),
            "class_group": forms.Select(attrs={"class": "form-control"}),
            "age_number": forms.NumberInput(attrs={"class": "form-control"}),
        }
        labels = {
            "name": "Klassens navn",
            "team": "Hold",
            "class_teachers": "Klasselærere",
            "class_group": "Klassetrin",
            "age_number": "Alder/Trin",
        }
