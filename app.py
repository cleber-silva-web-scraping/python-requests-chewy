import requests
import uuid
import traceback
import argparse
import json
import time 
import csv
import math
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
from selenium.webdriver.firefox.options import Options

process_uuid = str(uuid.uuid4())
path = '/'.join(__file__.split('/')[:-1])
now = datetime.now()
start_time = now.strftime("%H:%M:%S")

url_done = set()

def write_to_file(f, to_print, head_lines, data = None):
    writer = csv.DictWriter(f, fieldnames=to_print)

    if head_lines == False:
        writer.writeheader()

    to_print = remove_break_lines(to_print)
    writer.writerow(to_print)
    variations_products = 1

    if data != None and 'firstTimeAutoshipPrice' in data.keys() and data['firstTimeAutoshipPrice'] != None:
        variations_products = variations_products + 1
        to_print['Product Name'] = f"{data['name']} - Autosend"
        to_print['Price'] = data['firstTimeAutoshipPrice'].replace('$', '')
        to_print = remove_break_lines(to_print)
        writer.writerow(to_print)

    return variations_products

def remove_break_lines(dictionary):
    for key in dictionary.keys():
        try:
            dictionary[key] = None if dictionary[key] == None else re.sub("\n|\r", " ", f'{dictionary[key]}').strip()
        except:
            pass

    return dictionary

def log(message, product_url=None):
    log_now = datetime.now()
    log_time = log_now.strftime("%H:%M:%S")
    f = open(f"{path}/app_error.log", "a")
    f.write(f'[{log_time}] {message}\n')
    f.close()
    if product_url:
        f = open(f"{path}/url_error.log", "a")
        f.write(f'{product_url}\n')
        f.close()


def get_sub_header():
    max_try = 5
    data = None
    while max_try > 0:
        try:
            options = Options()
            options.add_argument("--headless")
            driver = webdriver.Firefox(options=options)
            driver.get('https://www.chewy.com/deals/todays-deals-2723')
            time.sleep(5)
            data = driver.find_element(By.XPATH,"//div[contains(@class,'__subtext__')]")
            data_text = data.text
            any_product = driver.find_element(By.XPATH, "//a[contains(@class, 'product-image')]")
            product_url = any_product.get_attribute('href')
            driver.quit()
            data = {
                'url': product_url,
                'sub_header': data_text
            }
            max_try = 0
        except:
            time.sleep(3)
            max_try = max_try -1

    return data

def get_path(url):
    max_try = 5
    data = None
    while max_try > 0:
        try:
            firefoxOptions = Options()
            firefoxOptions.add_argument("--headless")
            driver = webdriver.Firefox(options=firefoxOptions)
            driver.get(url)
            time.sleep(5)
            elem = driver.find_element("xpath", "//*")
            source_code = elem.get_attribute("outerHTML")
            driver.quit()
            data = str(source_code).split('chewy-pdp-ui-')[1].split('/')[0]
            max_try = 0
        except:
            time.sleep(3)
            max_try = max_try - 1

    return data

def useFirstTimeAutoshipDiscount(advertisedPrice, autoshipFirstTimeDiscountPercent, autoshipFirstTimeDiscountMaxSavings):
    if advertisedPrice == None:
        return None
    discountedPrice = float(advertisedPrice) * (1 - (float(autoshipFirstTimeDiscountPercent) / 100))
    maxSavingsPrice = float(advertisedPrice) - float(autoshipFirstTimeDiscountMaxSavings)
    if maxSavingsPrice > discountedPrice:
        return "%.2f" % maxSavingsPrice
    else:
        return "%.2f" % discountedPrice

def get_size(size_arr, atributes):
    try:
        for attr in atributes:
            id = attr['__ref'].split(':')[2].split(',')[0]
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

def get_product_links(params, cookies, headers, proxy):
    proxies = { 'https' : proxy } 
    max_try = 5
    product_links = []
    while max_try > 0:
        try:
            if proxy != '':
                response = requests.get('https://www.chewy.com/plp/api/search', params=params, cookies=cookies, headers=headers, proxies=proxies, timeout=21)
            else:
                time.sleep(1/5)
                response = requests.get('https://www.chewy.com/plp/api/search', params=params, cookies=cookies, headers=headers, timeout=22)

            json_data = json.loads(response.text)
            product_links = json_data['products'] 
            max_try = 0
        except:
            time.sleep(1)
            max_try = max_try - 1

    if product_links == []:
        log(f'products_links_list None with params {params}')

    return product_links

