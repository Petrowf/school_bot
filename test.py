import openai
from dotenv import load_dotenv
import os
load_dotenv()
openai.api_key = os.getenv('OPENAI')
# Установка параметров прокси-сервера
proxy = {
    "http": "http://188.114.96.6"

}
# Установка API-ключа
openai.api_key = "<ваш API-ключ>"
# Создание запроса с использованием прокси
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Who won the world series in 2020?"},
        {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
        {"role": "user", "content": "Where was it played?"}
    ],
    proxy=proxy
)
# Обработка ответа
print(response.choices[0].message.content)
