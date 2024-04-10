import requests
import sys
import argparse
import json
import time 
import csv
import math
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
from selenium.webdriver.firefox.options import Options
now = datetime.now()

start_time = now.strftime("%H:%M:%S")

def get_sub_header():
    firefoxOptions = Options()
    firefoxOptions.add_argument("--headless")
    driver = webdriver.Firefox(options=firefoxOptions)
    driver.get('https://www.chewy.com/deals/todays-deals-2723')
    time.sleep(5)
    data = driver.find_element(By.XPATH,"//div[contains(@class,'__subtext__')]")
    data_text = data.text
    any_product = driver.find_element(By.XPATH, "//a[contains(@class, 'product-image')]")
    product_url = any_product.get_attribute('href')
    driver.quit()
    return {
        'url': product_url,
        'sub_header': data_text
    }


def get_path(url):
    firefoxOptions = Options()
    firefoxOptions.add_argument("--headless")
    driver = webdriver.Firefox(options=firefoxOptions)
    driver.get(url)
    time.sleep(5)
    elem = driver.find_element("xpath", "//*")
    source_code = elem.get_attribute("outerHTML")
    driver.quit()
    return str(source_code).split('chewy-pdp-ui-')[1].split('/')[0]

def useFirstTimeAutoshipDiscount(advertisedPrice, autoshipFirstTimeDiscountPercent, autoshipFirstTimeDiscountMaxSavings):
    if advertisedPrice == None:
        return
    discountedPrice = float(advertisedPrice) * (1 - (float(autoshipFirstTimeDiscountPercent) / 100))
    maxSavingsPrice = float(advertisedPrice) - float(autoshipFirstTimeDiscountMaxSavings)
    if maxSavingsPrice > discountedPrice:
        return "%.2f" % maxSavingsPrice
    else:
        return "%.2f" % discountedPrice

def get_size(size_arr, atributes):
    for attr in atributes:
        id = attr['__ref'].split(':')[2].split(',')[0]
        try:
            return size_arr[id]
        except:
            pass
    return ''


headers = {
    'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Brave";v="122"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'sec-gpc': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
}

params = {
    'groupResults': 'true',
    'count': '36',
    'include': 'items',
    'fields[0]': 'PRODUCT_CARD_DETAILS',
    'omitNullEntries': 'true',
    'catalogId': '1004',
    'from': '0',
    'sort': 'byRelevance',
    'groupId': '2515',
}

def get_product_links(params, cookies, headers):
    max_try = 5
    product_links = []
    while max_try > 0:
        try:
            response = requests.get('https://www.chewy.com/plp/api/search', params=params, cookies=cookies, headers=headers)
            json_data = json.loads(response.text)
            product_links = [product['href'] for product in json_data['products']]
            max_try = 0
        except:
            time.sleep(3)
            max_try = max_try - 1

    if product_links == []:
        log(f'products_links_list None with params {params}')

    return product_links

def get_product_json_data(url, cookies, headers):
    max_try = 5
    detail_prd_json = None
    while max_try > 0:
        try:
            response_prd_json = requests.get(url, cookies=cookies, headers=headers)
            detail_prd_json = json.loads(response_prd_json.content)
            max_try = 0
        except:
            time.sleep(3)
            max_try = max_try - 1
    return detail_prd_json

def log(message):
    print(f'[LOG] {message}')

