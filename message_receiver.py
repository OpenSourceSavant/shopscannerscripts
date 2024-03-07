from telethon import TelegramClient, events
import requests
import re
from urllib.parse import unquote
import pytz
from telethon.tl.types import MessageEntityTextUrl
import subprocess


IST = pytz.timezone('Asia/Kolkata')

# Telethon credentials start
api_id = 11154281
api_hash = '0ec7b1f0282fd8119ca7d6ad426ca6fa'
client = TelegramClient('sessionjiolocalsystem', api_id, api_hash)
# Telethon credential end


@client.on(events.NewMessage())
async def newMessageListener(event):
    try:
        messageReceived = event.message.message

        if event.message.entities:
            for url_entity, inner_text in event.message.get_entities_text():
                if isinstance(url_entity, MessageEntityTextUrl):
                    url = url_entity.url
                    messageReceived = messageReceived.replace(inner_text, url)

        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', messageReceived)
        for url in urls:
            url = unquote(url)
            response = requests.head(url, allow_redirects=True, timeout=25)
            url = unquote(response.url)

            if 'amazon.in' in url:
                subprocess.run(["python3", "process_amazon_deal.py", url, messageReceived])                

            if 'myntra.com' in url:
                subprocess.run(["python3", "process_myntra_deal.py", url, messageReceived]) 

            if 'nykaa.com' in url:
                subprocess.run(["python3", "process_nykaa_deal.py", url, messageReceived])

            if 'flipkart.com' in url:
                subprocess.run(["python3", "process_flipkart_deal.py", url, messageReceived])     
    except Exception as e:
        print(e)

# Print a message when the client is started
print("Client started")

client.start()
client.run_until_disconnected()
