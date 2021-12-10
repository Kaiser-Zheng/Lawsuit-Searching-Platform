from django.urls import path
from search_info import views

urlpatterns = [
    path('', views.home, name="home"), # homepage
    path('table/', views.table, name="table"), #template

    path('search_info/', views.search_info, name="search_info"),
    path('law_personal/', views.law_personal, name="law_personal"),
    path('law_company/', views.law_company, name="law_company"),



]


