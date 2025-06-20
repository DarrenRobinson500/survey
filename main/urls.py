from django.contrib import admin
from django.urls import path
from app.views import *
from django.conf import settings # new
from  django.conf.urls.static import static #new

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", home, name="home"),
    path("home", home, name="home"),

    # User registration
    path("signup", signup, name="signup"),
    path("switch", switch, name="switch"),
    path('login/', login_user, name="login"),
    path('logout/', logout_user, name="logout"),

    # Files
    # path("files", files, name="files"),
    # path("file_upload", file_upload, name="file_upload"),
    # path("file_to_db/<id>", file_to_db, name="file_to_db"),

    path("download", download, name="download"),

    # Generic
    path("new/<model_str>", new, name="new"),
    path("list_view/<model_str>", list_view, name="list_view"),
    path("item/<model_str>/<id>", item, name="item"),
    path("new/<model_str>", new, name="new"),
    path("edit/<model_str>/<id>", edit, name="edit"),
    path("toggle_value/<id>/<parameter>", toggle_value, name="toggle_value"),
    path("delete/<model_str>/<id>", delete, name="delete"),
    path("delete_all/<model_str>/", delete_all, name="delete_all"),
    path("make_data/<model_str>/", make_data, name="make_data"),
    path("development", development, name="development"),

    # Descriptions
    path("edit_descriptions", edit_descriptions, name="edit_descriptions"),

    # Periods
    path('add_previous/<id>', add_previous, name='add_previous'),
    path('add_next/<id>', add_next, name='add_next'),

    # Answers
    path('answers', answers, name='answers'),
    path('select/<model_str>/<id>', select, name='select'),
    path('add_answer/<answer_id>/<answer_str>', add_answer, name='add_answer'),
    path('add_notes/<answer_id>', add_notes, name='add_notes'),

]