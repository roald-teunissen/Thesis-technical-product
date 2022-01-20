import altair as alt
from django.http import JsonResponse
from django.shortcuts import render
import altair
import duckdb
import pandas as pd
from datetime import date

def annual_overview(req):
    return JsonResponse(retrieve_annual_chart().to_dict(), safe = False)

def index(request):
    return render(request, 'index.html')

def retrieve_annual_chart(from_year = 2009, to_year = date.today().year):
    from_year = str(from_year)
    to_year = str(to_year)

    # Initialize connection with DuckDB and retrieve data
    conn = duckdb.connect()
    source  = conn.execute("SELECT * FROM './stats/static/datasets/annual.development.parquet' WHERE year >= " + from_year + " AND year <= " + to_year).df()

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

    line = altair.Chart(source[source['green'] == 'yes']).mark_line(stroke = '#5276A7', interpolate = 'monotone').encode(
        altair.X('year', type='ordinal', 
                axis = altair.Axis(
                    labelAngle = 0,
                    labelAlign = 'center',
                    labelPadding = 7,
                    )
                ),
        altair.Y('percentage',
                scale = altair.Scale(domain = (0,100)),
                axis = altair.Axis(
                    title = 'Percentage of green domains (%)', 
                    titleColor = '#5276A7',
                    grid = True,
                    orient = 'left',
                ),
        ),
    )

    return altair.layer(bar, line).resolve_scale(
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

def retrieve_monthly_chart(from_year = 2017, to_year = date.today().year):
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

     