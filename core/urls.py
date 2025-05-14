from django.urls import path

from .views import home, login, logout_view, register_site, register_site_form, password_reset, edit_assignees, view_site, create_site, export_file, change_status

urlpatterns = [
    path("", home, name="home"),
    path("login/", login, name="login"),
    path("logout/", logout_view, name="logout"),
    path("register/site/", register_site, name="register_site"),
    path("register/site/data/", register_site_form, name="register_site_form"),
    path("password-reset/<str:token>/", password_reset, name="password_reset"),
    path("edit/assignees/<int:site_id>/", edit_assignees, name="edit_assignees"),
    path("view/site/<int:site_id>/", view_site, name="view_site"),
    path("create/site/", create_site, name="create_site"),
    path("change/status/<int:site_id>/", change_status, name="change_status"),
    path('export/<str:format_type>/<int:site_id>/', export_file, name='export_file'),
]