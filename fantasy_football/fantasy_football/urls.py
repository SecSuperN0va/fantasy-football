"""
URL configuration for fantasy_football project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from home.views import HomeView, ScrapeView
from league.views import LeaguesView, LeagueView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', HomeView.as_view(),  name='home'),
    path('leagues/', LeaguesView.as_view(), name='leagues'),
    path('league/<int:league_id>', LeagueView.as_view(), name='league'),
    path('scrape', ScrapeView.as_view(pattern_name='home'), name='scrape')
]
