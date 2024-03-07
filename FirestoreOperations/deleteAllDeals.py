import firebase_admin
from firebase_admin import credentials, firestore, storage
from datetime import datetime, timedelta
import pytz
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

for doc in docs:
    doc.reference.delete()