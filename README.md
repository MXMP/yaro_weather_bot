# Telegram-бот "Погода в Ярославле"

## Описание

Боту доступен прогноз погоды на 15 дней вперед. Пользователь пишет ему сообщение с датой
в формате `dd.mm.yyyy` (другие форматы не поддерживаются) и если дата правильная, то бот
отвечает сообщением с кратким прогнозом. В прогнозе присутствуют данные: температура,
влажность, давление и вероятность осадков. 

## Запуск проекта

```
git clone https://github.com/MXMP/yaro_weather_bot.git
cd yaro_weather_bot
pip install -r requirements.txt
export TG_API_KEY=<api ключ вашего бота>
python bot.py
```