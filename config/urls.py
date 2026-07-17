from django.contrib import admin
from django.urls import include, path
from django.shortcuts import redirect


def home(request):
    return redirect("balance_list")


urlpatterns = [
    path("", home),

    path("admin/", admin.site.urls),

    path("", include("users.urls")),

    path("promyvki/", include("promyvki.urls")),

    path("balance/", include("balance.urls")),
]