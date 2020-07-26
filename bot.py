import requests
import logging
from datetime import date, datetime
import os

from telegram.ext import Updater, MessageHandler, CommandHandler, Filters


WEATHER_API_KEY = 'pbVFUZSS0EPziOMbZrnBEdYQLA0DUN38'
WEATHER_API_URL = 'https://api.climacell.co/v3/weather/forecast/daily'


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def get_min_and_max_values(metric_name, weather_json):
    """
    Возвращает минимальное и максимальное значение для метрики `metric_name` из объекта с прогнозом на один день.

    :param metric_name: имя метрики для поиска, например 'temp'
    :param weather_json: объект с прогнозом на один день
    :return: словарь с ключами 'min' и 'max'
    """

    for metric_data in weather_json[metric_name]:
        try:
            min_value = metric_data['min']['value']
        except KeyError:
            pass

        try:
            max_value = metric_data['max']['value']
        except KeyError:
            pass

    try:
        return {'min': min_value, 'max': max_value}
    except UnboundLocalError:
        raise KeyError(f"Could't find min or max value for {metric_name}")


def json_weather_to_human_string(weather_json):
    """
    Превращает JSON с прогнозом погоды в человекочитаемое сообщение.

    :param weather_json: JSON c прогнозом погоды на один день
    :return: строка с человекочитаемым прогнозом
    """

    temperature = get_min_and_max_values('temp', weather_json)
    temp_str = f"Температура: от {temperature['min']} до {temperature['max']}°C"
    precipitation_probability_str = f"Вероятность осадков: {weather_json['precipitation_probability']['value']}%"
    pressure = get_min_and_max_values('baro_pressure', weather_json)
    pressure_str = f"Атмосферное давление: от {pressure['min']} до {pressure['max']} мм рт. ст."
    humidity = get_min_and_max_values('humidity', weather_json)
    humidity_str = f"Влажность: от {humidity['min']} до {humidity['max']}%"
    return f"Погода на {weather_json['observation_time']['value']}\n{temp_str}\n{precipitation_probability_str}\n" \
           f"{pressure_str}\n{humidity_str}"


def get_weather_from_api(forecast_date):
    """
    Запрашивает прогноз погоды по API на дату `forecast_date`. В ответе будет объект из JSON, который верунлся от API.
    Если запрос делается на прошедшую дату или более чем 15 дней вперед, то будет выкинуто ValueError.

    :param forecast_date: дата, на которую нужен прогноз
    :return: JSON с прогнозом на нужный день
    """

    # Проверяем, что запрос поступил на правильную дату
    dates_diff = (forecast_date.date() - date.today()).days
    if dates_diff < 0 or dates_diff > 14:
        raise ValueError(f"Wrong date. Forecast a   vailable only for 15 days.")

    querystring = {"lat": "57.626559",
                   "lon": "39.893804",
                   "unit_system": "si",
                   "start_time": "now",
                   "fields": "temp,humidity,baro_pressure:mmHg,precipitation_probability",
                   "apikey": WEATHER_API_KEY}
    response = requests.request("GET", WEATHER_API_URL, params=querystring)
    return response.json()[dates_diff]


def start(update, context):
    """
    Обработка команды /start от пользователя. Отвечает пользователю приветственным сообщением.
    """

    update.message.reply_text(f'👋 Привет!\nЯ показываю прогноз погоды в Ярославле на нужную дату'
                              f' (в переделах 15 дней).\nПиши мне дату в обычном формате "день.месяц.год" (например:'
                              f' 20.08.2020) и я пришлю тебе прогноз.')


def forecast_request(update, context):
    """
    Обработка запроса прогноза погоды. Проверяет, что запрошена дата в правильном формате, делает запрос к API и
    отвечает пользователю человеческим сообщением с описанием погоды.
    """

    try:
        requested_date = datetime.strptime(f'{update.message.text} 00:00:00', '%d.%m.%Y %H:%M:%S')
    except ValueError:
        update.message.reply_text(f'Вы написали дату в неправильном формате.')
    else:
        try:
            update.message.reply_text(json_weather_to_human_string(get_weather_from_api(requested_date)))
        except ValueError:
            update.message.reply_text(f'Прогноз погоды доступен только на 15 дней вперед.')
        except requests.exceptions.RequestException:
            update.message.reply_text(f'Сервер с прогнозами недоступен, попробуйте пожалуйста позже.')
        except:
            update.message.reply_text(f'Что-то пошло не так при составлении прогноза, попробуйте пожалуйста позже.')


def main():
    try:
        updater = Updater(os.environ['TG_API_KEY'], use_context=True)
    except KeyError:
        print("Can't find TG_API_KEY environment variable.")
        exit(1)
    else:
        dispatcher = updater.dispatcher

        dispatcher.add_handler(CommandHandler('start', start))
        dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), forecast_request))

        updater.start_polling()
        updater.idle()


if __name__ == '__main__':
    main()
