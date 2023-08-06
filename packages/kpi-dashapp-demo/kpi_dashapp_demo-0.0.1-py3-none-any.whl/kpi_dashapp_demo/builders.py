#%%
import dash_bootstrap_components as dbc
from dash import html, dcc
from kpi_dashapp_demo.style import homepage_icon_style, page_style, cardstyling
import dash_trich_components as dtc
from kpi_dashapp_demo.helper_components import output_card
import pandas as pd
from PIL import Image
from kpi_dashapp_demo.kpi_utils import get_path
#%%

img_kpi_path = get_path(folder_name='kpi_dashapp_demo/img', file_name='kpi.png')
img_scq_path = get_path(folder_name='kpi_dashapp_demo/img', file_name='SCQ.png')

img_kpi = Image.open(img_kpi_path)

img_scq = Image.open(img_scq_path)
#%%
data_path = get_path(folder_name='kpi_dashapp_demo/Data', 
                     file_name='new_data.csv'
                    )
data=pd.read_csv(data_path)

#%%
main_layout = html.Div(
    [
        dbc.NavbarSimple(
            brand="Company",
            brand_href="/",
            light=True,
            brand_style={"color": "#FFFFFF", "backgroundColor": "#00624e"},
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Location(id="location"),
                        html.Div(id="main_content"),
                    ]
                )
            ]
        ),
    ],
    style=page_style,
)


app_description = dbc.Container(
    style=page_style,
    children=[
        html.Br(), html.Br(),
        
        dbc.Row(
            children=[
                dbc.Col(),
                dbc.Col(
                    [
                        html.H2("KPI Dashboard"),
                        dbc.Card(
                            [
                                dbc.CardImg(
                                    src=img_kpi,
                                    top=True,
                                    style=homepage_icon_style,
                                ),
                                dbc.CardLink(
                                    children=[
                                        dbc.CardImgOverlay(
                                            [
                                                dbc.CardBody(
                                                    html.H1(
                                                        style={"margin": "5%"},
                                                    )
                                                )
                                            ]
                                        )
                                    ],
                                    href="kpi_page",
                                ),
                            ],
                            style={"width": "18rem", "height": "18rem"},
                        )
                    ]
                ),
                dbc.Col(),
            ]
        ),
        
        html.Br(),
    ]
)


kpi_sidebar_layout = html.Div(
    [
        dtc.SideBar(
            [
                dtc.SideBarItem(id="id_home", label="Home", 
                                icon="bi bi-house-fill" 
                                ),
                dtc.SideBarItem(id="id_kpi", label="KPI", 
                                icon="fas fa-chart-bar" 
                                ),
                dtc.SideBarItem(id="id_user_kpi", label="User type KPI", 
                                icon="fas fa-chart-line"
                                )
            ],
            bg_color="#00624e",
        ),
        html.Div([], id="page_content"),
    ]
)

kpi_layout = html.Div(
    [
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            id="date_dropdown", lg=3, style={"paddingLeft": "0%"},
                            children=[
                                        dbc.Label('Select Year'),
                                        dcc.Dropdown(id='id_year_dropdown',
                                                        options=[{"label": year, "value": year}
                                                                    for year in data['Year'].unique()
                                                                    ]
                                                        ),
                                        html.Br(),
                                      dbc.Label('Select Month'),
                                      dcc.Dropdown(id='id_month_dropdown',
                                                   options=[{'label': month, 'value': month}
                                                            for month in data['Month'].unique()
                                                            ]
                                                   )
                                    ]
                        ),
                        dbc.Col(
                            lg=9,
                            children=[
                                dbc.Row(
                                    [
                                        output_card(id="id_conversion", 
                                                    card_label="Conversion rate",
                                                    icon="bi bi-bookmark-check-fill",
                                                    style=cardstyling
                                                    ),
                                        output_card(id="id_bounce", 
                                                    card_label="Bounce rate",
                                                    icon="bi bi-building",
                                                    style=cardstyling
                                                    )
                                    ]
                                ),
                                
                            ],
                        ),
                    ]
                ),
                
                html.Br(),
                dbc.Row(
                    [
                        dbc.Col(lg=6,
                            children=[dcc.Graph(id='conversion_graph')]
                            ),
                        html.Br(),
                        dbc.Col(lg=6,
                            children=[dcc.Graph(id='bounce_graph')]
                            )
                    ]
                ),
                
            ]
        ),
    ]
)

