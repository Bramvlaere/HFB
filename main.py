import requests
import json
import datetime
import sched 
import telegram 
from telegram.ext import *
import asyncio
from telegram import Update
from telegram.ext import Updater, MessageHandler
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
#import declarativetables
import time
import logging


logging.basicConfig(level=logging.INFO)


#Base = declarative_base()

print('Bot started...')

# Telegram API token and chat ID
TOKEN = '6161655715:AAGEYTNiOq7GZmj6xIIC35lDDAmw05GcWxo'
bot = telegram.Bot(token=TOKEN)
no_hao=['OP1','OP2']
parking_needed=['OP2']

def main():
    msg_to_send=[]
    
    preset=read_settings()
    for type,setting in preset.items():
        if "." in type:
            continue
        results = {}
        print('---------------------------------')
        logging.info(f'Checking for {type} properties')
        print('---------------------------------')
        response=multi_api_call(setting, results)
        normalized_response=response_normalizer(results)
        if isinstance(normalized_response,str):
            message=f'No results found for {type} setting'
            msg_to_send.append(message)
            continue

        if len(normalized_response)==0:
            message=f'No new properties found for {type}'
            msg_to_send.append(message)
            continue
        
        c=0
        
        for adress,features in normalized_response.items():
            output={}
            if check_post_of_the_day(features):
                location=generate_google_maps([features['latitude'],features['longitude']])
                link=zillow_link_based_on_zid(features['zpid'])
                res=HAO_check(features['zpid'])
                features.update(res)
                if type in no_hao:
                    if features['HOA']!="No HOA or not available":
                        continue
                if type in parking_needed:
                    if features['parking']=="No parking or not available" or features['parking']=="No parking or not available":
                        continue
                message=f"Address: {adress}\nType: {type}\n{features['imgSrc']}\nProperty Type: {features['propertyType']}\nEstimate Value: {features['zestimate']}\nDays Listed: {features['daysOnZillow']}\nListing Price: {features['price']}\nBedrooms: {features['bedrooms']}\nRent Estimate: {features['rentZestimate']}\nBathrooms: {features['bathrooms']}\nHAO: {features['HOA']}\nParking: {features['parking']}\nLiving Area: {features['livingArea']} sqft\n {location}\n {link}"
                msg_to_send.append(message)
                output.update({adress:features})

            else :
                c+=1
                logging.info(f'{c} older than 24 hours')

        if c==len(normalized_response):
            message=f'No new {type} found for today'
            msg_to_send.append(message)
            continue
    
    #upload_dictionary(output)

    return msg_to_send,c


# def run_every_24_hours(scheduler, interval, action, actionargs=()):
#     # Your code here
#     main()
#     scheduler.enter(interval, 1, run_every_24_hours, (scheduler, interval, action, actionargs))

# s = sched.scheduler(time.time, time.sleep)
# s.enter(86400, 1, run_every_24_hours, (s, 86400, run_every_24_hours))
# s.run()

def HAO_check(id):
    time.sleep(1)
    response = prop_details(id)
    if not response:
        return
    response = response.text
    response = json.loads(response)
    
    HOA = response.get("monthlyHoaFee") or "No HOA or not available"
    #Hoafeature = response.get("hoaFee") or "No HOA or not available"
    parking = response.get("parking", {})
    parking_features = parking.get("parkingFeatures") or "No parking or not available"
    parking = parking.get("parking") or "No parking or not available"

    res = {"HOA": HOA, "parking": parking_features, "parking": parking}
    return res


def zillow_link_based_on_zid(zid):
    return f'https://www.zillow.com/homedetails/{zid}_zpid/'

# def upload_dictionary(response):
#     engine = create_engine('sqlite:///properties.db')
#     connection = engine.connect()
#     if not engine.dialect.has_table(connection, "properties"):
#         Base.metadata.create_all(engine)
#     Session = sessionmaker(bind=engine)
#     session = Session()
#     new_ones_found={}
#     for adress, features in response.items():
#         if session.query(declarativetables.Properties).filter_by(adress=features['address']).first() is None:
#         #     new_ones_found.update({adress:features})
#             record = declarativetables.Properties(adress=features['address'])
#             session.add(record)
#             session.commit()
        
#     session.close()
#     connection.close()
#     return new_ones_found


