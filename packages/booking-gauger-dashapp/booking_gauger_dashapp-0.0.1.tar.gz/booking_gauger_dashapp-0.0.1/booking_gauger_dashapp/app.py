#%%
from dash import html, Input, Output, State, dcc
import dash
import dash_bootstrap_components as dbc
import pandas as pd
import requests
import json
from dash.exceptions import PreventUpdate
from .helper_components import get_data_path, nonselection_message
from .style import input_style
from .predictions_ui import prediction_layout
from joblib import load

from .utils import request_booked_days_prediction, predict_booked_days

#%%
#from constant import HOST, PORT, ENDPOINT

#URL = f'{HOST}:{PORT}{ENDPOINT}'

#%%
data_path = get_data_path(folder_name='booking_gauger_dashapp/data', file_name='data_used.csv')
data = pd.read_csv(data_path)

model_path = get_data_path(folder_name='booking_gauger_dashapp/model_store', file_name='best_model.model')

model = load(filename=model_path)
#%%
app = dash.Dash(__name__, external_stylesheets=[
                                                dbc.themes.SOLAR,
                                                dbc.icons.BOOTSTRAP,
                                                dbc.icons.FONT_AWESOME,
                                            ]
                )

app.layout = prediction_layout

app.validation_layout = [prediction_layout]

##################### backend ##############################

@app.callback(Output(component_id='project_canvans', component_property='is_open'),
              Input(component_id='proj_desc', component_property='n_clicks'),
              State(component_id='project_canvans', component_property='is_open')
              )
def toggle_project_description(proj_desc_button_clicked: str, is_open: bool) -> bool:
    """
    This function accepts click event input and the state of canvas component,
    and change the state of the canvans component when a click occurs

    Parameters
    ----------
    proj_desc_button_clicked : str
        This parameter is a count of each click made on a button.
    is_open : bool
        Has the values True or False that specifies whether the canvas component is opened or not.

    Returns
    -------
    bool
        Has values True or False that determines whether the canvans component should be open.
    """
    if proj_desc_button_clicked:
        return not is_open
    else:
        return is_open



@app.callback(Output(component_id='desc_popup', component_property='children'),
              Output(component_id='missing_para_popup', component_property='is_open'),
              Output(component_id='prediction_output', component_property='children'),
              Input(component_id='submit_parameters', component_property='n_clicks'),
              Input(component_id='session', component_property='value'),
              Input(component_id='city', component_property='value'),
              Input(component_id='user_verified', component_property='value'),
              Input(component_id='device', component_property='value'),
              Input(component_id='instant_book', component_property='value'))

def make_prediction_request(submit_button: int, session: int, city_selected: str, user_verified_selected: str,
                            device_selected: str, instant_booking_selected: str, 
                            prediction_method: str = 'stored_model',
                            prediction_api_endpoint: str = None
                            ):
    """
    This function accepts various input data selected, makes a request to a machine learning API
    and returns prediction

    Parameters
    ----------
    submit_button : int
        Number of times the submit button has been clicked.
    session : int
        This describes the number of sessions a customer made on the booking site..
    city_selected : str
        This is the city from which a customer is accessing the booking site from
    user_verified_selected : str
        Whether or not a customer who visited the site has been verified.
    device_selected : str
        This is the type of device used to access the booking site.
    instant_booking_selected : str
        The is a feature on a booking site and value is whether or not this feature was used by a customer.
    prediction_method: str ('stored_model | 'api')
                    Specifies the process for making the prediction with values being either 'stored_model',
                    or 'api'. For the stored_model, a model that was stored with the app is retrieved and used
                    for prediction while 'api' makes request to an ML API for the purpose. Using the 'api' 
                    with make sure the latest updates made to the ML model used for the prediction while the 
                    'stored_model' mayy not be the best model if it has not been manually changed in the app.
    prediction_api_endpoint: str
            The endpoint of the ML API when prediction_method is specified to be api
        

    Returns
    -------
    desc_popup: str
        This is a message in a popup component that indicates corrections to be made before submitting API request.
    missing_para_popup: bool
        This is an output component that opens when selection is not made
        for all parameters before clicking submit buttion.
    prediction_output
        This is an output component where prediction is displayed.

    """
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if not submit_button:
        raise PreventUpdate

    if button_id == 'submit_parameters':
        if ((not session) or (not city_selected) or (not user_verified_selected)
            or (not device_selected) or (not instant_booking_selected)):
            return nonselection_message, True, dash.no_update
        
        country_selected = data[data['city']==city_selected]['country'].unique().tolist()[0]
        if prediction_method == 'stored_model':
            prediction = predict_booked_days(device_class=device_selected, city=city_selected, 
                                            country=country_selected, instant_booking=instant_booking_selected,
                                            user_verified=user_verified_selected, num_sessions=session,
                                            model=model
                                            )
            prediction = prediction.item()
        elif prediction_method == 'api':
            in_data = {'num_sessions': session,
                        'city': city_selected,
                        'country': country_selected,
                        'device_class': device_selected,
                        'instant_booking': instant_booking_selected,
                        'user_verified': user_verified_selected
                    }
            prediction = request_booked_days_prediction(in_data=in_data, URL=prediction_api_endpoint)

        if prediction > 1:
            return dash.no_update, False,  f'{round(prediction)} day(s)'
        else:
            return dash.no_update, False, f'{round(prediction)} day'


app.run_server(port='4048', host='0.0.0.0', debug=False, use_reloader=False)
