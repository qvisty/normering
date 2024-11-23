from collections import defaultdict
from operator import itemgetter

from django.contrib import messages
from django.db.models import CharField, Count, F, Sum, Value
from django.db.models.functions import Concat
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.formats import localize

from .forms import SchoolClassForm
from .models import (
    Department,
    EmploymentCategory,
    Lesson,
    SchoolClass,
    SchoolFee,
    Staff,
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


from operator import itemgetter


def team_detail(request, team_id):
    team = Team.objects.get(pk=team_id)
    schoolclasses = SchoolClass.objects.filter(team=team)
    employment_categories = EmploymentCategory.objects.all()

    summary_data = []
    totals = {}
    totals["num_students"] = 0
    totals["school_fee"] = 0
    totals["school_fee_amount"] = 0
    totals["num_lessons"] = 0
    total_lessons_by_category = defaultdict(int)
    total_price_for_team = 0
    total_hours_by_category = defaultdict(int)
    total_school_fee_for_team = 0

    for schoolclass in schoolclasses:
        lessons = (
            Lesson.objects.filter(schoolclass=schoolclass)
            .annotate(
                teacher_name=Concat(
                    "teachers__name", Value(""), output_field=CharField()
                ),
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

        # Calculate total hours per employment category for this class
        total_hours = defaultdict(int)
        for lesson in lessons:
            total_hours[lesson["employment_category"]] += lesson[
                "total_lessons_per_teacher"
            ]

        # Add the hours for this class to the team's total
        for category, hours in total_hours.items():
            total_hours_by_category[category] += hours

        # Calculate total price for this class
        total_price_for_class = sum(
            lesson["total_lessons_per_teacher"] * lesson["price_per_lesson"]
            for lesson in lessons
        )
        total_price_for_team += total_price_for_class

        # Calculate total school fee for this class (sum of school fee for each student)
        total_school_fee_for_class = sum(
            student.school_fee.amount
            for student in schoolclass.students.all()
            if student.school_fee
        )
        total_school_fee_for_team += total_school_fee_for_class

        # Beregn antal elever i klassen
        num_students = schoolclass.students.count()
        totals["num_students"] += num_students

        # Beregn summen af school_fee for klassen
        sum_school_fee = sum(
            student.school_fee.amount
            for student in schoolclass.students.all()
            if student.school_fee
        )
        totals["school_fee"] += sum_school_fee

        # Beregn summen af school_fee_amount for klassen
        sum_school_fee_amount = (
            SchoolFee.objects.filter(student__schoolclass=schoolclass).aggregate(
                total_fee_amount=Sum("level")
            )["total_fee_amount"]
            or 0
        )
        totals["school_fee_amount"] += sum_school_fee_amount

        # Beregn antal lektioner i klassen
        num_lessons = schoolclass.lessons.count()
        totals["num_lessons"] += num_lessons

        # Hent det samlede antal lektioner pr. personalekategori for denne klasse
        total_lessons_by_category = schoolclass.total_lessons_per_category()

        # Opret en dictionary med personalekategorier som nøgler og antal lektioner som værdier
        lessons_by_category_dict = {
            f"{category}": lessons
            for category, lessons in total_lessons_by_category.items()
        }

        # Opret en streng, der indeholder navnet på skoleklassen efterfulgt af lektionerne pr. personalekategori
        class_data = lessons_by_category_dict

        # Hent det samlede antal lektioner pr. personalekategori for denne klasse
        total_lessons_by_category_class = schoolclass.total_lessons_per_category()
        for category, lessons in total_lessons_by_category_class.items():
            total_lessons_by_category[category] += lessons

        # Tilføj opsummeringsdata til listen
        summary_data.append(
            {
                "class_name": schoolclass.name,
                "num_students": num_students,
                "sum_school_fee": sum_school_fee,
                "sum_school_fee_amount": sum_school_fee_amount,
                "num_lessons": num_lessons,
                "employment_categories": employment_categories,
                "class_data": class_data,
            }
        )

    # Convert total_hours_by_category to a list of tuples
    total_hours_list = [
        (category, hours) for category, hours in total_hours_by_category.items()
    ]

    # Calculate total surplus for the team
    surplus = total_school_fee_for_team - total_price_for_team

    # Calculate percentage of school fee used
    percentage_used = 0
    if total_school_fee_for_team > 0:
        percentage_used = round(
            (total_price_for_team / total_school_fee_for_team) * 100, 1
        )

    # Formatering af tal som DKK
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
            "team": team,
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


def department_detail(request, department_id):
    department = Department.objects.get(pk=department_id)
    teams = department.teams.all()
    return render(
        request,
        "skole/department_detail.html",
        {
            "department": department,
            "teams": teams,
        },
    )