#function to load json as a dictionary
def load_json(json_file):
    with open(json_file) as f:
        data= json.load(f)
        return data

async def start_command(update, context):
    await update.message.reply_text('Type /update to get started!')

async def help_command(update, context):
    await update.message.reply_text('If you need help, please contact @vanlaere')

async def update_command(update, context):
    await update.message.reply_text('Looking for new properties...')
    try:
        res,c=main()
    except Exception as e:
        await update.message.reply_text(f'Error: {e} Please contact @vanlaere for help')
        return
    if c>0:
        await update.message.reply_text(f'Found {c} Properties that were not posted today')
    for message in res:
        await update.message.reply_text(message)


async def error(update, context):
    await print(f'Update {update} caused error {context.error}')

def prop_details(id):

    url = "https://zillow-com1.p.rapidapi.com/property"

    querystring = {"zpid":{id}}

    headers = {
        "X-RapidAPI-Key": "a3e8f2f73dmshc1ebdb25a44b0c3p1729c7jsn5b4457b1fe75",
        "X-RapidAPI-Host": "zillow-com1.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    return response

def generate_google_maps(coordinate):
    return f'https://www.google.com/maps/place/{coordinate[0]},{coordinate[1]}'


def read_settings():
    setting={}
    with open('config.json') as f:
        config=json.load(f)
        for x,y in config.items():
            for a,b in y.items():
                setting.update({a:b})

    return setting

def _api_call(query):
    url = "https://zillow-com1.p.rapidapi.com/propertyExtendedSearch"

    querystring = {"location":"New Jersy,","status_type":"ForSale","maxPrice":"500000"}

    headers = {
        "X-RapidAPI-Key": "a3e8f2f73dmshc1ebdb25a44b0c3p1729c7jsn5b4457b1fe75",
        "X-RapidAPI-Host": "zillow-com1.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    return response.text

def api_call(query):
    url = "https://zillow-com1.p.rapidapi.com/propertyExtendedSearch"
    headers = {
        "X-RapidAPI-Key": "a3e8f2f73dmshc1ebdb25a44b0c3p1729c7jsn5b4457b1fe75",
        "X-RapidAPI-Host": "zillow-com1.p.rapidapi.com"
    }
    response = requests.request("GET", url, headers=headers, params=query)
    return response.text

def multi_api_call(query, results, page=1):
    url = "https://zillow-com1.p.rapidapi.com/propertyExtendedSearch"
    headers = {
        "X-RapidAPI-Key": "a3e8f2f73dmshc1ebdb25a44b0c3p1729c7jsn5b4457b1fe75",
        "X-RapidAPI-Host": "zillow-com1.p.rapidapi.com"
    }
    query['page'] = page
    response = requests.request("GET", url, headers=headers, params=query)
    response=json.loads(response.text)
    results.update({page:response})
    if 'totalPages' not in response:
        return results
    else:
        if response['totalPages'] > page:
            time.sleep(1)
            multi_api_call(query, results, page+1)
        elif response['totalPages'] == page or response['totalPages'] < page:
            return results

        

def check_post_of_the_day(house):
    if house['dateSold'] is None and house['listingStatus'] == 'FOR_SALE' and house['daysOnZillow'] == "1" or house['daysOnZillow'] == "0" or house['daysOnZillow'] == "2":
        return True


def response_normalizer(response):
    for index, page in response.items():
        if page['totalResultCount'] == 0:
            return 'No results found'
        collect={}
        for properties in page.items():
            for property in properties:
                if isinstance(property,str) or isinstance(property,int):
                    continue
                else:
                    for house in property:
                        print('\n')
                        current_prop={house["address"]:house}
                        collect.update(current_prop)
        return collect


#make it so that on the day of listing it gets displayed
#keep track if printed or not


#main function should
# - call api
# api should check if multiple pages are available and if so, call them
# - normalize response
# - filter response to settings of user
# - check if new properties
# - if new properties, send to database
# - if new properties, send to telegram
# - if no new properties, send to telegram


#optional
# - like function
# - dislike function
# - if property is offmarked and liked or disliked, send to telegram








if __name__ == "__main__":
    
    application = Application.builder().token(TOKEN).build()
    # Commands
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('update', update_command))

    # Run bot
    application.run_polling()
