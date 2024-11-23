from django.urls import path

from . import views

urlpatterns = [
    # Schoolclass
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
    # Team
    path("team/<int:team_id>/", views.team_detail, name="team_detail"),
    path("team/<int:team_id>/edit/", views.team_edit, name="team_edit"),
    # Department
    path(
        "department/<int:department_id>/",
        views.department_detail,
        name="department_detail",
    ),
    path(
        "department/<int:department_id>/edit/",
        views.department_edit,
        name="department_edit",
    ),
    # Student
    path("student/<int:pk>/", views.student_detail, name="student_detail"),
    path("student/<int:pk>/edit/", views.student_edit, name="student_edit"),
    # home
    path("", views.homepage, name="homepage"),
]