def get_product_json_data(url, cookies, headers, proxy):
    proxies = { 'https' : proxy } 
    max_try = 5
    detail_prd_json = None
    while max_try > 0:
        try:
            if proxy != '':
                response_prd_json = requests.get(url, cookies=cookies, headers=headers, proxies=proxies, timeout=23)
            else:
                time.sleep(1/5)
                response_prd_json = requests.get(url, cookies=cookies, headers=headers, timeout=24)

            detail_prd_json = json.loads(response_prd_json.content)
            if '__APOLLO_STATE__' not in detail_prd_json['pageProps'].keys():
                time.sleep(3)
                max_try = max_try - 1
            else:
                max_try = 0
        except:
            time.sleep(1)
            max_try = max_try - 1
    return detail_prd_json

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
            if 'values' in size.keys():
                for value in size['values']:
                    attr_json = json.loads(value['__ref'].replace('AttributeValue:',''))
                    short_sizes[str(attr_json['id'])] = f"{size['name']}: {attr_json['value']}"

    except Exception as e:
        print(traceback.format_exc())
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
        products =  [detail_json['pageProps']['__APOLLO_STATE__'][product] for product in detail_json['pageProps']['__APOLLO_STATE__'] if "Item" in product]
        return products
    except:
        return None

def get_product_general_info(detail_json):
    try:
        return [detail_json['pageProps']['__APOLLO_STATE__'][product] for product in detail_json['pageProps']['__APOLLO_STATE__'] if "Product" in product][0]
    except Exception as e:
        log(f'Erroe on get product default: {str(traceback.format_exc())}')
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

def check_exist(rows, value):
    for row in rows:
        if row['url'] == value and row['status'] == 'Error':
            return True
    return False

def create_error_product(product_data):
    to_print={
        'Status': 'Error', 
        'Reference': product_data['href'],
        'Product Code': '',
        'Sku': product_data['partNumber'],
        'url': product_data['href'],
        'Product Name': product_data['name'],
        'Price': product_data['price'],
        'Stock': 'Instock' if product_data['inStock'] else 'Out of Stock', 
        'Breadcrumb': '',
        'Shipping': None if product_data['price'] == None else 0 if float(product_data['price']) > 49 else '4.95',
        'Image': product_data['image'],
        'Brand': product_data['manufacturer'],
        'generic_name': '',
        'product_form':'',
        'drug_type': '', 
        'prescription_item': 'yes' if product_data['isPrescription'] else 'no',
        'autoship': '',
        'promotional_text': '',
        'promotional_information:': sub_header['sub_header'],
        'pack_size': '',
        'msrp': None if 'strikePrice' not in product_data.keys() else product_data['strikePrice'].replace('$','') if product_data['strikePrice'] != None else '',
        'gtin': f"00000000000000",
    }
    return to_print


