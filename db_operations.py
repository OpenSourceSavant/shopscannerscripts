import firebase_admin
from firebase_admin import credentials, firestore, storage
from datetime import datetime, timedelta
import pytz
import json
import time
import pandas as pd
import os
from addTags import getTags


IST = pytz.timezone('Asia/Kolkata')


# Initialize Firebase Admin SDK
cred = credentials.Certificate('key.json')
firebase_admin.initialize_app(cred, {'storageBucket': 'smartsaver-ace3e.appspot.com'})

# Get references to Firestore and Storage
db = firestore.client()
bucket = storage.bucket()

def get_firestore_client():
    return db

def get_smartproxy_amazon_token():
    current_time = datetime.now(IST)
    collection_ref = db.collection('smartproxy_amazon_tokens')
    total_docs = collection_ref.get()
    # Generate a random offset within the total count
    total_docs = len(collection_ref.get())  
    random_offset = int(time.time()) % total_docs
    # Get a single document at the random offset
    query = collection_ref.limit(1).offset(random_offset)
    result = query.stream()
    token = None
    doc = next(result, None)

    if doc:
        token = doc.to_dict().get('token')

        # Update 'last_used' field with the current datetime in IST
        doc_ref = collection_ref.document(doc.id)
        doc_ref.update({
            'lastUsed': current_time,
            'count': doc.to_dict().get('count', 0) + 1  # Increment the count field
        })

    return token    

def create_firestore_document(deal):
    # Create a dictionary of the fields to save in the document
    current_time = datetime.now(IST)
    data = {
        'messageReceived': deal.messageReceived,
        'final_message': deal.finalMessage,
        'dealTime': current_time,
        'separatedText': deal.separatedText,
        'store': deal.store,
        'storeUrl': deal.storeUrl,
        'dealId': deal.dealId,
        'imageUrl':deal.imageUrl,
        'productTitle':deal.productTitle,
        'dealPrice':deal.dealPrice,
        'category':deal.category,
        'mrp':deal.mrp,
        'brand':deal.brand,
        'discountPercentage':round((deal.mrp - deal.dealPrice) * 100 / deal.mrp)
    }

    # Apply tagging logic

   
    tags = []
    if deal.store == 'amazon':
        tags.append('amazon')
    if deal.store == 'flipkart':
        tags.append('flipkart')


    # Add percentage-specific tags
    discount_percentage = deal.dealPercent
    if discount_percentage >= 50:
        tags.append('morethan50')  # Add 'morethan50' tag for discounts greater than 50%
    if discount_percentage >= 60:
        tags.append('morethan60')  # Add 'morethan60' tag for discounts greater than 60%
    if discount_percentage >= 70:
        tags.append('morethan70')  # Add 'morethan70' tag for discounts greater than 70%
    if discount_percentage >= 80:
        tags.append('morethan80')  # Add 'morethan80' tag for discounts greater than 80%
    if discount_percentage >= 90:
        tags.append('morethan90')  # Add 'morethan90' tag for discounts greater than 90%
    # Add more conditions as needed for additional percentage ranges

    

    try:
        json_data = getTags(deal.productTitle)
        print(json_data)
        
        brand = json_data.get('Brand', '')  # Get the brand from the dictionary
        new_tags = json_data.get('Tags', [])  # Get the new tags from the dictionary

        deal.brand = brand
        print(deal.brand)
        
        # Convert any integers in the existing tags list to strings
        print('hello')
        tags.extend(new_tags)

        # Add tags field to the data dictionary
        data['Tags'] = tags


    except Exception as e:
        print(f"An error occurred: {e}")


    finally:
        # Specify the document ID as the dealId
        doc_ref = db.collection('deals').document(str(deal.dealId))
        doc_ref.set(data)    

    