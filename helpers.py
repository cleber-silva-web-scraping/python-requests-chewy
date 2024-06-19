
import requests
import traceback
import json
import time 
import csv
import math
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
from selenium.webdriver.firefox.options import Options

start_time = datetime.now()
time.sleep(5)
total_requests = 0
def display_time():
    global total_requests
    total_requests = total_requests + 1
    end_time = datetime.now()
    avg =  '%.2f' % ((end_time - start_time).total_seconds() / total_requests)
    print(f'{avg}s per request')

path = '/'.join(__file__.split('/')[:-1])
def get_cookies(headers, proxy):
    proxies = { 'https' : proxy } 
    cookies = None
    max_try = 5
    while max_try > 0:
        try:
            session = requests.Session()
            if proxy != '':
                response = session.get('https://www.chewy.com/', headers=headers, proxies=proxies, timeout=25)
            else:
                response = session.get('https://www.chewy.com/', headers=headers, timeout=26)
            cookies = { 'KP_UIDz-ssn': f"{response.cookies.get_dict()['KP_UIDz-ssn']};" }
            max_try = 0
        except Exception as e:
            time.sleep(3)
            max_try = max_try - 1
    display_time()
    return cookies
def check_exist(rows, value):
    for row in rows:
        if row['url'] == value and row['status'] == 'Error':
            return True
    return False

def create_error_product(product_data, min_price, price_is):
    try:
     to_print={
        'Product Code': '',
        'Sku': product_data['partNumber'],
        'url': product_data['href'],
        'Price': product_data['price'],  
        'Shipping': None if product_data['advertisedPrice'] == None else 0 if (1.00 * float(product_data['advertisedPrice'])) > float(min_price) else price_is,
        'Product Name': product_data['name'],
        'Stock': 'Instock' if product_data['inStock'] else 'Out of Stock', 
        'Breadcrumb': '',
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
        'msrp': None if 'strikePrice' not in product_data.keys() else product_data['strikePrice'].replace('$','').replace(',','') if product_data['strikePrice'] != None else '',
        'gtin': f"00000000000000",
     }
     return to_print
    except:
        return None
    


def get_total_pages(params, cookies, headers, proxy = None):
    proxies = { 'https' : proxy } 
    max_try = 5
    total = None
    while max_try > 0:
        try:
            if proxy != None:
                response = requests.get('https://www.chewy.com/plp/api/search', params=params, cookies=cookies, headers=headers, proxies=proxies, timeout=27)
            else:
                time.sleep(1/2)
                response = requests.get('https://www.chewy.com/plp/api/search', params=params, cookies=cookies, headers=headers, timeout=28)
            json_data = json.loads(response.text)
            total =  math.ceil(float(json_data['recordSetTotal']) / 36)
            max_try = 0
        except:
            time.sleep(2)
            max_try = max_try - 1
    display_time()
    return total

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

    display_time()
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
    display_time()
    return detail_prd_json

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
        for attr in atributes:
            try:
                id = attr['__ref'].split('id":')[1].split(',')[0]
                if int(id) > 0:
                    if ":" in size_arr[id]:
                        return f'{size_arr[id]}'.split(':')[1].strip()
                    return size_arr[id].strip()
            except: 
                pass
        return ''

def get_sub_header():
    max_try = 5
    data = None
    while max_try > 0:
        options = Options()
        options.add_argument("--headless")
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-urlfetcher-cert-requests')
        options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(options=options)
        try:
            driver.get('https://www.chewy.com/')
            time.sleep(5)
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
        except Exception as e:
            time.sleep(1000)
            time.sleep(3)
            max_try = max_try -1
        finally:
            driver.quit()

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
            data = {
                    'sufix': str(source_code).split('chewy-pdp-ui-')[1].split('/')[0],
                    'min_price': str(source_code).split('autoshipFirstTimeDiscount","value":"')[1].split('"')[0],
                    'price_is': str(source_code).split('shipping is $')[1].split('. ')[0],
            }
            driver.quit()
            max_try = 0
        except:
            time.sleep(3)
            max_try = max_try - 1

    return data

def write_to_file(f, to_print, head_lines, data = None):
    if to_print == None:
        return 0

    writer = csv.DictWriter(f, fieldnames=to_print)

    if head_lines == False:
        writer.writeheader()

    to_print = remove_break_lines(to_print)
    writer.writerow(to_print)
    variations_products = 1

    if data != None and 'firstTimeAutoshipPrice' in data.keys() and data['firstTimeAutoshipPrice'] != None:
        variations_products = variations_products + 1
        to_print['Product Name'] = f"{data['name']} - Autosend"
        to_print['Price'] = data['firstTimeAutoshipPrice'].replace('$', '').replace(',','')
        to_print['Shipping'] = 0
        to_print = remove_break_lines(to_print)
        writer.writerow(to_print)

    return variations_products

def remove_break_lines(dictionary):
    try:
        for key in dictionary.keys():
            dictionary[key] = None if dictionary[key] == None else re.sub("\n|\r", " ", f'{dictionary[key]}').strip()
    except:
        pass

    return dictionary

def log(message, product_url=None):
    log_now = datetime.now()
    log_time = log_now.strftime("%H:%M:%S")
    f = open(f"{path}/process.log", "a")
    f.write(f'[{log_time}] {message}\n')
    f.close()
    if product_url:
        f = open(f"{path}/url_error.log", "a")
        f.write(f'{product_url}\n')
        f.close()
