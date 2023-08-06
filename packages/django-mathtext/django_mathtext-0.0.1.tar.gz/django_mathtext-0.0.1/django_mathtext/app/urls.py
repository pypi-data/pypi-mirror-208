from django.urls import path

from . import views

urlpatterns = [
    # path("", views.home, name="home"),
    path("text2int/", views.text2int_ep, name="text2int"),
    path("nlu/", views.evaluate_user_message_with_nlu_api, name="nlu"),
    path("num_one/", views.num_one, name="num_one"),
]
