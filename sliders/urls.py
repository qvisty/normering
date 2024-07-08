from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("update-result/", views.update_result, name="update_result"),
]
