import requests
import json

requests.packages.urllib3.disable_warnings()

headers = {
    'Fk-Affiliate-Id': 'arorakara1',
    'Fk-Affiliate-Token': '445cfc7694e9424f8547980ae80ac08a'
}

api_url = 'https://affiliate-api.flipkart.net/affiliate/1.0/product.json'


def get_flipkart_data(pid):
    productId = pid
    params = {'id': productId}
    response = requests.get(api_url, headers=headers, params=params)
    data = json.loads(response.text)

    result = {
        'productTitle': data['productBaseInfoV1']['title'],
        'storeUrl': data['productBaseInfoV1']['productUrl'],
        'mrp': data['productBaseInfoV1']['maximumRetailPrice']['amount'],
        'dealPrice': data['productBaseInfoV1']['flipkartSpecialPrice']['amount']
    }

    image_urls = data['productBaseInfoV1']['imageUrls']
    if len(image_urls) > 0:
        i = 0
        for size, url in image_urls.items():
            i = i + 1
            if i == 2:
                result['imageUrl'] = url

    return result