def get_feature_flags(detail_json, flag_name, default = None):
    '''
        "featureToggles":{
              "__typename":"PDPFeatureToggles",
              "autoshipBuyboxOverride":"VARIANT2",
              "autoshipBuyboxOverrideConflictingPromos":[
                 5213,
                 7564,
                 11565
              ],
              "autoshipFirstTimeDiscountMaxSavings":"20",
              "autoshipFirstTimeDiscountPercent":"35",
              "autoshipShipOnceEnabled":true,
              "autoshipShipOnceSpecialPromotion":"10595",
              "autoshipStartFromPDPEnabled":true,
              "autoshipSuppressFTASList":null,
              "autoshipUseLibsEnabled":false,
              "collectPetAndClinicInfoEnabled":true,
              "enhancedContentMobileEnabled":true,
              "enhancedContentMobileSkuList":"45430 45433",  
              "fbtWidgetEnabled":true,
              "freeShippingNewCustomerEnabled":true,
              "heroPromoSlotEnabled":true,
              "loyaltyFeaturesEnabled":false,
              "pcwWidgetEnabled":true,
              "pdp50WidgetEnabled":true,
              "plabWidgetEnabled":true,
              "plasfWidgetEnabled":true,
              "promoSmartshelfWidgetEnabled":true,
              "promoSmartshelfWidgetTitleEnabled":true,
              "qnaEnabled":true,
              "recentlyViewedEnabled":true,
              "reviewsEnabled":true
        },
    '''
    try:
        flags = detail_json['pageProps']['__APOLLO_STATE__']['ROOT_QUERY']['pdp']['featureToggles']
        return flags[flag_name]
    except:
        return default

def get_sizes_list(detail_json):
    '''
        "Attribute:402": {
            "__typename": "Attribute",
            "id": 402,
            "name": "Count",
            "values": [
              {
                "__ref": "AttributeValue:{\"id\":11635430,\"value\":\"1 Tablet\"}"
              },
              {
                "__ref": "AttributeValue:{\"id\":863604,\"value\":\"30 Tablets\"}"
              },
              {
                "__ref": "AttributeValue:{\"id\":11973166,\"value\":\"60 Tablets\"}"
              },
              {
                "__ref": "AttributeValue:{\"id\":863583,\"value\":\"90 Tablets\"}"
              }
            ]
        },
        or
        "Attribute:400":{
            "__typename":"Attribute",
            "id":400,
            "name":"Size",
            "values":[
               {
                  "__ref":"AttributeValue:{\"id\":320271,\"value\":\"8-oz bag\"}"
               },
               {
                  "__ref":"AttributeValue:{\"id\":520276,\"value\":\"16-oz bag\"}"
               }
            ]
         },
    '''
    short_sizes = {}
    try:
        attr_sizes = [detail_json['pageProps']['__APOLLO_STATE__'][product] for product in detail_json['pageProps']['__APOLLO_STATE__'] if "Attribute:" in product]
        attr_sizes = [attr for attr in attr_sizes if attr['name'] in ['Size', 'Count']]
        for size in attr_sizes:
            for value in size['values']:
                attr_json = json.loads(value['__ref'].replace('AttributeValue:',''))
                short_sizes[str(attr_json['id'])] = f"{size['name']}: {attr_json['value']}"
    except Exception as e:
        log(f'Error on get_sizes_list: {str(e)}')
    return short_sizes

def get_product_items(detail_json):
    '''
        "Item:SXRlbToyNjgwMjU=":{
            "__typename":"Item",
            "id":"SXRlbToyNjgwMjU=",
            "advertisedPrice":"$5.56",
            "name":"American Journey Sausage, Egg & Cheese Flavor Grain-Free Oven Baked Crunchy Biscuit Dog Treats, 16-oz bag",
            "partNumber":"241535",
            "entryID":"268025",
            "isGiftCard":false,
            "isPrescription":false,
            "inStock":true,
            "isPublished":true,
            "isUnavailable":false,
            "perUnitPrice":"$0.35",
            "unitOfMeasure":"ONZ",
            "attributeValues({\"includeEnsemble\":true,\"usage\":[\"DEFINING\"]})":[
               {
                  "__ref":"AttributeValue:{\"id\":null,\"value\":\"Sausage, Egg & Cheese\"}"
               },
               {
                  "__ref":"AttributeValue:{\"id\":520276,\"value\":\"16-oz bag\"}"
               }
            ],
            "fullImage":{
               "__typename":"Image",
               "url({\"autoCrop\":true,\"square\":144})":"https://image.chewy.com/is/image/catalog/241535_MAIN._AC_SS144_V1608316034_.jpg",
               "url({\"autoCrop\":true,\"maxWidth\":275})":"https://image.chewy.com/is/image/catalog/241535_MAIN._AC_SX275_V1608316034_.jpg"
            }
         },
    '''
    try:
        return [detail_json['pageProps']['__APOLLO_STATE__'][product] for product in detail_json['pageProps']['__APOLLO_STATE__'] if "Item" in product]
    except:
        return None

