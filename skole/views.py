from django.shortcuts import render
from django.db.models import Sum, CharField, Count, Value, F
from django.db.models.functions import Concat
from .models import (
    SchoolClass,
    Lesson,
    Team,
    SchoolFee,
    Staff,
    EmploymentCategory,
    Department,
)
from collections import defaultdict
from operator import itemgetter


def school_class_detail(request, class_id):
    school_class = SchoolClass.objects.annotate(
        total_school_fee=Sum("students__school_fee__amount")
    ).get(pk=class_id)
    lessons = (
        Lesson.objects.filter(school_class=school_class)
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
    total_lessons_in_class = Lesson.objects.filter(school_class=school_class).count()

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
    if school_class.total_school_fee and total_price_for_class:
        if school_class.total_school_fee > 0 and total_price_for_class > 0:
            surplus = int(school_class.total_school_fee - total_price_for_class)
            percentage_used = round(
                (total_price_for_class / school_class.total_school_fee) * 100, 1
            )

    return render(
        request,
        "skole/schoolclass_detail.html",
        {
            "school_class": school_class,
            "lessons": lessons,
            "total_hours": total_hours_list,
            "total_sum": total_sum,
            "total_lessons_in_class": total_lessons_in_class,
            "total_price_for_class": total_price_for_class,
            "surplus": surplus,
            "percentage_used": percentage_used,
        },
    )


def homepage(request):
    school_classes = SchoolClass.objects.all()
    teams = Team.objects.all()
    departments = Department.objects.all()

    return render(
        request,
        "skole/homepage.html",
        {"school_classes": school_classes, "teams": teams, "departments": departments},
    )


from operator import itemgetter


def team_detail(request, team_id):
    team = Team.objects.get(pk=team_id)
    school_classes = SchoolClass.objects.filter(team=team)
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

    for school_class in school_classes:
        lessons = (
            Lesson.objects.filter(school_class=school_class)
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
            for student in school_class.students.all()
            if student.school_fee
        )
        total_school_fee_for_team += total_school_fee_for_class

        # Beregn antal elever i klassen
        num_students = school_class.students.count()
        totals["num_students"] += num_students

        # Beregn summen af school_fee for klassen
        sum_school_fee = sum(
            student.school_fee.amount
            for student in school_class.students.all()
            if student.school_fee
        )
        totals["school_fee"] += sum_school_fee

        # Beregn summen af school_fee_amount for klassen
        sum_school_fee_amount = (
            SchoolFee.objects.filter(student__school_class=school_class).aggregate(
                total_fee_amount=Sum("level")
            )["total_fee_amount"]
            or 0
        )
        totals["school_fee_amount"] += sum_school_fee_amount

        # Beregn antal lektioner i klassen
        num_lessons = school_class.lessons.count()
        totals["num_lessons"] += num_lessons

        # Hent det samlede antal lektioner pr. personalekategori for denne klasse
        total_lessons_by_category = school_class.total_lessons_per_category()

        # Opret en dictionary med personalekategorier som nøgler og antal lektioner som værdier
        lessons_by_category_dict = {
            f"{category}": lessons
            for category, lessons in total_lessons_by_category.items()
        }

        # Opret en streng, der indeholder navnet på skoleklassen efterfulgt af lektionerne pr. personalekategori
        class_data = lessons_by_category_dict

        # Hent det samlede antal lektioner pr. personalekategori for denne klasse
        total_lessons_by_category_class = school_class.total_lessons_per_category()
        for category, lessons in total_lessons_by_category_class.items():
            total_lessons_by_category[category] += lessons

        # Tilføj opsummeringsdata til listen
        summary_data.append(
            {
                "class_name": school_class.name,
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
