from django.shortcuts import render


def home_views(request):
    return render(request, "app_gestion_centro_cultural/home.html")
