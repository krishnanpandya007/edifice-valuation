from django.urls import path

from .views import home, login, logout_view, register_site, register_site_form

urlpatterns = [
    path("", home, name="home"),
    path("login/", login, name="login"),
    path("logout/", logout_view, name="logout"),
    path("register/site/", register_site, name="register_site"),
    path("register/site/data/", register_site_form, name="register_site_form"),
]