def get_product_general_info(detail_json):
    try:
        return [detail_json['pageProps']['__APOLLO_STATE__'][product] for product in detail_json['pageProps']['__APOLLO_STATE__'] if "Product" in product][0]
    except Exception as e:
        log(f'Error on get product default {str(e)}')
        return None


def get_product_details(detail_json):
    try:
        product_items = get_product_items(detail_json)
        if product_items == None:
            return None
        details =  [key for key  in [main for main in product_items] if 'product' in key][0]
        return details
    except:
        return None

def get_breadcrumb(detail_json):
    '''
        "Breadcrumb:288":{
            "__typename":"Breadcrumb",
            "id":"288",
            "name":"Dog",
            "url":"https://www.chewy.com/b/dog-288"
         },
         "Breadcrumb:335":{
            "__typename":"Breadcrumb",
            "id":"335",
            "name":"Treats",
            "url":"https://www.chewy.com/b/treats-335"
         },
         "Breadcrumb:1537":{
            "__typename":"Breadcrumb",
            "id":"1537",
            "name":"Biscuits, Cookies & Crunchy Treats",
            "url":"https://www.chewy.com/b/biscuits-cookies-crunchy-treats-1537"
         },
    '''
    try:
        return '>'.join([breadcrumb['name'] for breadcrumb in [detail_json['pageProps']['__APOLLO_STATE__'][product] for product in detail_json['pageProps']['__APOLLO_STATE__'] if "Breadcrumb" in product]])
    except:
        return ''

def get_promotion(detail_json):
    '''
        "Promotion:11570":{
            "__typename":"Promotion",
            "id":11570,
            "isSmartshelfEligible":true,
            "flagText":null,
            "longDescription":"For every $100 purchase with promo code ENJOY24, you'll receive a $30 e-Gift card. Limit 1 use per order, limit 3 orders per customer. Must add $100.00 worth of eligible items and enter code ENJOY24 at checkout to receive $30 eGift card. Free eGift Card added at Checkout with qualifying purchase and automatically added to your Chewy account after your order ships. Excludes gift cards, select prescription items, and select brands including but not limited to Balto, Embark, Diamond, Castor & Pollux, Frontline Plus, Kibbles 'n Bits, Kit & Kaboodle, Kitten Chow, OraVet, Sullivan Supply, Seresto, Sweet Meadow Farm, The Petz Kitchen, Taste of the Wild, Tidy Max, Thundershirt,  Victor, 9 Lives, Wisdom Panel, Yaheetech, Wholistic Pet Organics, and other select items. Customer must be logged into account to view all applicable promotions. Subject to Chewy Gift Card Terms and Conditions found here: https://chewy.com/app/content/gift-cards-terms. Gift Cards cannot be returned, refunded, or redeemed for cash except as required by law. Valid through 4/08/24 6:30AM EST, while supplies last, subject to Terms.",
            "shortDescription":"Spend $100, Get $30 eGift Card with code: ENJOY24",
            "helperText":"Must enter code ENJOY24 at checkout to redeem",
            "desktopPromoTermDetailsUrl":null,
            "mobilePromoTermDetailsUrl":null,
            "accessibilityPromoTermDetails":null,
            "promoHeadlineLong":null,
            "promoHeadlineShort":null
         },
    '''
    try:
        return [promotion for promotion in [detail_json['pageProps']['__APOLLO_STATE__'][product] for product in detail_json['pageProps']['__APOLLO_STATE__'] if "Promotion" in product]][0]
    except:
        return None

