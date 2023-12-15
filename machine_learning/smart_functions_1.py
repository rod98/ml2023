import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
import numpy as np
from typing import Tuple, Dict, List
import random
from pmdarima import auto_arima

import random

seed: int = 322

random.seed(seed)
np.random.seed(seed)

def prepare_data(input_data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    data = input_data.copy()

    data.reset_index(drop=True, inplace=True)
    data = data.dropna(subset=['sellingprice'])

    columns_to_drop = ['vin', 'saledate', 'state']
    for col in columns_to_drop:
        data.drop(col, axis=1, inplace=True)

    numeric_cols_fill = ['condition','odometer','mmr']
    for col in numeric_cols_fill:
        data[col].fillna(data[col].mean(), inplace=True)

    categorical_cols_fill = ['make', 'model', 'trim', 'body', 'transmission', 'color', 'interior', 'seller']
    for col in categorical_cols_fill:
        data[col].fillna(data[col].mode()[0], inplace=True)


    label_encoder = LabelEncoder()
    categorical_cols_label_encode = categorical_cols_fill.copy() + ['year']
    for col in categorical_cols_label_encode:
        data[col] = label_encoder.fit_transform(data[col])

    selling_price = data['sellingprice']

    data = data.drop('sellingprice', axis=1)

    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(data)

    res_data = pd.DataFrame(scaled_features, index=data.index, columns=data.columns)
    res_data['sellingprice'] = selling_price
    return res_data

def show_similar_and_more_profitable(df: pd.DataFrame, given_index: int, offers_count: int = 5) -> List[int]:
    task_df = df.copy()

    # considered row
    row = task_df.iloc[[given_index]]

    task_df.drop(df.index[[given_index]], inplace=True)

    df_x = task_df.drop('sellingprice', axis=1)
    row_x = row.drop('sellingprice', axis=1)
    # calculate the euclidean distance without sellingprice
    task_df['distance'] = np.linalg.norm(df_x.values - row_x.values, axis=1)

    # Sort by distance (ascending order) and profitability (descending order)
    df_sorted = task_df.sort_values(by=['distance', 'sellingprice'], ascending=[True, False])

    selected_row_price = row['sellingprice'].values[0]

    #print('df_sorted:\n', df_sorted)
    
    top_similar_and_profitable = df_sorted[df_sorted['sellingprice'] < selected_row_price].head(offers_count)

    #print('top_similar_and_profitable:\n', top_similar_and_profitable)

    return top_similar_and_profitable.index.values.tolist()


def generate_timeseries_patterns() -> Dict[str, np.array]:
    limit: int = 200

    def get_diffs(path: str, value_col: str) -> np.array:
        df = pd.read_csv(path)
        values =  df[value_col][:limit].to_numpy()
        return np.diff(values)
    
    patterns = {
        'birth': get_diffs('data/births.csv', 'Births'),
        'daily-min-temp': get_diffs('data/daily-min-temperatures.csv', 'Temp'),
        'monthly-juice-prod': get_diffs('data/monthly-juice-production-in-austr.csv', 'Monthly juice production'),
        'monthly-mean-temp.csv': get_diffs('data/monthly-mean-temp.csv', 'Temperature'),
        'sunspots': get_diffs('data/sunspots.csv', 'Sunspots'),
    }

    return patterns


def assign_history(data: pd.DataFrame) -> Dict[int, List[float]]:
    history = dict()

    patterns = generate_timeseries_patterns()
    users_count = data.shape[0]
    for id in range(users_count):
        pattern = random.choice(list(patterns.values()))
        history[id] = pattern.tolist()
    return history


def generate_history_for_car(data: pd.DataFrame, history: Dict[int, List[float]], car_id: int, scale: float) -> List[int]:
    car_info = data.iloc[[car_id]]
    car_price = car_info['sellingprice'].values[0]
    car_price_hist = [car_price]
    for el in history[car_id]:
        car_price_hist.append(round(car_price_hist[-1] + el * scale))
    return car_price_hist


# returns the car price in a next month
def forecast(car_price_history: List[int]) -> int:
    model = auto_arima(car_price_history, suppress_warnings=True)
    return round(model.predict(n_periods=1)[0])