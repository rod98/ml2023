import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_squared_error
from gigachat import GigaChat


def add_column_to_dataframe(input_data):
    text1 = "Продается Kia Sorento LX года выпуска. Автомобиль оснащен автоматической коробкой передач и имеет пробег 16639.0 миль. VIN: 5xyktca69fg566472. Цвет кузова - белый, цвет салона - черный. Оценка состояния авто (город/шоссе): 5.0. Продавец: Kia Motors America, Inc. Цена: $20500-$21500. Местонахождение: Калифорния, CA. Дата выпуска: Tue Dec 16 2014 12:30:00 GMT-0800 (PST). Дополнительные фотографии и информация доступны по запросу. Свяжитесь для получения более подробной информации."
    text2 = "Продаю автомобиль Kia Sorento LX 2015 года выпуска. Это прекрасный внедорожник с автоматической коробкой передач. VIN-номер авто: 5xyktca69fg561319. Автомобиль в отличном состоянии, пробег составляет 9,393 миль. Кузов окрашен в белый цвет, внутренняя отделка выполнена в бежевом цвете. Производитель - Kia Motors America, Inc. Заинтересованным лицам предлагается купить этот автомобиль по цене 21,500 долларов. Дата и время публикации объявления: Вт, 16 декабря 2014 года, 12:30:00 GMT-0800 (PST). Если у вас есть вопросы или вы хотите организовать просмотр, пожалуйста, свяжитесь со мной по указанному номеру телефона."
    text3 = "Продаю BMW 3 Series 328i SULEV Sedan. Автоматическая коробка передач, пробег 4.5 тыс. миль. Цвет кузова серый, салон черный. Автомобиль в идеальном состоянии. Выпущен в кредитной компании financial services remarketing (lease). Цена: $31,900. Торг возможен. Дата публикации объявления: Thu Jan 15 2015 04:30:00 GMT-0800 (PST). Для получения дополнительной информации позвоните по номеру: 30000."
    text4 = "Продаётся автомобиль Volvo S60 T5 седан 2015 года выпуска. Автоматическая коробка передач, VIN: yv1612tb4f1310987, пробег 14282.0 миль, белого цвета с черным интерьером. Автомобиль находится в отличном состоянии, был использован в лизинговых финансовых услугах. Цена продажи составляет $27500. Дата и время продажи: Thu Jan 29 2015 04:30:00 GMT-0800 (PST)."
    column_data = [text1, text2, text3, text4] + [''] * (558811 - 4)
    input_data.insert(16, 'announcement', column_data, True)
    return input_data


def prepare_data2(input_data):
    data = input_data.copy()

    data = add_column_to_dataframe(data)

    data.reset_index(drop=True, inplace=True)
    data = data.dropna(subset=['sellingprice'])

    columns_to_drop = ['vin', 'saledate', 'state', 'announcement']
    for col in columns_to_drop:
        data.drop(col, axis=1, inplace=True)

    numeric_cols_fill = ['condition','odometer','mmr']
    for col in numeric_cols_fill:
        data[col].fillna(data[col].mean(), inplace=True)

    categorical_cols_fill = ['make', 'model', 'trim', 'body', 'transmission', 'color', 'interior', 'seller']
    for col in categorical_cols_fill:
        data[col].fillna(data[col].mode()[0], inplace=True)

    label_encoder = dict()
    categorical_cols_label_encode = categorical_cols_fill.copy() + ['year']
    for col in categorical_cols_label_encode:
        label_encoder[col] = LabelEncoder()
        data[col] = label_encoder[col].fit_transform(data[col])

    selling_price = data['sellingprice']

    data = data.drop('sellingprice', axis=1)

    res_data = pd.DataFrame(data, index=data.index, columns=data.columns)
    res_data['sellingprice'] = selling_price
    return res_data


def important_features(prepared_data):
    cur_data = prepared_data.copy()

    model = RandomForestRegressor(random_state=42)
    columns_to_drop = ['sellingprice', 'mmr']
    x = cur_data.drop(columns=columns_to_drop)
    y = cur_data['sellingprice']
    model.fit(x, y)

    feature_importances = model.feature_importances_

    importance = pd.DataFrame({
        'Feature': x.columns,
        'Importance': feature_importances
    })

    importance_df = importance.sort_values(by='Importance', ascending=False)

    # Топ 10
    top_features = importance_df.head(10)

    plt.figure(figsize=(10, 6))
    plt.barh(top_features['Feature'], top_features['Importance'], color='skyblue')
    plt.xlabel('Importance')
    plt.title('Top 10 Important Features for Car Price Prediction')
    plt.gca().invert_yaxis()
    plt.show()

    return importance, top_features['Feature']


def predict_car_price(prepared_data, label_encoder, car_info):
    # car_info = {'year': 2015, 'make': 'Toyota', 'model': 'Camry', 'trim': 'LE', 'body': 'Sedan', 'transmission': 'automatic', 'condition': 4.5,	'odometer': 50000, 'color': 'blue', 'interior': 'black', 'seller': 'kia motors america, inc'}
    cur_data = prepared_data.copy()

    model = RandomForestRegressor(random_state=42)
    columns_to_drop = ['sellingprice', 'mmr']
    x = cur_data.drop(columns=columns_to_drop)
    y = cur_data['sellingprice']
    model.fit(x, y)

    car_info_encoded = []
    for info in car_info.keys():
        if info in label_encoder.keys():
            car_info_encoded.append(label_encoder[info].transform([car_info[info]])[0])
        else:
            car_info_encoded.append(car_info[info])

    car_info_encoded = pd.DataFrame([car_info_encoded], columns=x.columns)
    predicted_price = model.predict(car_info_encoded)

    return predicted_price[0]


def calculate_fair_price(label_encoder, weights, car_info):
    car_info_encoded = []
    for info in car_info.keys():
        if info in label_encoder.keys():
            car_info_encoded.append(label_encoder[info].transform([car_info[info]])[0])
        else:
            car_info_encoded.append(car_info[info])
    fair_price = 0
    for i in range(len(car_info)):
        fair_price += car_info_encoded[i] / weights['Importance'][i]
    return fair_price / 100 * 4


def calculate_fair_price_indx(data, weights, indx):
    fair_price = 0
    for i in range(len(weights['Feature'])):
        print(weights['Feature'][i])
        fair_price += data.iloc[[indx]][weights['Feature'][i]] / weights['Importance'][i]
    return fair_price / 100 * 4


def write_advertisement(car_info, price):
    car_info_str = ", ".join(i + ": " + str(car_info[i]) for i in car_info.keys())
    car_info_str = car_info_str + ", price:" + str(price)

    with GigaChat(credentials='',
                  verify_ssl_certs=False) as giga:
        querty_text = "Составь текст объявления о продаже авто, используя следующие данные об авто: " + car_info_str
        response = giga.chat(querty_text)
        
    return response.choices[0].message.content


def write_advertisement_indx(prepared_data, indx, price):
    column = prepared_data.columns.values
    car_info_str = ", ".join(i + ": " + str(prepared_data.iloc[[indx]][i]) for i in column)
    car_info_str = car_info_str + ", price:" + str(price)

    with GigaChat(credentials='',
                  verify_ssl_certs=False) as giga:
        querty_text = "Составь текст объявления о продаже авто, используя следующие данные об авто: " + car_info_str
        response = giga.chat(querty_text)
        
    return response.choices[0].message.content

    