def isConflitPromo(data):
    if data['topPromotion'] in data['autoshipBuyboxOverrideConflictingPromos'] and data['topPromotion'] != None and data['autoshipBuyboxOverrideConflictingPromos'] != None:
        return True
    return False

def get_description_attribute(data, attribute_name):
    try:
        return data['descriptionAttributes'][attribute_name].replace('\"',"")
    except:
        return ''

def main(category, perc, f_name):
    print('\n\nGETING WEB SITE BUILD PATH JUST WAIT PLEASE...')
    sub_header = get_sub_header()
    sufix = get_path(sub_header['url'])

    session = requests.Session()
    response = session.get('https://www.chewy.com/', headers=headers)
    cookies = { 'KP_UIDz-ssn': f"{response.cookies.get_dict()['KP_UIDz-ssn']};" }

    head_lines = False

    params['groupId'] = f'{category}'
    response = requests.get('https://www.chewy.com/plp/api/search', params=params, cookies=cookies, headers=headers)
    json_data = json.loads(response.text)
    total = math.ceil(float(json_data['recordSetTotal']) / 36)
    pageStr = perc
    pageInit = int(pageStr.split('-')[0])
    pageEnd = int(pageStr.split('-')[1])
    pageInit = int(math.ceil((total / 100 * pageInit)))
    pageEnd = int(math.ceil((total / 100 * pageEnd)))
    if '-100' in pageStr:
        pageEnd = pageEnd + 1

    print(f'Category: {category}\nInitial Page: {pageInit}\nLast Page: {pageEnd}\nFile Name: {f_name}\n Site build {sufix}')

    print('ALL DONE, STARTING CRAWLER NOW...\n\n')
    time.sleep(5)

    with open(f_name, 'a') as f:
        for i in range(pageInit,pageEnd):
            params['from'] = f'{i * 36}'
            params['groupId'] = f'{category}'
            products_links_list = get_product_links(params, cookies, headers)

            for product_url in products_links_list:
                try:
                    json_backend_url = f'https://www.chewy.com/_next/data/chewy-pdp-ui-{sufix}/en-US/{product_url.replace("https://www.chewy.com/", "")}.json'
                    detail_json = get_product_json_data(json_backend_url, cookies, headers)
                    time.sleep(1/2)
                    if detail_json == None:
                        log(f'detail_json None in json url: {json_backend_url}')
                        sub_header = get_sub_header()
                        sufix = get_path(sub_header['url'])
                        session = requests.Session()
                        response = session.get('https://www.chewy.com/', headers=headers)
                        cookies = { 'KP_UIDz-ssn': f"{response.cookies.get_dict()['KP_UIDz-ssn']};" }
                        json_backend_url = f'https://www.chewy.com/_next/data/chewy-pdp-ui-{sufix}/en-US/{product_url.replace("https://www.chewy.com/", "")}.json'
                        detail_json = get_product_json_data(json_backend_url, cookies, headers)
                        if detail_json == None:
                            continue # skip this product and go to the next

                    product_items = get_product_items(detail_json)
                    if product_items == None:
                        log(f'product_items None in json url: {json_backend_url}')
                        continue # skip this product and go to the next

                    for product in product_items:
                        product_active_url = f"{('/').join(product_url.split('/')[:-1])}/{product['entryID']}"
                        json_backend_url = f'https://www.chewy.com/_next/data/chewy-pdp-ui-{sufix}/en-US/{product_active_url.replace("https://www.chewy.com/", "")}.json'
                        detail_json = get_product_json_data(json_backend_url, cookies, headers)
                        time.sleep(1/2)
                        
                        product_general_info = get_product_general_info(detail_json)
                        if product_general_info == None:
                            log(f'product_general_info None in json url: {json_backend_url}')
                            continue # skip this product and go to the next


                        autoshipFirstTimeDiscountPercent     = float(get_feature_flags(detail_json, 'autoshipFirstTimeDiscountPercent', 0))
                        autoshipFirstTimeDiscountMaxSavings  = float(get_feature_flags(detail_json, 'autoshipFirstTimeDiscountMaxSavings',0))
                        short_sizes = get_sizes_list(detail_json)    
                        breadcrumb = get_breadcrumb(detail_json) 
                        promotion = get_promotion(detail_json)
                        product_detail = get_product_details(detail_json)

                        if product_detail == None:
                            log(f'product_detail None in json url: {json_backend_url}')
                            continue # skip this product and go to the next

                        data = {
                            "slug": product_general_info['slug'],
                            'manufacturerName': product_general_info['manufacturerName'], 
                            "promotion": '' if promotion == None else promotion['shortDescription'] if 'shortDescription' in promotion.keys() else None,
                            "autoshipFirstTimeDiscountPercent": autoshipFirstTimeDiscountPercent,
                            "isAutoshipAllowed": None if 'isAutoshipAllowed' not in product_detail.keys() else product_detail['isAutoshipAllowed'],
                            "autoshipDiscountPct": None if 'autoshipDiscountPct' not in product_detail.keys() else product_detail['autoshipDiscountPct'],
                            "autoshipFirstTimeDiscountMaxSavings": autoshipFirstTimeDiscountMaxSavings,
                            "strikeThroughPrice": None if 'strikeThroughPrice' not in product_detail.keys() else product_detail['strikeThroughPrice'],
                            "shippingMessage": None if 'shippingMessage'  not in product_detail.keys() else product_detail['shippingMessage'],
                            "isAutoshipAllowed": None if 'isAutoshipAllowed' not in product_detail.keys() else product_detail['isAutoshipAllowed'],
                        }
                        try:
                            data["topPromotion"] = product_detail['topPromotion']['__ref'].split(':')[1]
                        except:
                            data["topPromotion"] = None

                        try:
                            data["topHeadlinePromotion"] = product_detail['topHeadlinePromotion']
                        except:
                            data['topHeadlinePromotion'] = None

                        attribute_values_key = [key for key in product.keys() if 'attributeValues' in key][0]
                        
                        try:
                            try:
                                images = [image for _, image in product['fullImage'].items() if image != 'Image'][1]
                            except:
                                images = ''
                            data.update({
                                "entryID": product['entryID'],
                                "name": product['name'],
                                "attributeValues": product[attribute_values_key], 
                                "url": product_active_url,
                                "advertisedPrice": product['advertisedPrice'].replace('$',''),
                                "autoShipDiscountPercent": get_feature_flags(detail_json, 'autoshipFirstTimeDiscountPercent'),
                                "mapSavings": None if 'mapSavings' not in product_detail.keys() else product_detail['mapSavings'],                            
                                "descriptionAttributes": {},
                                "mapEnforced": product_detail['mapEnforced'],                            
                                "autoshipBuyboxOverrideConflictingPromos": get_feature_flags(detail_json, 'autoshipBuyboxOverrideConflictingPromos'),
                                "autoshipSuppressFTASList": get_feature_flags(detail_json, 'autoshipSuppressFTASList'),
                                "inStock": product['inStock'],
                                "gtin": f"{str(product['gtin'])}" if product['gtin'] != None else '000000000',
                                "images" : images, 
                                "partNumber": product['partNumber'],
                                "isPrescription": product['isPrescription'],
                            })

                            for attribute in product_detail['descriptionAttributes']:
                                data['descriptionAttributes'][f"{attribute['name']}"] = attribute['values'][0]['__ref'].split(':')[-1].split('}')[0] 

                            data["firstTimeAutoshipPrice"] = useFirstTimeAutoshipDiscount(data['advertisedPrice'], data['autoShipDiscountPercent'], data['autoshipFirstTimeDiscountMaxSavings'])
                            data['isConflitPromo']  = isConflitPromo(data)
                            mapRestricted  = data['mapEnforced']  and data['mapSavings'] != None
                            data['mapRestricted'] = mapRestricted
                            isFTASRepressedSku = int(data['partNumber']) in data['autoshipSuppressFTASList'] if data['autoshipSuppressFTASList'] != None else False
                            data['isFTASRepressedSku'] = isFTASRepressedSku

                            display = True
                            if data['isAutoshipAllowed'] == False:
                                data['firstTimeAutoshipPrice'] = None
                            else:
                                display = not (data['topHeadlinePromotion'] == None and data['isConflitPromo'] == False and data['mapRestricted'] == False and data['isFTASRepressedSku'] == False)
                                if display == False:
                                    data['firstTimeAutoshipPrice'] = data['advertisedPrice']    


                            to_print={
                                'Product Code': data['entryID'],
                                'Sku': data['partNumber'],
                                'url': data['url'],
                                'Product Name': data['name'],
                                'Price': data['advertisedPrice'],
                                'Stock': 'Instock' if data['inStock'] else 'Out of Stock', 
                                'Breadcrumb': breadcrumb,
                                'Shipping': 0 if float(data['advertisedPrice']) > 49 else '4.95',
                                'Image': data['images'],
                                'Brand': data['manufacturerName'],
                                'generic_name': get_description_attribute(data,'Generic Name'),
                                'product_form': get_description_attribute(data,'Product Form'),
                                'drug_type': get_description_attribute(data,'Drug Type'),
                                'prescription_item': 'yes' if data['isPrescription'] else 'no',
                                'autoship': data['firstTimeAutoshipPrice'],
                                'promotional_text': data['promotion'],
                                'promotional_information:': sub_header['sub_header'],
                                'pack_size': get_size(short_sizes, data['attributeValues']),
                                'msrp': data['strikeThroughPrice'].replace('$','') if data['strikeThroughPrice'] != None else '',
                                'gtin': f"0000000000000{data['gtin']}"[-14:],
                            }
                            print(json.dumps(to_print, indent=4))
                            writer = csv.DictWriter(f, fieldnames=to_print)

                            if head_lines == False:
                                head_lines = True
                                writer.writeheader()
                            writer.writerow(to_print)
                            if data['firstTimeAutoshipPrice'] != None:
                             to_print['Product Name'] = f"{data['name']} - Autosend"
                             to_print['Price'] = data['firstTimeAutoshipPrice']
                             print('--------')
                             print(json.dumps(to_print, indent=4))
                             writer.writerow(to_print)
                        except Exception as e:
                            print('Error A', e)
                            pass
                except KeyboardInterrupt:
                    exit(0)
                except Exception as e:
                    print('Error B', e)
                print('--------')
        time.sleep(2)
