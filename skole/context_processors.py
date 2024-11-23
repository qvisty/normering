from django.db.models import IntegerField, Value
from django.db.models.functions import Cast
from django.db.models import Case, When, F
from .models import School, Department, Team, SchoolClass


def global_context(request):
    all_schools = School.objects.all()
    all_departments = Department.objects.all().order_by(
        "name"
    )  # Sorter afdelinger alfabetisk
    all_teams = Team.objects.all().order_by(
        "department__name", "name"
    )  # Sorter teams efter afdeling og derefter alfabetisk indenfor afdeling

    all_schoolclasses = SchoolClass.objects.annotate(
        class_number=Cast(
            Case(When(name__regex=r"^\d+", then=F("name")), default=Value("0")),
            IntegerField(),
        )
    ).order_by("team__department__name", "class_number", "name")

    return {
        "all_schools": all_schools,
        "all_departments": all_departments,
        "all_teams": all_teams,
        "all_schoolclasses": all_schoolclasses,
    }
