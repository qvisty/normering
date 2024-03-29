from django.urls import path
from . import views

urlpatterns = [
    path('schoolclass/<int:class_id>/', views.school_class_detail, name='school_class_detail'),
    path('team/<int:team_id>/', views.team_detail, name='team_detail'),
    path('', views.homepage, name='homepage'),
]
