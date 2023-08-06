#%%
import requests
import json
from typing import List
import pandas as pd

def request_prediction(URL: str, data: dict) -> int:
    """
    This function accepts

    Parameters
    ----------
    URL : str
        The API link.
    data : dict
        input data to be used for prediction.

    Returns
    -------
    int
        prediction.

    """
    req = requests.post(url=URL, json=data)
    response = req.content
    prediction = json.loads(response)['predicted_value'][0]
    return prediction


def predict_booked_days(device_class, city, country, 
                            instant_booking, user_verified,
                            num_sessions, model):
        in_data = {'num_sessions': num_sessions, 'city': city, 'country': country,
                    'device_class': device_class, 'instant_booking': instant_booking,
                    'user_verified': user_verified
                    }
        
        prediction_input_data = pd.DataFrame(data=in_data, index=[0])
        y_pred = model.predict(prediction_input_data)
        return y_pred
    
    
def request_booked_days_prediction(in_data: dict, URL: str):
    req = requests.post(url=URL, json=in_data)
    response = req.content
    prediction = json.loads(response)['predicted_value'][0]
    return prediction

