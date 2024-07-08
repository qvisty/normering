from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="sliderindex"),
    path("update-result/", views.update_result, name="update_result"),
]
