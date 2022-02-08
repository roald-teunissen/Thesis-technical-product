"""
*Abstract Factory Pattern for the main graph
This pattern serves to provide an interface for different implementations of 
time scopes, such as annually, monthly and daily.

The implementations return a dictionary for the Altair library to use.
"""

from typing import Type

import altair as alt
import duckdb


class Graph:
    def __init__(self, start_year, end_year, tld) -> None:
        self.start_year = start_year
        self.end_year = end_year
        self.tld = tld

    def create_visualization(self) -> None:
        raise NotImplementedError
    
    def get_source(self, query) -> None:
        conn = duckdb.connect()
        source = conn.execute(query).df()

        # Convert the numbers of lookups to a more readable size
        source['look_ups'] = source['look_ups']/1000000
        return source

class Annual(Graph):
    def __init__(self, start_year, end_year, tld) -> None:
        super().__init__(start_year, end_year, tld)

        dataset_location = './stats/static/datasets/annual.development.parquet'

        if (self.tld and self.tld != 'global'):
            # Query based on Top-Level Domain (TLD)
            query = "SELECT * FROM '{}' WHERE year >= {} AND year <= {} AND tld = '{}'".format(dataset_location, self.start_year, self.end_year, self.tld)
            graph_title = "Greencheck annual overview for .{} - {} to {}".format(self.tld, self.start_year, self.end_year)
        else:
            # No TLD specified, so query all TLDs
            query = "SELECT year, green, sum(look_ups) AS look_ups FROM '{}' WHERE year >= {} AND year <= {} GROUP BY year, green".format(dataset_location, self.start_year, self.end_year)
            graph_title = "Greencheck annual overview - {} to {}".format(self.start_year, self.end_year)

        self.graph_title = graph_title
        self.source = super().get_source(query)

    def create_visualization(self) -> None:
        return alt.Chart(self.source).mark_bar().encode(
            alt.X('year', 
                    title = 'Years', 
                    type = 'ordinal', 
                    axis = alt.Axis(
                        labelAngle = 0
                        )
                    ),
            alt.Y('look_ups', 
                    title = 'lookups', 
                    axis = alt.Axis(
                        title = 'Millions of lookups',
                        titleColor = '#97CE64',
                    ),
                ),
            alt.Color('green', 
                        title = 'Green',
                        scale = alt.Scale(
                            domain = ['yes', 'no'],
                            range = ['#C3E3A6', '#CECCCA']
                        )
            )
        ).properties(
            title = self.graph_title,

            width = 1000,
            height = 400,
        ).configure_legend(
            labelFontSize = 12,
            
            # Legend placement
            orient = 'none',
            direction = 'horizontal',
            titleOrient = 'left',
            legendX = 450,
            legendY = -20,
        ).configure_axis(
            labelFontSize = 13,
            titleFontSize = 15,
        ).configure_title(
            fontSize = 18,
        ).to_dict()


class Month(Graph):
    def __init__(self, start_year, end_year, tld) -> None:
        super().__init__(start_year, end_year, tld)

        dataset_location = './stats/static/datasets/monthly.lookups.parquet'

        if (self.tld and self.tld != 'global'):
            # Query based on Top-Level Domain (TLD)
            query = "SELECT * FROM '{}' WHERE year >= {} AND year <= {} AND tld = '{}'".format(dataset_location, self.start_year, self.end_year, self.tld)
            graph_title = "Greencheck monthly overview for .{} - {} to {}".format(self.tld, self.start_year, self.end_year),
        else:
            # No TLD specified, so query all TLDs
            query = "SELECT year, month, green, sum(look_ups) AS look_ups FROM '{}' WHERE year >= {} AND year <= {} GROUP BY year, month, green".format(dataset_location, self.start_year, self.end_year)
            graph_title = "Greencheck monthly overview - {} to {}".format(self.start_year, self.end_year),

        self.graph_title = graph_title
        self.source = super().get_source(query)

    def create_visualization(self) -> None:
        return alt.Chart(self.source).mark_bar().encode(
            alt.X('month', 
                    title = '', 
                    type = 'ordinal',
                    axis = None
                ),
            alt.Column('year:O', 
                        title = self.graph_title, 
                        spacing = 2,
                        header = alt.Header(
                            titleFontSize = 15, 
                            labelFontSize = 13, 
                            titlePadding = 20
                            )
                        ),
            alt.Y('look_ups', title = 'Millions of lookups'),
            alt.Color('green', 
                        title = 'Green',
                        scale = alt.Scale(
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
            legendX = 450,
            legendY = -50,
        ).properties(
            width = 75,
        ).to_dict()


class GraphAction:
    def __init__(self, graph_factory: Type[Graph], start_year, end_year, tld) -> None:
        self.graph_factory = graph_factory(start_year, end_year, tld)
        
    def retrieve_visualization(self) -> Graph:
        graph = self.graph_factory
        return graph.create_visualization()
