from django.urls import path
from . import views

urlpatterns = [
    # i have a name so i can refer to it easily, and do not need to 
    path('', views.my_cool_chart_view, name='cool-chart'),
]