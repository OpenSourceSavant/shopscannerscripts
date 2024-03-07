import gspread
from oauth2client.service_account import ServiceAccountCredentials
from deal_structure import Deal
import time


# Set the path to the file containing the count
count_file = 'googleSheetsCount.txt'

# Use the credentials JSON file for authentication
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
g_client = gspread.authorize(creds)
sheet = g_client.open("ProductsData").worksheet('Nykaa')


def write_data_to_sheet(deal,category):
    # Read the count from the file
    with open(count_file, 'r') as file:
        count = int(file.read())
    
    
    sheet.update(f'A{count}', deal.storeUrl)
    time.sleep(1)
    sheet.update(f'B{count}', deal.productTitle)
    time.sleep(1)
    sheet.update(f'C{count}', category)
    time.sleep(1)
    sheet.update(f'D{count}', deal.dealPrice)
    time.sleep(1)
    sheet.update(f'E{count}', deal.mrp)



    #sheet.update(f'B{count}', Tags)


    with open(count_file, 'w') as file:
        count=count+1
        file.write(str(count))

       