# start time = 02:15
categories = {
    'dog': '288',
    'cat': '325',
    'fish': '885',
    'bird': '941',
    'small-pet': '977',
    'reptile': '1025',
    'farm-animal': '8403',
    'horse': '1663',
    'pharmacy': '2515',
}

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    file_time = now.strftime("%y%m%d%H%M%S")

    parser.add_argument("--category",  "-c", help="[REQUIRED] Category can be dog, cat, fish, bird, small-pet, reptile, farm-animal, horse or pharmacy.")
    parser.add_argument("--percentage", "-p", help='[OPTIONAL] Percentual of pages can be 0-25, 25-50, 10-20 or any combinations between 0 and 100. Default 0-100.', type=str, default='0-100')
    parser.add_argument("--file", "-f", help='[OPTIONAL] File name(csv) to ouput result. Default [category]_chewy_[percentage]_YY-MM-DD-HH-mm-ss.csv', type=str)
    args=parser.parse_args()
    if args.category == None:
        print(parser.format_help())
        exit(0)

    if args.category not in categories.keys():
        print(f'\n\n\nInvalid param "{args.category}"\n\n')
        print(parser.format_help())
        exit(0)
    if args.file == None:
        args.file=f"{args.category}_chewy_{args.percentage}_{file_time}.csv"

    main(categories[args.category], args.percentage, args.file)
    print("Start Time =", start_time)
    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)

