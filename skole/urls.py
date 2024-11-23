from django.urls import path
from neapolitan.views import CRUDView

from . import views

urlpatterns = [
    # schoolclass
    path(
        "schoolclass/<int:class_id>/",
        views.schoolclass_detail,
        name="schoolclass_detail",
    ),
    path(
        "schoolclass/<int:class_id>/edit/",
        views.schoolclass_edit,
        name="schoolclass_edit",
    ),
    # team
    path("team/<int:team_id>/", views.team_detail, name="team_detail"),
    # department
    path(
        "department/<int:department_id>/",
        views.department_detail,
        name="department_detail",
    ),
    # home
    path("", views.homepage, name="homepage"),
]
