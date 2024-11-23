from django.urls import path

from .views import (
    DepartmentCreateView,
    DepartmentDetailView,
    DepartmentEditView,
    DepartmentListView,
    EmploymentCategoryCreateView,
    EmploymentCategoryDetailView,
    EmploymentCategoryEditView,
    EmploymentCategoryListView,
    LessonCreateView,
    LessonDetailView,
    LessonEditView,
    LessonListView,
    SchoolClassCreateView,
    SchoolClassListView,
    SchoolCreateView,
    SchoolDetailView,
    SchoolEditView,
    SchoolFeeCreateView,
    SchoolFeeDetailView,
    SchoolFeeEditView,
    SchoolFeeListView,
    SchoolListView,
    StaffCreateView,
    StaffDetailView,
    StaffEditView,
    StaffListView,
    StudentCreateView,
    StudentDetailView,
    StudentEditView,
    StudentListView,
    TeamCreateView,
    TeamDetailView,
    TeamEditView,
    TeamListView,
    department_detail,
    department_edit,
    homepage,
    schoolclass_detail,
    schoolclass_edit,
    student_detail,
    student_edit,
    team_detail,
    team_edit,
)

urlpatterns = [
    # Home
    path("", homepage, name="homepage"),
    # School
    path("schools/", SchoolListView.as_view(), name="school_list"),
    path("school/<int:pk>/", SchoolDetailView.as_view(), name="school_detail"),
    path("school/<int:pk>/edit/", SchoolEditView.as_view(), name="school_edit"),
    # Department
    path("departments/", DepartmentListView.as_view(), name="department_list"),
    path(
        "department/create/", DepartmentCreateView.as_view(), name="department_create"
    ),
    path(
        "department/<int:department_id>/",
        department_detail,
        name="department_detail",
    ),
    path(
        "department/<int:department_id>/edit/",
        department_edit,
        name="department_edit",
    ),
    # Team
    path("teams/", TeamListView.as_view(), name="team_list"),
    path("team/create/", TeamCreateView.as_view(), name="team_create"),
    path("team/<int:team_id>/", team_detail, name="team_detail"),
    path("team/<int:team_id>/edit/", team_edit, name="team_edit"),
    # Schoolclass
    path(
        "schoolclass/<int:class_id>/",
        schoolclass_detail,
        name="schoolclass_detail",
    ),
    path("schoolclass/create/", SchoolClassCreateView.as_view(), name="schoolclass_create"),
    path(
        "schoolclass/<int:class_id>/edit/",
        schoolclass_edit,
        name="schoolclass_edit",
    ),
    path("schoolclasses/", SchoolClassListView.as_view(), name="schoolclass_list"),
    # Lesson
    path("lessons/", LessonListView.as_view(), name="lesson_list"),
    path("lesson/create/", LessonCreateView.as_view(), name="lesson_create"),
    path("lesson/<int:pk>/", LessonDetailView.as_view(), name="lesson_detail"),
    path("lesson/<int:pk>/edit/", LessonEditView.as_view(), name="lesson_edit"),
    # School Fee
    path("school-fees/", SchoolFeeListView.as_view(), name="schoolfee_list"),
    path("school-fee/create/", SchoolFeeCreateView.as_view(), name="schoolfee_create"),
    path(
        "school-fee/<int:pk>/", SchoolFeeDetailView.as_view(), name="schoolfee_detail"
    ),
    path(
        "school-fee/<int:pk>/edit/", SchoolFeeEditView.as_view(), name="schoolfee_edit"
    ),
    # Student
    path("students/", StudentListView.as_view(), name="student_list"),
    path("student/create/", StudentCreateView.as_view(), name="student_create"),
    path("student/<int:pk>/", student_detail, name="student_detail"),
    path("student/<int:pk>/edit/", student_edit, name="student_edit"),
    # Employment Category
    path(
        "employment-categories/",
        EmploymentCategoryListView.as_view(),
        name="employmentcategory_list",
    ),
    path(
        "employment-category/create/",
        EmploymentCategoryCreateView.as_view(),
        name="employmentcategory_create",
    ),
    path(
        "employment-category/<int:pk>/",
        EmploymentCategoryDetailView.as_view(),
        name="employmentcategory_detail",
    ),
    path(
        "employment-category/<int:pk>/edit/",
        EmploymentCategoryEditView.as_view(),
        name="employmentcategory_edit",
    ),
    # Staff
    path("staff/", StaffListView.as_view(), name="staff_list"),
    path("staff/create/", StaffCreateView.as_view(), name="staff_create"),
    path("staff/<int:pk>/", StaffDetailView.as_view(), name="staff_detail"),
    path("staff/<int:pk>/edit/", StaffEditView.as_view(), name="staff_edit"),
]
