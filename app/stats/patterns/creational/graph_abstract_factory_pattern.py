"""
*What is this pattern about?

In Java and other languages, the Abstract Factory Pattern serves to provide an interface for
creating related/dependent objects without need to specify their
actual class.

The idea is to abstract the creation of objects depending on business
logic, platform choice, etc.

In Python, the interface we use is simply a callable, which is "builtin" interface
in Python, and in normal circumstances we can simply use the class itself as
that callable, because classes are first class objects in Python.

*What does this example do?
This particular implementation abstracts the creation of a pet and
does so depending on the factory we chose (Dog or Cat, or random_animal)
This works because both Dog/Cat and random_animal respect a common
interface (callable for creation and .speak()).
Now my application can create pets abstractly and decide later,
based on my own criteria, dogs over cats.

*Where is the pattern used practically?

*References:
https://sourcemaking.com/design_patterns/abstract_factory
http://ginstrom.com/scribbles/2007/10/08/design-patterns-python-style/

*TL;DR
Provides a way to encapsulate a group of individual factories.
"""

import random
import altair as alt
import duckdb
from typing import Type




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