from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
from .helper_components import output_card, create_offcanvans, get_data_path, create_dropdown_with_label
from .style import input_style


#%%
data_path = get_data_path(folder_name='booking_gauger_dashapp/data', file_name='data_used.csv')
data = pd.read_csv(data_path)


prediction_layout = html.Div([dbc.Row([html.Br(), html.Br(),
                                        dbc.Col(dbc.Button('Project description',
                                                        id='proj_desc',
                                                        n_clicks=0
                                                        )
                                            ),
                                        dbc.Col(children=[html.Div(children=[create_offcanvans(id='project_canvans',
                                                                                    title='BookingGauger',
                                                                                    is_open=False
                                                                                    )
                                                                            ]
                                                                ),
                                                        ]
                                                )
                                    ]),
                                dbc.Label("Select characteristics of online visitor to predict the number of accommodation days to be booked"),
                                html.Br(), html.Br(),
                                dbc.Row([dbc.Col(lg=4,children=[dbc.Label('Number of session',style=input_style),
                                                            html.Br(),
                                                            dcc.Input(id='session',
                                                                    placeholder='Number of sessions by site visitor',
                                                                    min=1, max=11, type='number',
                                                                    debounce=True
                                                                )
                                                        ]
                                                ),
                                        create_dropdown_with_label(label='City', placeholder='city from which client visited the platform',
                                                                    dropdown_id='city', values_data=data['city']
                                                                    ),
                                        create_dropdown_with_label(label='User verification status', dropdown_id='user_verified', 
                                                                placeholder='Is the visitor verified on platform', 
                                                                values_data=data['user_verified']
                                                                ),
                                        ]
                                        ),
                                html.Br(), html.Br(),

                                dbc.Row([create_dropdown_with_label(label='Device type', dropdown_id='device', 
                                                                    placeholder='type of device used to access platform',
                                                                    values_data=data['device_class']
                                                                    ),
                                        create_dropdown_with_label(label='Instant booking feature used?',dropdown_id='instant_book',
                                                                    placeholder='Whether visitor used instant booking feature', 
                                                                    values_data=data['instant_booking']
                                                                    ),
                                        dbc.Col([
                                            #html.Br(),
                                            dbc.Label(''),
                                            dbc.Button(id='submit_parameters',
                                                            children='Predict booking days'
                                                            )
                                                ]
                                                )
                                        ]
                                        ),
                                html.Br(), html.Br(),
                                dbc.Row([dbc.Col(id='prediction',
                                                children=[
                                                    html.Div(id="prediction_div",
                                                            children=[output_card(id="prediction_output",
                                                                                    card_label="Prediction"
                                                                                    )
                                                                        ]
                                                            )
                                                ]
                                                ),
                                        dbc.Col([
                                            dbc.Modal(id='missing_para_popup', is_open=False,
                                                children=[
                                                dbc.ModalBody(id='desc_popup')
                                            ])
                                        ]
                                                )
                                        ]
                                        )
                            ])