usertype_kpi_layout = html.Div(
    [
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            id="user_date_dropdown", lg=3, style={"paddingLeft": "0%"},
                            children=[
                                        dbc.Label('Select Year'),
                                        dcc.Dropdown(id='id_user_year_dropdown',
                                                        options=[{"label": year, "value": year}
                                                                    for year in data['Year'].unique()
                                                                    ]
                                                        ),
                                      html.Br(),
                                      
                                      dbc.Label('Select Month'),
                                      dcc.Dropdown(id='id_user_month_dropdown',
                                                   options=[{'label': month, 'value': month}
                                                            for month in data['Month'].unique()
                                                            ]
                                                   )
                                    ]
                        ),
                        dbc.Col(
                            lg=9,
                            children=[
                                dbc.Row(
                                    [
                                        output_card(id="id_newuser_conversion", 
                                                    card_label="New User Conversion rate",
                                                    icon="bi bi-bookmark-check-fill",
                                                    style=cardstyling
                                                    ),
                                        output_card(id="id_newuser_bounce", 
                                                    card_label="New User Bounce rate",
                                                    icon="bi bi-bookmark-x",
                                                    style=cardstyling
                                                    ),
                                        output_card(id="id_returnuser_bounce", 
                                                    card_label="Returning Bounce rate",
                                                    icon="bi bi-bookmark-x",
                                                    style=cardstyling
                                                    )
                                    ]
                                ),
                                html.Br(),
                                dbc.Row(
                                    [
                                        output_card(id="id_returnuser_conversion", 
                                                    card_label="Returning Conversion rate",
                                                    icon="bi bi-bookmark-check-fill",
                                                    style=cardstyling
                                                    ),
                                        output_card(id="id_total_new_user", 
                                                    card_label="Number of New Users",
                                                    icon="bi bi-people",
                                                    style=cardstyling
                                                    ),
                                        output_card(id="id_total_return_use", 
                                                    card_label="Number of Returning Users",
                                                    icon="bi bi-people",
                                                    style=cardstyling
                                                    )
                                    ]
                                ),     
                            ],
                        ),
                    ]
                ),
                html.Br(),
                dbc.Row(
                        children=[
                                    dbc.Col(lg=6,
                                            children=[dcc.Graph(id='new_user_graph')]
                                        ),
                                    html.Br(),
                                    dbc.Col(lg=6,
                                            children=[dcc.Graph(id='return_user_graph')]
                                            )
                                ]
                    ),
            ]
        ),
    ]
)


intro_layout = dbc.Container(
    children=[
        dbc.Row(
            [
              html.H2("Key Performance Indicator (KPI) monitorying and reporting"),
              dbc.Col(lg=3),
              dbc.Col(lg=6,
                    children=[
                        dbc.Label('Business Problem Design'), html.Br(),
                        dbc.Card(
                            [
                                dbc.CardImg(
                                    src=img_scq,
                                    top=True,
                                    style=homepage_icon_style,
                                ),
                            ],
                        )
                    ]
                ),
              dbc.Col(lg=3)     
            ]
        ), html.Br(),
        dcc.Markdown(
            '''
                This web app reports both current and past performance of product 
                solution KPIs.
                
                The overall performance of the product solution measured by conversion rate
                and bounce rate, can be few using the KPI button at the sidebar.
                
                Given that it is possible to rebook appointments depending on stage 
                of treatment, that is either preparation or actual treatement; the KPI 
                has also been disaggregated into new user and returning to capture such 
                
                dynamics. Such insights have been viewed by clicking of User type KPI 
                from the sidebar.
                
                Definition of KPIs
                
                __Conversion rate__: Conversion rate is defined as the number of 
                                    positive patients who actually use link to book 
                                    appointment divided by total number of positive 
                                    patients who  who access the online booking platform 
                                    and the result multiply by 100. Conversion is said 
                                    to have occurred when a positive patient who receives the link, 
                                    access the platform and actually makes an appointment. 
                
                __Bounce rate__: Bounce rate is the rate at which patients click and 
                                access the booking platform but immediately leave 
                                without booking a doctor appointment. Bounce indicates 
                                single page view without conversion and this KPI should 
                                be monitored to keep it to the minimum possible.
                
                __Number of Returning user__: Returning user is a positive patient who 
                                            has previously access the booking platform. 
                                            A higher returning user rate potentially 
                                            results in previous bounce translating into 
                                            conversion or repeated conversions 
                                            (booking another doctor appointment).
                                            
                __Number of New user__: A new user is regarded as a patient who has not 
                                        previously used the booking platform. Generally, 
                                        an increasing number of new users implies 
                                        that the product solution (booking platform) is gaining traction 
                                        and popularity among patients hence digitization 
                                        and marketing efforts are paying off. 
                                        More relevantly, conversion by 
                                        new users will capture increasing doctors’ 
                                        clients and revenue.                
                Click to expand the sidebar and visualize the results.

            '''
        )
    ]
)





