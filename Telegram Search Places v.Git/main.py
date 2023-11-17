import telebot
from telebot import types
from tokenn import TOKEN
from geopy.geocoders import Nominatim
import requests

bot = telebot.TeleBot(TOKEN) 

def search_places(types,location):
    global name, address, places_text

    institution = types
    town = city
    geolocator = Nominatim(user_agent="myGeocoder")
    town = geolocator.geocode(town)
    osm_url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": f"{institution} {town}",
        "format": "json",
        "lat": location.latitude,
        "lon": location.longitude,
    }
    response = requests.get(osm_url, params=params)
    if response.status_code == 200:
        data = response.json()
        places_text = ""
        for place in data:
            name = place.get('name')
            address = place.get('display_name')
            places_text += f'Name: {name} \nAddress: {address}\n\n'
@bot.message_handler(commands=['start'])
def welcome_screen(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    get_location = types.KeyboardButton('🌎 Give us your location', request_location=True)
    why = types.KeyboardButton('❓ Why do you need my location?')
    markup.add(get_location, why)
    bot.send_message(message.chat.id, 'Hello dude, I can help you to find anything in your city!', reply_markup=markup)

@bot.message_handler(content_types=['location'])
def get_location(message):
    global location
    if message.location is not None:
        location = message.location

        def get_city(location):
            global city
            osm_reverse_geocoding_url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={location.latitude}&lon={location.longitude}"
            response = requests.get(osm_reverse_geocoding_url)
            if response.status_code == 200:
                data = response.json()
                city = data.get('address', {}).get('city')
        get_city(location)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        establishments = types.KeyboardButton('🗺️ Establishments of your city')
        give_again_location = types.KeyboardButton('🌎 Re-provide the location', request_location=True)
        markup.add(establishments, give_again_location)
        bot.send_message(message.chat.id, f'Location is connected ✅ \nYour city is: {city}', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Location was not provided. Please provide your location.')

@bot.message_handler(content_types=['text'])
def global_logic(message):
    if message.chat.type == 'private':
        if message.text == '❓ Why do you need my location?':
            bot.send_message(message.chat.id, 'I need your location so you dont write the city name, it will make the code easier and you wont have to choose a city from thousands or type it')
        if message.text == 'Location is connected ✅':
            bot.send_message(message.chat.id, 'I dont need your location, if you wanna re-provide the location, press "🌎 Re-provide the location"')
        if message.text == '🗺️ Establishments of your city':
            establishments = types.ReplyKeyboardMarkup(resize_keyboard=True)
            caffee = types.KeyboardButton('☕ Coffee')
            supermarket = types.KeyboardButton('🧺 Supermarket')
            establishments.add(caffee, supermarket)
            bot.send_message(message.chat.id, 'Now choose one of more establishments what do you need?', reply_markup=establishments)
        if message.text == '☕ Coffee':
            bot.send_message(message.chat.id, '🔍 Searching...')
            search_places('coffee',location)
            bot.send_message(message.chat.id, places_text)
        if message.text == '🧺 Supermarket':
            bot.send_message(message.chat.id, '🔍 Searching...')
            search_places('supermarket',location)
            bot.send_message(message.chat.id, places_text)
             
print('Telegram bot is started')
bot.polling(none_stop=True)