def main(category, perc, f_name, proxy, runner_data = None):
    proxies = { 'https' : proxy } 
    unique_products = 0
    error_products = 0
    variations_products = 0

    if runner_data:
        sub_header = runner_data
        sufix = runner_data['sufix']
    else:
        print('\n\nGETING WEB SITE BUILD PATH JUST WAIT PLEASE...')
        sub_header = get_sub_header()
        if sub_header == None:
            log(f'Fatal error headers -c {category} -p {perc}')
            print('Finish')
            exit(0)

        sufix = get_path(sub_header['url'])
        if sufix == None:
            log(f'Fatal error sufix -c {category} -p {perc}')
            print('Finish')
            exit(0)

    session = requests.Session()
    if proxy != '':
        response = session.get('https://www.chewy.com/', headers=headers, proxies=proxies, timeout=25)
    else:
        response = session.get('https://www.chewy.com/', headers=headers, timeout=26)

    cookies = { 'KP_UIDz-ssn': f"{response.cookies.get_dict()['KP_UIDz-ssn']};" }

    head_lines = False

    params['groupId'] = f'{category}'
    if proxy != '':
        response = requests.get('https://www.chewy.com/plp/api/search', params=params, cookies=cookies, headers=headers, proxies=proxies, timeout=27)
    else:
        time.sleep(1/2)
        response = requests.get('https://www.chewy.com/plp/api/search', params=params, cookies=cookies, headers=headers, timeout=28)

    json_data = json.loads(response.text)
    total = math.ceil(float(json_data['recordSetTotal']) / 36)
    pageStr = perc
    pageInit = int(pageStr.split('-')[0])
    pageEnd = int(pageStr.split('-')[1])
    pageInit = int(math.ceil((total / 100 * pageInit)))
    pageEnd = int(math.ceil((total / 100 * pageEnd)))
    if '-100' in pageStr:
        pageEnd = pageEnd + 1
    print(f'Category: {category}\nInitial Page: {pageInit}\nLast Page: {pageEnd}\nFile Name: {f_name}\nSite build "{sufix}"')
    print('ALL DONE, STARTING CRAWLER NOW...\n\n')

    time.sleep(1)
    with open(f_name, 'a') as f:
        for i in range(pageInit,pageEnd):
            params['from'] = f'{i * 36}'
            params['groupId'] = f'{category}'
            products_links_list_main = get_product_links(params, cookies, headers, proxy)
            products_links_list = [{'url': link['href'], 'status':'normal' } for link in  products_links_list_main]

            for product_data in products_links_list:
                product_url = product_data['url']
                product_status = product_data['status']
                unique_products = unique_products + 1
                try:
                    json_backend_url = f'https://www.chewy.com/_next/data/chewy-pdp-ui-{sufix}/en-US/{product_url.replace("https://www.chewy.com/", "")}.json'
                except:
                    log(f'Product url replace error in : {product_url}', product_url)
                    if product_status == 'Error':
                        error_products = error_products + 1
                        to_print = create_error_product(product_data)
                        variations_products = variations_products + write_to_file(f, to_print, head_lines, {'firstTimeAutoshipPrice': None if 'autoshipPrice'  not in product_data.keys() else product_data['autoshipPrice']})

                    if product_status == 'normal' and check_exist(products_links_list, product_url) == False:
                        products_links_list.append({'url': product_url, 'status': 'Error'})
                        error_products = error_products - 1
                    continue

                try:
                    detail_json = get_product_json_data(json_backend_url, cookies, headers, proxy)
                    if detail_json == None:
                        log(f'detail_json None in json url: {json_backend_url}', product_url)
                        sub_header = get_sub_header()
                        sufix = get_path(sub_header['url'])
                        session = requests.Session()
                        if proxy != '': 
                            response = session.get('https://www.chewy.com/', headers=headers, proxies=proxies, timeout=29)
                        else:
                            response = session.get('https://www.chewy.com/', headers=headers, timeout=19)

                        cookies = { 'KP_UIDz-ssn': f"{response.cookies.get_dict()['KP_UIDz-ssn']};" }
                        json_backend_url = f'https://www.chewy.com/_next/data/chewy-pdp-ui-{sufix}/en-US/{product_url.replace("https://www.chewy.com/", "")}.json'
                        detail_json = get_product_json_data(json_backend_url, cookies, headers, proxy)
                        if detail_json == None:
                            if product_status == 'Error':
                                error_products = error_products + 1
                                to_print = create_error_product(product_data)
                                variations_products = variations_products + write_to_file(f, to_print, head_lines, {'firstTimeAutoshipPrice': None if 'autoshipPrice'  not in product_data.keys() else product_data['autoshipPrice']})
                            log(f'Error skip product list {str(json_backend_url)}', product_url)
                            if product_status == 'normal' and check_exist(products_links_list, product_url) == False:
                                products_links_list.append({'url': product_url, 'status': 'Error'})
                            continue # skip this product and go to the next

                    product_items = get_product_items(detail_json)
                    if product_items == None:
                        if product_status == 'Error':
                            error_products = error_products + 1
                            to_print = create_error_product(product_data)
                            variations_products = variations_products + write_to_file(f, to_print, head_lines, {'firstTimeAutoshipPrice': None if 'autoshipPrice'  not in product_data.keys() else product_data['autoshipPrice']})

                        log(f'Error skip product_items in json url: {str(json_backend_url)}', product_url)
                        if product_status == 'normal' and check_exist(products_links_list, product_url) == False:
                            products_links_list.append({'url': product_url, 'status': 'Error'})
                        continue # skip this product and go to the next

                    for product in product_items:
                        if 'entryID' not in product.keys():
                            product['entryID'] = product_url.split('/')[-1]
                        product_active_url = f"{('/').join(product_url.split('/')[:-1])}/{product['entryID']}"
                        if product_active_url in url_done:
                            continue # duplicated url...

                        json_backend_url = f'https://www.chewy.com/_next/data/chewy-pdp-ui-{sufix}/en-US/{product_active_url.replace("https://www.chewy.com/", "")}.json'
                        detail_json = get_product_json_data(json_backend_url, cookies, headers, proxy)
                        product_general_info = get_product_general_info(detail_json)
                        if product_general_info == None:
                            log(f'product_general_info None in json url: {json_backend_url}', product_url)
                            if product_status == 'Error':
                                error_products = error_products + 1
                                to_print = create_error_product(product_data)
                                variations_products = variations_products + write_to_file(f, to_print, head_lines, {'firstTimeAutoshipPrice': None if 'autoshipPrice'  not in product_data.keys() else product_data['autoshipPrice']})
                                
                            if product_status == 'normal' and check_exist(products_links_list, product_url) == False:
                                products_links_list.append({'url': product_url, 'status': 'Error'})
                            continue # skip this product and go to the next


                        autoshipFirstTimeDiscountPercent     = float(get_feature_flags(detail_json, 'autoshipFirstTimeDiscountPercent', 0))
                        autoshipFirstTimeDiscountMaxSavings  = float(get_feature_flags(detail_json, 'autoshipFirstTimeDiscountMaxSavings',0))
                        short_sizes = get_sizes_list(detail_json)    
                        breadcrumb = get_breadcrumb(detail_json) 
                        promotion = get_promotion(detail_json)
                        product_detail = get_product_details(detail_json)

                        if product_detail == None:
                            log(f'product_detail None in json url: {json_backend_url}', product_url)
                            if product_status == 'Error':
                                error_products = error_products + 1
                                to_print = create_error_product(product_data)
                                variations_products = variations_products + write_to_file(f, to_print, head_lines, {'firstTimeAutoshipPrice': None if 'autoshipPrice'  not in product_data.keys() else product_data['autoshipPrice']})

                            if product_status == 'normal' and check_exist(products_links_list, product_url) == False:
                                products_links_list.append({'url': product_url, 'status': 'Error'})
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
                        
                        try:
                            attribute_values_key = [key for key in product.keys() if 'attributeValues' in key][0]
                        except:
                            attribute_values_key = None
                        
                        try:
                            try:
                                images = [image for _, image in product['fullImage'].items() if image != 'Image'][1]
                            except:
                                images = ''

                            try:
                                advertised_price =  product['advertisedPrice'].replace('$','')
                            except:
                                advertised_price = None

                            data.update({
                                "entryID": None if 'entryID' not in product.keys() else product['entryID'],
                                "name": product['name'],
                                "attributeValues": None if attribute_values_key == None else product[attribute_values_key], 
                                "url": product_active_url,
                                "advertisedPrice": advertised_price,
                                "autoShipDiscountPercent": get_feature_flags(detail_json, 'autoshipFirstTimeDiscountPercent'),
                                "mapSavings": None if 'mapSavings' not in product_detail.keys() else product_detail['mapSavings'],                            
                                "descriptionAttributes": {},
                                "mapEnforced": None if 'mapEnforced' not in product_detail.keys() else product_detail['mapEnforced'],                            
                                "autoshipBuyboxOverrideConflictingPromos": get_feature_flags(detail_json, 'autoshipBuyboxOverrideConflictingPromos'),
                                "autoshipSuppressFTASList": get_feature_flags(detail_json, 'autoshipSuppressFTASList'),
                                "inStock": False if 'inStock' not in product.keys() else product['inStock'],
                                "gtin": '000000000' if 'gtin' not in product.keys() else f"{str(product['gtin'])}" if product['gtin'] != None else '000000000',
                                "images" : images, 
                                "partNumber": None if 'partNumber' not in product.keys() else product['partNumber'],
                                "isPrescription": None if 'isPrescription' not in product.keys() else product['isPrescription'],
                            })
                            if 'descriptionAttributes' in product_detail.keys():
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
                                'Status': 'normal',
                                'Reference': product_url, 
                                'Product Code': data['entryID'],
                                'Sku': data['partNumber'],
                                'url': data['url'],
                                'Product Name': data['name'],
                                'Price': data['advertisedPrice'],
                                'Stock': 'Instock' if data['inStock'] else 'Out of Stock', 
                                'Breadcrumb': breadcrumb,
                                'Shipping': None if data['advertisedPrice'] == None else 0 if float(data['advertisedPrice']) > 49 else '4.95',
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
                                'msrp': None if 'strikeThroughPrice' not in data.keys() else data['strikeThroughPrice'].replace('$','') if data['strikeThroughPrice'] != None else '',
                                'gtin': f"0000000000000{data['gtin']}"[-14:],
                            }

                            variations_products = variations_products + write_to_file(f, to_print, head_lines, data)
                            if head_lines == False:
                                head_lines = True

                            report = {
                                'uuid': process_uuid, 
                                'total': unique_products, 
                                'variations': variations_products, 
                                'errors': error_products, 
                                'category': category, 
                                'page_init': pageInit, 
                                'page_end': pageEnd
                            }

                            print(report)
                            url_done.add(product_active_url)
                        except Exception as e:
                           print(traceback.format_exc())
                           if product_status == 'Error':
                                to_print = create_error_product(product_data)
                                variations_products = variations_products + write_to_file(f, to_print, head_lines, {'firstTimeAutoshipPrice': None if 'autoshipPrice'  not in product_data.keys() else product_data['autoshipPrice']})
                                error_products = error_products + 1
                           if product_status == 'normal' and check_exist(products_links_list, product_url) == False:
                               products_links_list.append({'url': product_url, 'status': 'Error'})
                           print('Error A', e)
                           print(traceback.format_exc())
                except KeyboardInterrupt:
                    exit(0)
                except Exception as e:
                    print(traceback.format_exc())
                    if product_status == 'Error':
                        error_products = error_products + 1
                        to_print = create_error_product(product_data)
                        variations_products = variations_products + write_to_file(f, to_print, head_lines, {'firstTimeAutoshipPrice': None if 'autoshipPrice'  not in product_data.keys() else product_data['autoshipPrice']})

                    if product_status == 'normal' and check_exist(products_links_list, product_url) == False:
                        products_links_list.append({'url': product_url, 'status': 'Error'})
                    log(f'Error in B parte of code {str(e)}')
                    print('Error B', e)



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
    parser.add_argument("--proxy", "-x", help='[OPTIONAL] Proxy "https://user:pass@proxy_host:prox_port" or "hosting:port"', type=str, default='')
    parser.add_argument("--sufix",  help='[OPTIONAL] Use only for runners', type=str, default='')
    parser.add_argument("--promo",  help='[OPTIONAL] Use only for runners', type=str, default='')

    args=parser.parse_args()
    if args.category == None:
        print(parser.format_help())
        print('Finish')
        exit(0)

    if args.category not in categories.keys():
        print(f'\n\n\nInvalid param "{args.category}"\n\n')
        print(parser.format_help())
        print('Finish')
        exit(0)
    if args.file == None:
        args.file=f"{args.category}_chewy_{args.percentage}_{file_time}.csv"

    data = {}
    if args.sufix != '' and args.promo != '':
        data = {
                'sub_header': args.promo,
                'sufix': args.sufix,
        }

    main(categories[args.category], args.percentage, f'{path}/{args.file}', args.proxy, data)

    print("Start Time =", start_time)
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)
    print('Finish')

