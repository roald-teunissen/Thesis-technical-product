from datetime import date

import altair
import duckdb
import pandas as pd
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .forms import StatFilterForm


def retrieve_graph_data(request):
    scope = request.GET.get('scope')

    if (scope == 'monthly'):
        data = retrieve_monthly_chart()
    else:
        data = retrieve_annual_chart()
    
    return JsonResponse(data.to_dict(), safe = False)

@csrf_exempt
def index(request):
    if request.htmx:
        # refresh partial template
        form = StatFilterForm(request.POST or None)

        if form.is_valid():
            time_scope= form.cleaned_data.get("time_scope")
        else:
            time_scope = 'annually'

        template_name = "partials/greencheck_graph.html"
        graph_url = "/retrieve_graph_data/?scope=" + time_scope
    else:
        # serve the whole page
        form = StatFilterForm()
        template_name = "index.html"
        graph_url = "/retrieve_graph_data/?scope=annually"
    
    return render(request, template_name, {'graphUrl': graph_url, 'form': form})

def retrieve_annual_chart(from_year = 2009, to_year = date.today().year, tld = None):
    from_year = str(from_year)
    to_year = str(to_year)

    # Initialize connection with DuckDB and retrieve data
    conn = duckdb.connect()
    
    if (tld):
        query = "SELECT * FROM './stats/static/datasets/annual.development.parquet' WHERE year >= " + from_year + " AND year <= " + to_year + " AND tld = '" + tld + "'"
    else:
        query = "SELECT year, green, sum(look_ups) AS look_ups FROM './stats/static/datasets/annual.development.parquet' WHERE year >= " + from_year + " AND year <= " + to_year + " GROUP BY year, green"

    source  = conn.execute(query).df()

    # Convert the numbers of lookups to a more readable size
    source['look_ups'] = source['look_ups']/1000000

    # Build Altair chart
    base = altair.Chart(source).encode(
        altair.X('year:O')
    )

    bar = altair.Chart(source).mark_bar().encode(
        altair.X('year', 
                title = 'Years',
                type = 'ordinal',
            ),
        altair.Y('look_ups', 
                title = 'lookups', 
                axis = altair.Axis(
                    title = 'Millions of lookups',
                    titleColor = '#97CE64',
                    orient = 'right',
                ),
            ),
        altair.Color('green', 
                    title = 'Green',
                    scale = altair.Scale(
                        domain = ['yes', 'no'],
                        range = ['#C3E3A6', '#CECCCA']
                    )
        )
    )

    # line = altair.Chart(source[source['green'] == 'yes']).mark_line(stroke = '#5276A7', interpolate = 'monotone').encode(
    #     altair.X('year', type='ordinal', 
    #             axis = altair.Axis(
    #                 labelAngle = 0,
    #                 labelAlign = 'center',
    #                 labelPadding = 7,
    #                 )
    #             ),
    #     altair.Y('percentage',
    #             scale = altair.Scale(domain = (0,100)),
    #             axis = altair.Axis(
    #                 title = 'Percentage of green domains (%)', 
    #                 titleColor = '#5276A7',
    #                 grid = True,
    #                 orient = 'left',
    #             ),
    #     ),
    # )

    return altair.layer(bar).resolve_scale(
        y = 'independent'
    ).properties(
        title = "Greencheck annual overview - " + from_year + " to " + to_year,

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

def retrieve_monthly_chart(from_year = 2009, to_year = date.today().year):
    chart_width = 1000
    column_width = chart_width/(to_year - from_year)
    from_year = str(from_year)
    to_year = str(to_year)

    conn = duckdb.connect()
    source  = conn.execute("SELECT * FROM './stats/static/datasets/monthly.lookups.parquet' WHERE year >= " + from_year + " AND year <= " + to_year).df()

    source['look_ups'] = source['look_ups']/1000000

    return altair.Chart(source).mark_bar().encode(
        altair.X('month', 
                title = '', 
                type = 'ordinal',
                axis = altair.Axis(
                    labelAngle = 0,
                    labelAlign = 'center',
                    labelPadding = 0,
                    tickCount = 5,
                    )
                ),
        altair.Column('year:O', 
                    title = "Greencheck monthly overview - " + from_year + " to " + to_year,
                    spacing = 3,
                    header = altair.Header(titleFontSize = 15, labelFontSize = 13, titlePadding = 20)),
        altair.Y('look_ups', title = 'Millions of lookups'),
        altair.Color('green', 
                    title = 'Green',
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
        legendX = chart_width/2,
        legendY = -50,
    ).properties(
        width = column_width,
    )

     