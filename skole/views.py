from collections import defaultdict

from django.contrib import messages
from django.db.models import CharField, Count, F, Prefetch, Sum, Value
from django.db.models.functions import Concat
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView

from .forms import (
    DepartmentForm,
    EmploymentCategoryForm,
    LessonForm,
    SchoolClassForm,
    SchoolFeeForm,
    SchoolForm,
    StaffForm,
    StudentForm,
    TeamForm,
)
from .models import (
    Department,
    EmploymentCategory,
    Lesson,
    School,
    SchoolClass,
    SchoolFee,
    Staff,
    Student,
    Team,
)


def schoolclass_detail(request, class_id):
    schoolclass = SchoolClass.objects.annotate(
        total_school_fee=Sum("students__school_fee__amount")
    ).get(pk=class_id)
    lessons = (
        Lesson.objects.filter(schoolclass=schoolclass)
        .annotate(
            teacher_name=Concat("teachers__name", Value(""), output_field=CharField()),
            total_lessons=Count("id"),
            employment_category=F("teachers__employment_category__name"),
            price_per_lesson=F("teachers__employment_category__price_pr_lesson"),
        )
        .values(
            "teacher_name",
            "employment_category",
            "subject",
            "classroom",
            "price_per_lesson",
        )
        .annotate(total_lessons_per_teacher=Count("id"))
        .order_by("teacher_name", "subject")
    )

    # Calculate total hours per employment category
    total_hours = defaultdict(int)
    for lesson in lessons:
        total_hours[lesson["employment_category"]] += lesson[
            "total_lessons_per_teacher"
        ]

    # Convert total_hours to a list of tuples
    total_hours_list = [(category, hours) for category, hours in total_hours.items()]

    # Calculate total sum
    total_sum = sum(total_hours.values())

    # Calculate total number of lessons in the class
    total_lessons_in_class = Lesson.objects.filter(schoolclass=schoolclass).count()

    # Beregn totalprisen for hver lektion baseret på prisen per lektion og antallet af lektioner
    for lesson in lessons:
        lesson["total_price"] = (
            lesson["total_lessons_per_teacher"] * lesson["price_per_lesson"]
        )

    # Beregn den samlede pris for klassen ved at summere prisen for hver lektion
    total_price_for_class = sum(lesson["total_price"] for lesson in lessons)

    # Overskud? og forbrugs%
    surplus = 0
    percentage_used = 0
    if schoolclass.total_school_fee and total_price_for_class:
        if schoolclass.total_school_fee > 0 and total_price_for_class > 0:
            surplus = int(schoolclass.total_school_fee - total_price_for_class)
            percentage_used = round(
                (total_price_for_class / schoolclass.total_school_fee) * 100, 1
            )

    return render(
        request,
        "skole/schoolclass_detail.html",
        {
            "schoolclass": schoolclass,
            "lessons": lessons,
            "total_hours": total_hours_list,
            "total_sum": total_sum,
            "total_lessons_in_class": total_lessons_in_class,
            "total_price_for_class": total_price_for_class,
            "surplus": surplus,
            "percentage_used": percentage_used,
        },
    )


def schoolclass_edit(request, class_id):
    schoolclass = get_object_or_404(SchoolClass, pk=class_id)

    if request.method == "POST":
        form = SchoolClassForm(request.POST, instance=schoolclass)
        if form.is_valid():
            form.save()
            messages.success(request, "Klassen blev opdateret!")
            return redirect(
                "schoolclass_detail", class_id=schoolclass.pk
            )  # Tilpas til detail-viewets URL
    else:
        form = SchoolClassForm(instance=schoolclass)

    return render(
        request,
        "skole/schoolclass_edit.html",
        {
            "form": form,
            "schoolclass": schoolclass,
        },
    )


def homepage(request):
    schoolclasses = SchoolClass.objects.all()
    teams = Team.objects.all()
    departments = Department.objects.all()

    return render(
        request,
        "skole/homepage.html",
        {"schoolclasses": schoolclasses, "teams": teams, "departments": departments},
    )


