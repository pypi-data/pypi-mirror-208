#%%
import pandas as pd
import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from kpi_dashapp_demo.builders import (kpi_sidebar_layout, kpi_layout, 
                      usertype_kpi_layout, main_layout,
                      app_description, intro_layout)
from kpi_dashapp_demo.helper_components import plot_barplot
from kpi_dashapp_demo.kpi_utils import get_path

data_path = get_path(folder_name='kpi_dashapp_demo/Data', file_name='new_data.csv')

data = pd.read_csv(data_path)
# %%
app = dash.Dash(__name__, external_stylesheets=[
                                                dbc.themes.SOLAR,
                                                dbc.icons.BOOTSTRAP,
                                                dbc.icons.FONT_AWESOME
                                            ],
                suppress_callback_exceptions=True,
                )

app.layout = main_layout


app.validation_layout = [kpi_sidebar_layout, kpi_layout, usertype_kpi_layout, app_description]


@app.callback(
    Output(component_id="main_content", component_property="children"),
    Input(component_id="location", component_property="href"),
)
def show_page_display(href):
    site_page = href
    site_to_view = site_page.split("/")[-1]
    if site_to_view == "kpi_page":
        return kpi_sidebar_layout
    else:
        return app_description
    
@app.callback(
    Output("page_content", "children"),
    [
        Input("id_home", "n_clicks_timestamp"),
        Input("id_kpi", "n_clicks_timestamp"),
        Input("id_user_kpi", "n_clicks_timestamp"),
    ],
)
def sidebar_display(home: str, kpi: str, usertype_kpi: str):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if not ctx.triggered:
        return intro_layout
    elif button_id == "id_kpi":
        return kpi_layout
    elif button_id == "id_user_kpi":
        return usertype_kpi_layout
    else:
        return intro_layout    
    
@app.callback(Output(component_id='id_conversion', component_property='children'),
              Output(component_id='id_bounce', component_property='children'),
              Output(component_id='conversion_graph', component_property='figure'),
              Output(component_id='bounce_graph', component_property='figure'),
              Input(component_id='id_year_dropdown', component_property='value'),
              Input(component_id='id_month_dropdown', component_property='value')
              )
def compute_kpi(year_selected: str, month_selected: str):
    if not(year_selected and month_selected):
        raise PreventUpdate
    else:
        conrate = (data[(data["Year"]== year_selected) & 
                        (data["Month"] == month_selected)]
                   ['conversion_rate'].item()
                   )
        bounce_rate = (data[(data["Year"]== year_selected) & 
                        (data["Month"] == month_selected)]
                   ['bounce_rate'].item()
                   )
        graph_data = data[data["Year"]==year_selected]
        
        conrate_graph = plot_barplot(data = graph_data, x_colname='Month',
                                     y_colname='conversion_rate',
                                     title=f'Conversion rates during {year_selected}')
        
        bounce_graph = plot_barplot(data=graph_data, x_colname='Month', 
                                    y_colname='bounce_rate',
                                    title=f'Bounce rates during {year_selected}'
                                    )
        return f'{conrate}%', f'{bounce_rate}%', conrate_graph, bounce_graph
    
    
## render user type kpi
@app.callback(Output(component_id='id_newuser_conversion', component_property='children'),
              Output(component_id='id_newuser_bounce', component_property='children'),
              Output(component_id='id_returnuser_conversion', component_property='children'),
              Output(component_id='id_returnuser_bounce', component_property='children'),
              Output(component_id='id_total_new_user', component_property='children'),
              Output(component_id='id_total_return_use', component_property='children'),
              Output(component_id='return_user_graph', component_property='figure'),
              Output(component_id='new_user_graph', component_property='figure'),
              Input(component_id='id_user_year_dropdown', component_property='value'),
              Input(component_id='id_user_month_dropdown', component_property='value')
              )
def compute_usertype_kpi(user_year_selected: str, user_month_selected: str):
    if not(user_year_selected and user_month_selected):
        raise PreventUpdate
    else:
        newuser_conrate = (data[(data["Year"]== user_year_selected) & 
                        (data["Month"] == user_month_selected)]
                   ['new_user_con_rate'].item()
                   )#.sort()
        newuser_bounce_rate = (data[(data["Year"]== user_year_selected) & 
                        (data["Month"] == user_month_selected)]
                   ['new_user_bounce_rate'].item()
                   )
        
        returnuser_conrate = (data[(data["Year"]== user_year_selected) & 
                        (data["Month"] == user_month_selected)]
                   ['return_user_con_rate'].item()
                   )
        returnuser_bounce_rate = (data[(data["Year"]== user_year_selected) & 
                        (data["Month"] == user_month_selected)]
                   ['return_user_bounce_rate'].item()
                   )
        
        total_newuser = (data[(data["Year"]== user_year_selected) & 
                        (data["Month"] == user_month_selected)]
                   ['new_user'].item()
                   )
        
        total_returnuser = (data[(data["Year"]== user_year_selected) & 
                        (data["Month"] == user_month_selected)]
                   ['return_user'].item()
                   )
        graph_data = data[data["Year"]==user_year_selected]
        
        total_returnuser_graph = plot_barplot(data = graph_data, x_colname='Month',
                                     y_colname='return_user',
                                     title=f'Total return user per month in {user_year_selected}')
        
        total_newuser_graph = plot_barplot(data=graph_data, x_colname='Month', 
                                    y_colname='new_user',
                                    title=f'Total new user per month in {user_year_selected}'
                                    )
        return (f'{newuser_conrate}%', f'{newuser_bounce_rate}%',
                 f'{returnuser_conrate}%', f'{returnuser_bounce_rate}%',
                 total_newuser, total_returnuser,
                 total_returnuser_graph, total_newuser_graph
                )  

if __name__ == '__main__':
    app.run_server(port=8040, debug=False)

# %%

