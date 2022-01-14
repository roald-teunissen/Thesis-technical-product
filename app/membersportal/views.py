import altair as alt
from django.http import JsonResponse
from django.shortcuts import render


def my_cool_chart_view(req):
    return JsonResponse({'test': 'test'})
    # query = MyModel.objects.all().values()
    # data = alt.Data(values=list(query))
    # chart_obj = alt.Chart(data).mark_bar().encode(
    #     # encode your data using the channels
    #     # and marks grammar we covered before 
    #     # you want here
    # )       
    # return JsonResponse(chart_obj)

# def index_page(req):
    # render(req, "index_page.html")
