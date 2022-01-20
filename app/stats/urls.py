from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('annual_overview/', views.annual_overview, name='annual_overview'),
        
    # path('cool_chart/',
    #         views.my_cool_chart_view,
    #         name='my-cool-chart'
    #     ),
]