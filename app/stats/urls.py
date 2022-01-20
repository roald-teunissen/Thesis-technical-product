from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('retrieve_graph_data/', views.retrieve_graph_data, name='retrieve_graph_data'),
]