from dash import dcc, html
import dash_bootstrap_components as dbc
from kpi_dashapp_demo.style import card_icon
import plotly.express as px
import pandas as pd
from typing import List

def output_card(id: str = None, card_label: str =None,
                style={"backgroundColor": 'yellow'},
                icon: str ='bi bi-cash-coin', card_size: int = 4):
    return dbc.Col(lg=card_size,
                        children=dbc.CardGroup(
                        children=[
                                    dbc.Card(
                                    children=[
                                        dcc.Loading(type='circle', children=html.H3(id=id)),
                                        html.P(card_label)
                                    ]
                                ),
                            dbc.Card(
                                    children=[
                                        html.Div(
                                            className=icon,
                                            style=card_icon
                                        )
                                    ],
                                    style=style
                            )
                        ]
                    )
                )

# function to create barplot   
def plot_barplot(data: pd.DataFrame,
                    x_colname: str,
                    y_colname: str,
                    title: str = None,
                    ):
    """ Barplot 
    Args:
        data (pd.DataFrame): Data which contains variables to plot
        
        y_colname (str): column name (variable) to plot on y-axis
        x_colname (str): column name (variable) to plot on x-axis
    """
    data = data[[x_colname, y_colname]].dropna()
    fig = px.bar(data, x=x_colname, y=y_colname,
                     title=title,
                     template='plotly_dark',
                     color=x_colname
                     )
    return fig    