def team_detail(request, team_id):
    team = get_object_or_404(Team, pk=team_id)

    # Prefetch students, school fees, lessons, and teachers with employment categories
    schoolclasses = (
        SchoolClass.objects.filter(team=team)
        .prefetch_related(
            Prefetch(
                "students",
                queryset=Student.objects.select_related("school_fee"),
            ),
            Prefetch(
                "lessons",
                queryset=Lesson.objects.select_related("schoolclass").prefetch_related(
                    Prefetch(
                        "teachers",
                        queryset=Staff.objects.select_related("employment_category"),
                    )
                ),
            ),
        )
        .select_related("team")
    )

    employment_categories = list(EmploymentCategory.objects.all())

    summary_data = []
    totals = {
        "num_students": 0,
        "school_fee": 0,
        "num_lessons": 0,
    }
    total_price_for_team = 0
    total_hours_by_category = defaultdict(int)
    total_school_fee_for_team = 0

    lessons_data = []  # Collect all lessons for efficient aggregation

    for schoolclass in schoolclasses:
        # Collect all lessons data for aggregation
        for lesson in schoolclass.lessons.all():
            lessons_data.append(
                {
                    "teacher_name": (
                        lesson.teachers.first().name if lesson.teachers.exists() else ""
                    ),
                    "employment_category": (
                        lesson.teachers.first().employment_category.name
                        if lesson.teachers.exists()
                        else ""
                    ),
                    "price_per_lesson": (
                        lesson.teachers.first().employment_category.price_pr_lesson
                        if lesson.teachers.exists()
                        else 0
                    ),
                    "schoolclass_id": lesson.schoolclass_id,
                }
            )

        # Calculate total school fee for this class
        students = schoolclass.students.all()
        total_school_fee_for_class = sum(
            student.school_fee.amount for student in students if student.school_fee
        )
        total_school_fee_for_team += total_school_fee_for_class

        # Calculate number of students in the class
        num_students = len(students)
        totals["num_students"] += num_students

        # Calculate total school_fee for the class
        sum_school_fee = sum(
            student.school_fee.amount for student in students if student.school_fee
        )
        totals["school_fee"] += sum_school_fee

        # Number of lessons is already prefetched
        num_lessons = schoolclass.lessons.count()
        totals["num_lessons"] += num_lessons

        # Add summary data for this class
        summary_data.append(
            {
                "class_name": schoolclass.name,
                "num_students": num_students,
                "sum_school_fee": sum_school_fee,
                "total_price_for_class": 0,  # Calculate later
                "num_lessons": num_lessons,
                "employment_categories": employment_categories,
            }
        )

    # Aggregate lessons data efficiently
    total_price_for_team = sum(lesson["price_per_lesson"] for lesson in lessons_data)

    # Convert total_hours_by_category to a list of tuples
    total_hours_list = [
        (category, hours) for category, hours in total_hours_by_category.items()
    ]

    # Calculate total surplus for the team
    surplus = total_school_fee_for_team - total_price_for_team

    # Calculate percentage of school fee used
    percentage_used = (
        round((total_price_for_team / total_school_fee_for_team) * 100, 1)
        if total_school_fee_for_team > 0
        else 0
    )

    # Formatting of numbers as DKK
    total_school_fee_for_team_formatted = f"{total_school_fee_for_team:.0f} DKK"
    total_price_for_team_formatted = f"{total_price_for_team:.0f} DKK"
    surplus_formatted = f"{surplus:.0f} DKK"

    return render(
        request,
        "skole/team_detail.html",
        {
            "team": team,
            "summary_data": summary_data,
            "totals": totals,
            "total_hours": total_hours_list,
            "total_price_for_team": total_price_for_team,
            "total_school_fee_for_team": total_school_fee_for_team,
            "total_school_fee_for_team_formatted": total_school_fee_for_team_formatted,
            "total_price_for_team_formatted": total_price_for_team_formatted,
            "surplus_formatted": surplus_formatted,
            "surplus": surplus,
            "percentage_used": percentage_used,
        },
    )


