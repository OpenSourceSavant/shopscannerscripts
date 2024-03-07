import pandas as pd
from datetime import datetime, timedelta
import json
import sys
from deal_structure import Deal  # Assuming Deal is defined in deal_structure module
from get_flipkart_data import get_flipkart_data
import pytz
import uuid
import re
from db_operations import create_firestore_document
from send_msg_main_queue import send_message_to_queue

IST = pytz.timezone('Asia/Kolkata')
current_time = datetime.now(IST)


def check_duplicate_flipkart_pid(flipkart_pid):
    df = pd.read_csv('flipkart_deals.csv')
    if not df.empty:
        df['message_time'] = pd.to_datetime(df['message_time'], format='%Y-%m-%d %H:%M:%S').dt.tz_localize(pytz.utc).dt.tz_convert(IST)

        # Filter rows with the same flipkart_url in the last 40 minutes
        filtered_df = df[(df['flipkart_pid'] == flipkart_pid) & (df['message_time'] >= datetime.now(IST) - timedelta(minutes=40))]

        if not filtered_df.empty:
            print(f"The flipkart ID {flipkart_pid} is already present in the CSV file within the last 40 minutes.")
            return True

    return False

def main(url, messageReceived):
    flipkart_pid = ''
    results = []
    if 'pid=' in url:
        flipkart_pid = str(url.split('pid=', 1)[1][0:16])
        result = get_flipkart_data(flipkart_pid)
        results.append(result)
        
    elif 'redirectpid1=' in url:
        flipkart_pid = str(url.split('redirectpid1=', 1)[1][0:16])
        result = get_flipkart_data(flipkart_pid)
        results.append(result)





    if flipkart_pid != '' and not check_duplicate_flipkart_pid(flipkart_pid):
        print('########flipkart PID##########', flipkart_pid)

        print('flipkart URL created and is not repeated')
        

        ## Now Fetch flipkart data using Scraper
        ## Also create deal object now
        deal = Deal()
        deal.messageReceived = messageReceived
        deal.finalMessage = messageReceived
        deal.dealId = str(uuid.uuid4())
        deal.store = 'flipkart'
        flipkart_data = results[0]  # Assuming there is only one result for simplicity

        if flipkart_data:
            deal.productTitle = flipkart_data["productTitle"]
            deal.imageUrl = flipkart_data["imageUrl"]
            deal.dealPrice = flipkart_data["dealPrice"]
            deal.mrp = flipkart_data["mrp"]
            deal.dealPercent = round((deal.mrp - deal.dealPrice) * 100 / deal.mrp)

            deal.storeUrl = flipkart_data["storeUrl"]

            ##create firestore document
            if deal.dealPrice>0:
                # Add the code to append the new record to the CSV file with flipkart_url and current time
                new_record = pd.DataFrame({'flipkart_url': [flipkart_pid], 'message_time': [datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')]})
                new_record.to_csv('flipkart_deals.csv', mode='a', header=False, index=False)
                create_firestore_document(deal)
                send_message_to_queue('deal', deal.to_json())

            
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <url> <message_received>")
        sys.exit(1)

    url = sys.argv[1]
    messageReceived = sys.argv[2]
    print(url)
    main(url, messageReceived)
