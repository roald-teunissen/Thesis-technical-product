from datetime import date

import altair
import duckdb
import pandas as pd
import urllib
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .forms import StatFilterForm


def retrieve_graph_data(request):
    scope = request.GET.get('scope')
    tld = request.GET.get('tld')

    if (scope == 'monthly'):
        data = retrieve_monthly_chart(tld)
    else:
        data = retrieve_annual_chart(tld)
    
    return JsonResponse(data.to_dict(), safe = False)

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

def retrieve_annual_chart(tld = None):
    dataset_location = './stats/static/datasets/annual.development.parquet'
    start_year = '2009'
    end_year = '2021'
   
    if (tld and tld != 'global'):
        # Query based on Top-Level Domain (TLD)
        query = "SELECT * FROM '{}' WHERE year >= {} AND year <= {} AND tld = '{}'".format(dataset_location, start_year, end_year, tld)
        graph_title = "Greencheck annual overview for .{} - {} to {}".format(tld, start_year, end_year),
    else:
        # No TLD specified, so query all TLDs
        query = "SELECT year, green, sum(look_ups) AS look_ups FROM '{}' WHERE year >= {} AND year <= {} GROUP BY year, green".format(dataset_location, start_year, end_year)
        graph_title = "Greencheck annual overview - {} to {}".format(start_year, end_year),

    # Initialize a connection with DuckDB and retrieve data
    conn = duckdb.connect()
    source  = conn.execute(query).df()

    # Convert the numbers of lookups to a more readable size
    source['look_ups'] = source['look_ups']/1000000

    # Build Altair chart
    base = altair.Chart(source).encode(altair.X('year:O'))

    bar_chart = altair.Chart(source).mark_bar().encode(
        altair.X('year', title = 'Years', type = 'ordinal'),
        altair.Y('look_ups', title = 'lookups', 
                axis = altair.Axis(
                    title = 'Millions of lookups',
                    titleColor = '#97CE64',
                    orient = 'right',
                ),
            ),
        altair.Color('green', title = 'Green',
                    scale = altair.Scale(
                        domain = ['yes', 'no'],
                        range = ['#C3E3A6', '#CECCCA']
                    )
        )
    )

    return altair.layer(bar_chart).resolve_scale(
        y = 'independent'
    ).properties(
        title = graph_title,

        width = 800,
        height = 400,
    ).configure_legend(
        labelFontSize = 12,
        
        # Legend placement
        orient = 'none',
        direction = 'horizontal',
        titleOrient = 'left',
        legendX = 250,
        legendY = -20,
    ).configure_axis(
        labelFontSize = 13,
        titleFontSize = 15,
    ).configure_title(
        fontSize = 18,
    )

def retrieve_monthly_chart(tld = None):
    dataset_location = './stats/static/datasets/monthly.lookups.parquet'
    start_year = 2009
    end_year = 2021

    # Calculate the graph size based on the number of years it will show
    final_chart_width = 800
    column_width = final_chart_width/(start_year - end_year)

    if (tld and tld != 'global'):
        # Query based on Top-Level Domain (TLD)
        query = "SELECT * FROM '{}' WHERE year >= {} AND year <= {} AND tld = '{}'".format(dataset_location, start_year, end_year, tld)
        graph_title = "Greencheck monthly overview for .{} - {} to {}".format(tld, start_year, end_year),
    else:
        # No TLD specified, so query all TLDs
        query = "SELECT year, green, sum(look_ups) AS look_ups FROM '{}' WHERE year >= {} AND year <= {} GROUP BY year, green".format(dataset_location, start_year, end_year)
        graph_title = "Greencheck monthly overview - {} to {}".format(start_year, end_year),

    # Initialize a connection with DuckDB and retrieve data
    conn = duckdb.connect()
    source = conn.execute(query).df()

    # Convert the numbers of lookups to a more readable size
    source['look_ups'] = source['look_ups']/1000000

    return altair.Chart(source).mark_bar().encode(
        altair.X('month', title = '', type = 'ordinal',
                axis = altair.Axis(
                    labelAngle = 0,
                    labelAlign = 'center',
                    labelPadding = 0,
                    tickCount = 5,
                    )
                ),
        altair.Column('year:O', title = graph_title,spacing = 1,
                    header = altair.Header(
                        titleFontSize = 15, 
                        labelFontSize = 13, 
                        titlePadding = 20
                        )
                    ),
        altair.Y('look_ups', title = 'Millions of lookups'),
        altair.Color('green', title = 'Green',
                    scale = altair.Scale(
                        domain = ['yes', 'no'],
                        range = ['#C3E3A6', '#CECCCA']
                    ),
        ),
    ).configure_axis(
        labelFontSize = 13,
        titleFontSize = 15,
    ).configure_legend(
        labelFontSize = 15,
        titleFontSize = 15,
        
        # Legend placement
        orient = 'none',
        direction = 'horizontal',
        titleOrient = 'left',
        legendX = final_chart_width/2,
        legendY = -50,
    ).properties(
        width = column_width,
    )

     