def team_edit(request, team_id):
    team = get_object_or_404(Team, pk=team_id)

    if request.method == "POST":
        form = TeamForm(request.POST, instance=team)
        if form.is_valid():
            form.save()
            return redirect("team_detail", team_id=team.pk)
    else:
        form = TeamForm(instance=team)

    return render(
        request,
        "skole/team_edit.html",
        {
            "form": form,
            "team": team,
        },
    )


def department_detail(request, department_id):
    # Prefetch related teams and their related objects
    department = Department.objects.prefetch_related(
        Prefetch(
            "teams",
            queryset=Team.objects.prefetch_related(
                Prefetch(
                    "schoolclasses",
                    queryset=SchoolClass.objects.prefetch_related("students"),
                )
            ),
        )
    ).get(pk=department_id)

    return render(
        request,
        "skole/department_detail.html",
        {
            "department": department,
            "teams": department.teams.all(),  # Already prefetched
        },
    )


from django.shortcuts import get_object_or_404, redirect, render

from .forms import DepartmentForm
from .models import Department, Team


def department_edit(request, department_id):
    department = get_object_or_404(Department, pk=department_id)
    teams = department.teams.prefetch_related("schoolclasses")

    if request.method == "POST":
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            return redirect("department_detail", department_id=department.pk)
    else:
        form = DepartmentForm(instance=department)

    return render(
        request,
        "skole/department_edit.html",
        {
            "form": form,
            "department": department,
            "teams": teams,
        },
    )


from django.shortcuts import get_object_or_404, redirect, render

from .forms import StudentForm
from .models import Student


def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, "skole/student_detail.html", {"student": student})


def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect("schoolclass_detail", class_id=student.schoolclass.pk)
    else:
        form = StudentForm(instance=student)

    return render(
        request,
        "skole/student_edit.html",
        {
            "form": form,
            "student": student,
        },
    )


def organization_overview(request):
    all_departments = Department.objects.prefetch_related("teams__schoolclasses").all()
    return render(
        request,
        "skole/homepage.html",
        {
            "all_departments": all_departments,
        },
    )


class BaseEditView(UpdateView):
    template_name = "skole/edit_form.html"
    success_url = reverse_lazy("homepage")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Tilføj verbose_name til konteksten for at gøre det lettere at tilpasse skabeloner
        context["verbose_name"] = self.model._meta.verbose_name
        context["verbose_name_plural"] = self.model._meta.verbose_name_plural
        return context


class BaseCreateView(CreateView):
    template_name = "skole/create_form.html"
    success_url = reverse_lazy("homepage")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["verbose_name"] = self.model._meta.verbose_name
        return context


class SchoolCreateView(BaseCreateView):
    model = School
    form_class = SchoolForm


class DepartmentCreateView(BaseCreateView):
    model = Department
    form_class = DepartmentForm


class TeamCreateView(BaseCreateView):
    model = Team
    form_class = TeamForm


class EmploymentCategoryCreateView(BaseCreateView):
    model = EmploymentCategory
    form_class = EmploymentCategoryForm


class StaffCreateView(BaseCreateView):
    model = Staff
    form_class = StaffForm


class LessonCreateView(BaseCreateView):
    model = Lesson
    form_class = LessonForm


class SchoolFeeCreateView(BaseCreateView):
    model = SchoolFee
    form_class = SchoolFeeForm


class StudentCreateView(BaseCreateView):
    model = Student
    form_class = StudentForm


from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, UpdateView

from .forms import (
    DepartmentForm,
    EmploymentCategoryForm,
    LessonForm,
    SchoolFeeForm,
    SchoolForm,
    StaffForm,
    StudentForm,
    TeamForm,
)
from .models import (
    Department,
    EmploymentCategory,
    Lesson,
    School,
    SchoolClass,
    SchoolFee,
    Staff,
    Student,
    Team,
)


# School
class SchoolListView(ListView):
    model = School
    template_name = "skole/school_list.html"
    context_object_name = "schools"


