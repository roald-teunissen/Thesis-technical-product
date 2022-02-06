import pandas as pd
import urllib
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .patterns.creational.graph_abstract_factory_pattern import GraphAction, Annual, Month

from .forms import StatFilterForm


def retrieve_graph_data(request):
    scope = request.GET.get('scope')
    tld = request.GET.get('tld')

    if (scope == 'monthly'):
        graph_action = GraphAction(Month, 2009, 2021, tld)
    else:
        graph_action = GraphAction(Annual, 2009, 2021, tld)
    
    return JsonResponse(graph_action.retrieve_visualization(), safe = False)

@csrf_exempt
def index(request):
    if request.htmx:
        # Refresh partial template
        form = StatFilterForm(request.POST or None)

        if form.is_valid():
            time_scope = form.cleaned_data.get("time_scope")
            tld = form.cleaned_data.get("tld")

        template_name = "partials/greencheck_graph.html"
        graph_data_url = "/retrieve_graph_data/?" + urllib.parse.urlencode({'scope': time_scope,'tld': tld})
    else:
        # Serve the whole page
        form = StatFilterForm()
        template_name = "index.html"
        graph_data_url = "/retrieve_graph_data/?scope=annually"
    
    return render(request, template_name, {'graphUrl': graph_data_url, 'form': form})