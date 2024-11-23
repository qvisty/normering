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


from django import forms
from .models import School

class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Indtast skolens navn'}),
        }
        labels = {
            'name': 'Skolens Navn',
        }


from .models import Department

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'school']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Indtast afdelingens navn'}),
            'school': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Afdelingens Navn',
            'school': 'Skole',
        }


from .models import Team

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'department']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Indtast teamnavn'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Teamnavn',
            'department': 'Afdeling',
        }


from .models import EmploymentCategory

class EmploymentCategoryForm(forms.ModelForm):
    class Meta:
        model = EmploymentCategory
        fields = ['name', 'type', 'price_pr_lesson']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Indtast kategoriens navn'}),
            'type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Indtast kategoriens type'}),
            'price_pr_lesson': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Kategoriens Navn',
            'type': 'Kategoriens Type',
            'price_pr_lesson': 'Pris pr. Lektion',
        }


from .models import Staff

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['name', 'employment_category', 'employment_grade']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Indtast medarbejderens navn'}),
            'employment_category': forms.Select(attrs={'class': 'form-control'}),
            'employment_grade': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Medarbejderens Navn',
            'employment_category': 'Ansættelseskategori',
            'employment_grade': 'Ansættelsesgrad (timer/uge)',
        }


from .models import Lesson

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['schoolclass', 'subject', 'classroom', 'teachers']
        widgets = {
            'schoolclass': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Indtast fag'}),
            'classroom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Indtast lokale'}),
            'teachers': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }
        labels = {
            'schoolclass': 'Klasse',
            'subject': 'Fag',
            'classroom': 'Lokale',
            'teachers': 'Lærere',
        }


from .models import SchoolFee

class SchoolFeeForm(forms.ModelForm):
    class Meta:
        model = SchoolFee
        fields = ['name', 'level', 'amount', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Indtast takstens navn'}),
            'level': forms.NumberInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Beskriv taksten'}),
        }
        labels = {
            'name': 'Takstnavn',
            'level': 'Takstniveau',
            'amount': 'Beløb',
            'description': 'Beskrivelse',
        }


from .models import Student

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'schoolclass', 'age_number', 'date_of_birth', 'school_fee']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Indtast elevens navn'}),
            'schoolclass': forms.Select(attrs={'class': 'form-control'}),
            'age_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'school_fee': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Elevens Navn',
            'schoolclass': 'Klasse',
            'age_number': 'Klassetrin',
            'date_of_birth': 'Fødselsdato',
            'school_fee': 'Takst',
        }
