
#%%
from utils import predict_booked_days
from helper_components import get_data_path
from joblib import load

model_path = get_data_path(folder_name='model_store', file_name='best_model.model')

model = load(filename=model_path)

predict_booked_days(device_class='desktop', city='Berlin', 
                    country='DE', instant_booking='Not_instant', 
                    user_verified='Verified', num_sessions=2,
                    model = model
                )
# %%
