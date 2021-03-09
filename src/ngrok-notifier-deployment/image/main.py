import json
import requests
import telegram
import time
from datetime import datetime
import os

def main():
    # get all parameters
    token = os.getenv('TELEGRAM_AUTH_TOKEN')
    assert token != None

    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    assert chat_id != None

    ngrok_client_urls = os.getenv('NGROK_CLIENT_URLS')
    protocols = os.getenv('PROTOCOLS')
    descriptions = os.getenv('DESCRIPTIONS')

    assert ngrok_client_urls != None and protocols != None and descriptions != None

    ngrok_client_urls = ngrok_client_urls.split(';')
    protocols = protocols.split(';')
    descriptions = descriptions.split(';')[:-1]
    assert len(ngrok_client_urls) == len(descriptions) == len(protocols)

    # create a separator for the message
    separator = '\n-----------------\n'

    # initialize the bot
    bot = telegram.Bot(token=token)

    # loop for check all the urls, and in case of changes, send the new message
    public_urls_prev = ''
    while True:
        public_urls, message = get_message(ngrok_client_urls, protocols, descriptions, separator)
        if public_urls_prev != public_urls:
            public_urls_prev = public_urls
            bot.send_message(chat_id=chat_id, text=message)
        # check time
        time.sleep(10 * 60)
def get_message(ngrok_client_urls, protocols, descriptions, separator) -> str:
    message = ''
    public_urls = ''
    for ngrok_client_url, protocol, description in zip(ngrok_client_urls, protocols, descriptions):
        public_url = get_public_url(ngrok_client_url.strip(), protocol.strip())
        message += description + public_url + separator
        public_urls += public_url
    
    return public_urls, message[:-len(separator)]
    
def get_public_url(ngrok_client_url, protocol) -> str:
    assert protocol == 'http' or protocol == 'https' or protocol == 'tcp'

    res = requests.get('http://' + ngrok_client_url + ':4040/api/tunnels')
    jsondata = json.loads(res.text)
    if protocol == 'http': return jsondata['tunnels'][0]['public_url']
    elif protocol == 'https': return jsondata['tunnels'][1]['public_url']
    elif protocol == 'tcp': return jsondata['tunnels'][0]['public_url'][6:]

if __name__   == "__main__":
   main()