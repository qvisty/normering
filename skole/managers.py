from django.db import models
from django.db.models import IntegerField, Value
from django.db.models.functions import Cast, Substr
from django.db.models import Case, When


class SchoolClassManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(
                class_number=Case(
                    When(
                        name__regex=r"^\d+",
                        then=Cast(Substr("name", 1, 2), IntegerField()),
                    ),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            )
            .order_by("team__department__name", "class_number", "name")
        )
