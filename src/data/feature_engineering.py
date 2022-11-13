import numpy as np
import pandas as pd
from haversine import haversine


def engineer_features(orders_data: pd.DataFrame, cities_data: pd.DataFrame, product_data: pd.DataFrame, training_data=False):
    """Feature engineering pipeline both for training and prediction."""

    # City coordinate extraction

    cities_data1 = cities_data[['city_from_name', 'city_from_coord']]
    cities_data2 = cities_data[['city_to_name', 'city_to_coord']]
    cities_data1 = cities_data1.rename(columns={'city_from_name': 'city_name', 'city_from_coord': 'city_coord'})
    cities_data2 = cities_data2.rename(columns={'city_to_name': 'city_name', 'city_to_coord': 'city_coord'})

    cities_data = pd.concat([cities_data1, cities_data2]).drop_duplicates().set_index('city_name')

    # Transform lat long tuple as string to two columns
    cities_data['lat'] = cities_data['city_coord'].apply(lambda x: float(x[1:-1].split(',')[0]))
    cities_data['long'] = cities_data['city_coord'].apply(lambda x: float(x[1:-1].split(',')[1]))
    cities_data = cities_data.drop(columns=['city_coord'])

    ### Feature engineering
    # - Lat long for all three locations attributes
    # - Distance on water
    # - Distance on land
    # - Distance on land **log**
    # - Distance on land **sqr**
    # - Units
    # - Units **log**
    # - Units **sqr**
    # - Third party **ONH**
    # - Customs **ONH**
    # - Material handling **ONH**
    # - Weight
    # - Weight **log**
    # - Weight **sqr**
    # - Weight percent deviation from mean

    # Replace ATHENAS with Athens and BCN with Barcelona in the origin_port column
    orders_data['origin_port'] = orders_data['origin_port'].replace('ATHENAS', 'Athens')
    orders_data['origin_port'] = orders_data['origin_port'].replace('BCN', 'Barcelona')

    # Order coordinate mapping

    # Filter only for those extracted columns
    city_lat_longs = cities_data[['lat', 'long']].drop_duplicates()

    # Add to order df
    orders_data = orders_data.join(city_lat_longs.rename(columns={'lat': 'start_lat', 'long': 'start_long'}), on='origin_port')
    orders_data = orders_data.join(city_lat_longs.rename(columns={'lat': 'hub_lat', 'long': 'hub_long'}), on='logistic_hub')
    orders_data = orders_data.join(city_lat_longs.rename(columns={'lat': 'end_lat', 'long': 'end_long'}), on='customer')

    orders_data.loc[orders_data['logistic_hub'].isna(), 'hub_lat'] = orders_data.loc[orders_data['logistic_hub'].isna(), 'start_lat']
    orders_data.loc[orders_data['logistic_hub'].isna(), 'hub_long'] = orders_data.loc[orders_data['logistic_hub'].isna(), 'start_long']

    # Shippment distance calculations

    # Calculate distances
    orders_data['distance_on_water'] = orders_data.apply(lambda x: haversine((x['start_lat'], x['start_long']), (x['hub_lat'], x['hub_long'])), axis=1)
    orders_data['distance_on_land'] = orders_data.apply(lambda x: haversine((x['hub_lat'], x['hub_long']), (x['end_lat'], x['end_long'])), axis=1)

    # Handle no hub orders
    # if hub == nan then replace sea_distance with 0
    orders_data['distance_on_water'] = orders_data['distance_on_water'].fillna(0)
    orders_data.loc[orders_data['logistic_hub'].isna(), 'distance_on_land'] = orders_data.loc[orders_data['logistic_hub'].isna()].apply(lambda x: haversine((x['start_lat'], x['start_long']), (x['end_lat'], x['end_long'])), axis=1)

    # Log version of distance on land
    orders_data['distance_on_land_log'] = orders_data['distance_on_land'].apply(lambda x: np.log(x))

    # No distance on land err handling
    orders_data.loc[orders_data['distance_on_land'] == 0, 'distance_on_land_log'] = 0

    # Add distance on land squared
    orders_data['distance_on_land_squared'] = orders_data['distance_on_land'] ** 2

    # Order product volume

    # Log version of units of order
    orders_data['units_log'] = orders_data['units'].apply(lambda x: np.log(x))

    # Units squared
    orders_data['units_squared'] = orders_data['units'] ** 2

    # Product weight information and material handling

    # Join product data
    orders_data = orders_data.join(product_data, on='product_id')

    # Log version of product weight
    orders_data['weight_log'] = orders_data['weight'].apply(lambda x: np.log(x))

    # Add squared version of weight and units
    orders_data['weight_squared'] = orders_data['weight'] ** 2

    # Relative deviation from mean weight
    orders_data['weight_deviation'] = (orders_data['weight'] - orders_data['weight'].mean()).abs()

    # Convert material handling class as int to string class
    orders_data['material_handling'] = orders_data['material_handling'].apply(lambda x: "c" + str(float(x)))

    # Missing product info att
    orders_data['missing_product_info'] = orders_data['weight'].isna()

    orders_data = orders_data.fillna(0)

    # One-hot encoding 

    if training_data:
        orders_target = orders_data['late_order'] * 1
        orders_data = orders_data.drop(columns=['late_order'])

    orders_features = orders_data.drop(columns=['origin_port', 'logistic_hub', 'customer', 'product_id'])
    orders_features = pd.get_dummies(orders_features)

    # Ensure that all columns are present
    columns_to_check = [
        '3pl_v_001',
        '3pl_v_002',
        '3pl_v_003',
        '3pl_v_004',
        'customs_procedures_CRF',
        'customs_procedures_DTD',
        'customs_procedures_DTP',
        'material_handling_c0.0',
        'material_handling_c1.0',
        'material_handling_c2.0',
        'material_handling_c3.0',
        'material_handling_c4.0',
        'material_handling_c5.0',
        'material_handling_cnan',
    ]
    for col in columns_to_check:
        if col not in orders_features.columns:
            orders_features[col] = 0

    # Order columns
    orders_features = orders_features[['units', 'start_lat', 'start_long', 'hub_lat', 'hub_long', 'end_lat',
       'end_long', 'distance_on_water', 'distance_on_land',
       'distance_on_land_log', 'distance_on_land_squared', 'units_log',
       'units_squared', 'weight', 'weight_log', 'weight_squared',
       'weight_deviation', 'missing_product_info', '3pl_v_001', '3pl_v_002',
       '3pl_v_003', '3pl_v_004', 'customs_procedures_CRF',
       'customs_procedures_DTD', 'customs_procedures_DTP',
       'material_handling_c0.0', 'material_handling_c1.0',
       'material_handling_c2.0', 'material_handling_c3.0',
       'material_handling_c4.0', 'material_handling_c5.0',
       'material_handling_cnan']]

    if training_data:
        return orders_features, orders_target
    else:
        return orders_features