from django.contrib import admin

from .models import School, Department, Team, SchoolClass, Student, Lesson, Staff, SchoolFee, EmploymentCategory

# Register your models here.

mods = [School, Department, Team, SchoolClass, Lesson, Staff, SchoolFee, EmploymentCategory, ]

for mod in mods:
    admin.site.register(mod)


class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'school_class', 'age')  # Tilføj 'age' til listen over felter, der vises
    readonly_fields = ('age',)  # Gør 'age' til et skrivebeskyttet felt i detaljevisningen

admin.site.register(Student, StudentAdmin)