import firebase_admin
from firebase_admin import credentials, firestore, storage
from datetime import datetime, timedelta
import pytz
from addTags import getTags
import time  # Import the time module
import pandas as pd  # Import the pandas library for CSV handling

IST = pytz.timezone('Asia/Kolkata')
current_time = datetime.now(IST)

# Initialize Firebase Admin SDK
cred = credentials.Certificate('key.json')
firebase_admin.initialize_app(cred, {'storageBucket': 'smartsaver-ace3e.appspot.com'})

# Get references to Firestore and Storage
db = firestore.client()
bucket = storage.bucket()

collection_name = 'deals'
docs = db.collection(collection_name).order_by('dealTime', direction=firestore.Query.DESCENDING).stream()


# Iterate through the documents
for doc in docs:
    try:
      
        existing_doc_ids = set(pd.read_csv('updated_docs.csv')['doc_id'])
       
        # Retrieve the document data
        doc_data = doc.to_dict()
        doc_id = doc.id

        if doc_id in existing_doc_ids:
            print(f"Skipping {doc_id} as it's already in updated_docs.csv")
            continue

        # Assuming the deal price is stored in the 'dealPrice' field
        productTitle = doc_data.get('productTitle', '')
        
        # Retrieve existing tags
        existing_tags = doc_data.get('Tags', [])

        # Get new tags
        new_tags_response = getTags(productTitle)
        new_tags = new_tags_response.get('Tags', [])

        # Append new tags to existing tags
        updated_tags = existing_tags + new_tags

        # Remove duplicates if necessary
        updated_tags = list(set(updated_tags))

        print(productTitle)
        print(updated_tags)

        # Update the document with the new tags
        doc.reference.update({'Tags': updated_tags})
        
        # Introduce a delay of 10 seconds
        time.sleep(20)

        print(f"Tags for {productTitle} updated successfully.")
        existing_doc_ids.add(doc_id)
        pd.DataFrame({'doc_id': list(existing_doc_ids)}).to_csv('updated_docs.csv', index=False)

    except Exception as e:
        print(f"Error updating tags for {productTitle}: {e}")

print("Tags update process completed.")