class SchoolDetailView(DetailView):
    model = School
    template_name = "skole/school_detail.html"
    context_object_name = "school"


class SchoolEditView(BaseEditView):
    model = School
    form_class = SchoolForm
    template_name = "skole/edit_form.html"
    success_url = reverse_lazy("school_list")


# Department


class DepartmentDetailView(DetailView):
    model = Department
    template_name = "skole/department_detail.html"
    context_object_name = "department"


class DepartmentEditView(BaseEditView):
    model = Department
    form_class = DepartmentForm
    template_name = "skole/edit_form.html"
    success_url = reverse_lazy("department_list")


class TeamListView(ListView):
    model = Team
    template_name = "skole/team_list.html"
    context_object_name = "teams"


class TeamDetailView(DetailView):
    model = Team
    template_name = "skole/team_detail.html"
    context_object_name = "team"


class TeamEditView(BaseEditView):
    model = Team
    form_class = TeamForm
    template_name = "skole/edit_form.html"
    success_url = reverse_lazy("team_list")


class SchoolClassListView(ListView):
    model = SchoolClass
    template_name = "skole/schoolclass_list.html"
    context_object_name = "schoolclasses"


class SchoolClassDetailView(DetailView):
    model = SchoolClass
    template_name = "skole/schoolclass_detail.html"
    context_object_name = "schoolclass"


class SchoolClassCreateView(BaseCreateView):
    model = SchoolClass
    form_class = SchoolClassForm


class StudentEditView(BaseEditView):
    model = Student
    form_class = StudentForm
    template_name = "skole/edit_form.html"
    success_url = reverse_lazy("student_list")


# Department Views
class DepartmentListView(ListView):
    model = Department
    template_name = "skole/department_list.html"
    context_object_name = "departments"


# Student Views
class StudentListView(ListView):
    model = Student
    template_name = "skole/student_list.html"
    context_object_name = "students"


class StudentDetailView(DetailView):
    model = Student
    template_name = "skole/student_detail.html"
    context_object_name = "student"


# Lesson Views
class LessonListView(ListView):
    model = Lesson
    template_name = "skole/lesson_list.html"
    context_object_name = "lessons"


class LessonDetailView(DetailView):
    model = Lesson
    template_name = "skole/lesson_detail.html"
    context_object_name = "lesson"


class LessonEditView(BaseEditView):
    model = Lesson
    form_class = LessonForm
    template_name = "skole/edit_form.html"
    success_url = reverse_lazy("lesson_list")


# EmploymentCategory Views
class EmploymentCategoryListView(ListView):
    model = EmploymentCategory
    template_name = "skole/employmentcategory_list.html"
    context_object_name = "employmentcategories"


class EmploymentCategoryDetailView(DetailView):
    model = EmploymentCategory
    template_name = "skole/employmentcategory_detail.html"
    context_object_name = "employmentcategory"


class EmploymentCategoryEditView(BaseEditView):
    model = EmploymentCategory
    form_class = EmploymentCategoryForm
    template_name = "skole/edit_form.html"
    success_url = reverse_lazy("employmentcategory_list")


# SchoolFee Views
class SchoolFeeListView(ListView):
    model = SchoolFee
    template_name = "skole/schoolfee_list.html"
    context_object_name = "schoolfees"


class SchoolFeeDetailView(DetailView):
    model = SchoolFee
    template_name = "skole/schoolfee_detail.html"
    context_object_name = "schoolfee"


class SchoolFeeEditView(BaseEditView):
    model = SchoolFee
    form_class = SchoolFeeForm
    template_name = "skole/edit_form.html"
    success_url = reverse_lazy("schoolfee_list")


# Staff Views
class StaffListView(ListView):
    model = Staff
    template_name = "skole/staff_list.html"
    context_object_name = "staff"


class StaffDetailView(DetailView):
    model = Staff
    template_name = "skole/staff_detail.html"
    context_object_name = "staffmember"


class StaffEditView(BaseEditView):
    model = Staff
    form_class = StaffForm
    template_name = "skole/edit_form.html"
    success_url = reverse_lazy("staff_list")
