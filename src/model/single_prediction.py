import pickle as pk
import pandas as pd
from data import feature_engineering


class Model:
    def __init__(self, model_path, cities_data, product_attributes):
        with open(model_path, 'rb') as f:
            self.model = pk.load(f) 
        self.cities_data = cities_data
        self.product_data = product_attributes
    
    def make_prediction(self, order_data):
        df = pd.DataFrame(order_data)
        df = feature_engineering.engineer_features(df, self.cities_data, self.product_data)

        return self.model.predict_proba(df)[0][1]