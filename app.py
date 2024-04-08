import requests
import json
import time 
import csv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from datetime import datetime

now = datetime.now()

start_time = now.strftime("%H:%M:%S")



def get_path(url):
    options = webdriver.ChromeOptions()
    #options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)

    driver.get(url)

    time.sleep(5)
    driver.save_screenshot('image.png')
    elem = driver.find_element("xpath", "//*")
    source_code = elem.get_attribute("outerHTML")
    driver.quit()
    return source_code.split('chewy-pdp-ui-')[1].split('/')[0]

def useFirstTimeAutoshipDiscount(advertisedPrice, autoshipFirstTimeDiscountPercent, autoshipFirstTimeDiscountMaxSavings):
    if advertisedPrice == None:
        return
    discountedPrice = float(advertisedPrice) * (1 - (float(autoshipFirstTimeDiscountPercent) / 100))
    maxSavingsPrice = float(advertisedPrice) - float(autoshipFirstTimeDiscountMaxSavings)
    if maxSavingsPrice > discountedPrice:
        return "%.2f" % maxSavingsPrice
    else:
        return "%.2f" % discountedPrice


path = get_path('https://www.chewy.com/hills-science-diet-kitten-tender/dp/244608')
print(path)
#exit(0)
#sufix = 'PpXgC7yTiuRq'
sufix = path
time.sleep(5)
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
    'groupId': '288',
}

session = requests.Session()
response = session.get('https://www.chewy.com/', headers=headers)
cookies = { 'KP_UIDz-ssn': f"{response.cookies.get_dict()['KP_UIDz-ssn']};" }

index = 0

head_lines = False
f_name = 'chewy_com_demo.csv'

print('\n\n\n\n\n\n\n')
with open(f_name, 'a') as f:
    for i in range(0,278):
        params['from'] = f'{i * 36}'
        response = requests.get('https://www.chewy.com/plp/api/search', params=params, cookies=cookies, headers=headers)
        json_data = json.loads(response.text)
        data_list = json_data['products']
        for item in data_list:
            try:
                index = index + 1
                del item['itemAnalytics']
                item_data = {'line': index}
                #item['href'] = 'https://www.chewy.com/pedigree-complete-nutrition-grilled/dp/141433'
                #item['href'] = 'https://www.chewy.com/pedigroee-choice-cuts-in-gravy-steak/dp/141595'
                #item['href'] = 'https://www.chewy.com/bravecto-chew-dogs-44-88-lbs-blue-box/dp/172909'
                url = f'https://www.chewy.com/_next/data/chewy-pdp-ui-{sufix}/en-US/{item["href"].replace("https://www.chewy.com/", "")}.json'
                time.sleep(1/2)
                internal = requests.get(url, cookies=cookies, headers=headers)
                detail_json = json.loads(internal.content)
                autoshipFirstTimeDiscountPercent  = 0
                try:
                    autoshipFirstTimeDiscountPercent = float(detail_json['pageProps']['__APOLLO_STATE__']['ROOT_QUERY']['pdp']['featureToggles']['autoshipFirstTimeDiscountPercent'])
                    autoshipFirstTimeDiscountMaxSavings  = float(detail_json['pageProps']['__APOLLO_STATE__']['ROOT_QUERY']['pdp']['featureToggles']['autoshipFirstTimeDiscountMaxSavings'])
                except:
                    autoshipFirstTimeDiscountPercent = 0
                    autoshipFirstTimeDiscountMaxSavings = 0
                
                apollo = [detail_json['pageProps']['__APOLLO_STATE__'][product] for product in detail_json['pageProps']['__APOLLO_STATE__'] if "Item" in product]
                apollo_product = [detail_json['pageProps']['__APOLLO_STATE__'][product] for product in detail_json['pageProps']['__APOLLO_STATE__'] if "Product" in product][0]
                breadcrumb = '/'.join([breadcrumb['name'] for breadcrumb in [detail_json['pageProps']['__APOLLO_STATE__'][product] for product in detail_json['pageProps']['__APOLLO_STATE__'] if "Breadcrumb" in product]])
                product_detail = [key for key  in [main for main in apollo] if 'product' in key][0]
                data = {
                    "slug": apollo_product['slug'],
                    'manufacturerName': apollo_product['manufacturerName'], 
                    "topHeadlinePromotion": product_detail['topHeadlinePromotion'],
                    "autoshipFirstTimeDiscountPercent": autoshipFirstTimeDiscountPercent,
                    'autoPrice': product_detail['autoshipPrice'],
                    "isAutoshipAllowed": product_detail['isAutoshipAllowed'],
                    "autoshipDiscountPct": product_detail['autoshipDiscountPct'],
                    "autoshipFirstTimeDiscountMaxSavings": autoshipFirstTimeDiscountMaxSavings,
                    "rating": apollo_product['rating'],
                    "ratingCount": apollo_product['ratingCount'],
                    "recommendedRatingCount": apollo_product['recommendedRatingCount'],
                    "recommendedRatingPercent": apollo_product['recommendedRatingPercent'],
                    "description": product_detail['description'],
                    "isHealthCare": product_detail['isHealthCare'],
                    "maxQuantity": product_detail['maxQuantity'],
                    "isPersonalized": product_detail['isPersonalized'],
                    "isVetDiet": product_detail['isVetDiet'],
                    "isSinglePill": product_detail['isSinglePill'],
                    "strikeThroughPrice": product_detail['strikeThroughPrice'],
                    "strikeThroughPriceType": product_detail['strikeThroughPriceType'],
                    "strikeThroughSavings": product_detail['strikeThroughSavings'],
                    "strikeThroughSavingsPct": product_detail['strikeThroughSavingsPct'],
                    "shippingMessage":product_detail['shippingMessage'],
                    "shippingTimeframe":product_detail['shippingTimeframe'],
                    "dropshipMessage":product_detail['dropshipMessage'],
                    "rxShippingMessage":product_detail['rxShippingMessage'],
                    "isAutoshipAllowed":product_detail['isAutoshipAllowed'],
                    "isFrozen":product_detail['isFrozen'],
                    "isFresh":product_detail['isFresh'],
                    "isBundle":product_detail['isBundle'],
                    "dimensions":product_detail['dimensions'],
                    "weight":product_detail['weight'],
                    "isRefrigerated":product_detail['isRefrigerated'],
                    "isRestricted":product_detail['isRefrigerated'],
                }
                try:
                    data["topPromotion"] = product_detail['topPromotion']['__ref'].split(':')[1]
                except:
                    data["topPromotion"] = None


                for product in apollo:
                    try:
                        try:
                            images = [image for _, image in product['fullImage'].items() if image != 'Image'][1]
                        except:
                            images = ''
                        complete = {
                            "entryID": product['entryID'],
                            "name": product['name'],
                            "url": f"{'/'.join(item['href'].split('/')[:-1])}/{product['entryID']}",
                            "advertisedPrice": product['advertisedPrice'].replace('$',''),
                            "autoShipDiscountPercent": detail_json['pageProps']['__APOLLO_STATE__']['ROOT_QUERY']['pdp']['featureToggles']['autoshipFirstTimeDiscountPercent'],
                            "mapSavings": product_detail['mapSavings'],                            
                            "mapEnforced": product_detail['mapEnforced'],                            
                            "autoshipBuyboxOverrideConflictingPromos": detail_json['pageProps']['__APOLLO_STATE__']['ROOT_QUERY']['pdp']['featureToggles']['autoshipBuyboxOverrideConflictingPromos'],
                            "autoshipSuppressFTASList": detail_json['pageProps']['__APOLLO_STATE__']['ROOT_QUERY']['pdp']['featureToggles']['autoshipSuppressFTASList'],
                           "inStock": product['inStock'],
                            "images" : images, 
                            "partNumber": product['partNumber'],
                            "isGiftCard": product['isGiftCard'],
                            "isPrescription": product['isPrescription'],
                            "isPublished": product['isPublished'],
                            "isUnavailable": product['isUnavailable'],
                            "perUnitPrice": product['perUnitPrice'],
                            "unitOfMeasure": product['unitOfMeasure'],
                        }
                        complete.update(data)
                        complete["firstTimeAutoshipPrice"] = useFirstTimeAutoshipDiscount(complete['advertisedPrice'], complete['autoShipDiscountPercent'], complete['autoshipFirstTimeDiscountMaxSavings'])

                        
                        isConflitPromo = False
                        if complete['topPromotion'] in complete['autoshipBuyboxOverrideConflictingPromos'] and complete['topPromotion'] != None and complete['autoshipBuyboxOverrideConflictingPromos'] != None:
                            isConflitPromo = True
                        complete['isConflitPromo']  = isConflitPromo
                        mapRestricted  = complete['mapEnforced']  and complete['mapSavings'] != None
                        complete['mapRestricted'] = mapRestricted
                        isFTASRepressedSku = int(complete['partNumber']) in complete['autoshipSuppressFTASList'] if complete['autoshipSuppressFTASList'] != None else False
                        complete['isFTASRepressedSku'] = isFTASRepressedSku
                        display = True
                        if complete['isAutoshipAllowed'] == False:
                            complete['firstTimeAutoshipPrice'] = None
                        else:
                            display = not (complete['topHeadlinePromotion'] == None and complete['isConflitPromo'] == False and complete['mapRestricted'] == False and complete['isFTASRepressedSku'] == False)
                            if display == False:
                                complete['firstTimeAutoshipPrice'] = complete['advertisedPrice']    

                        to_print={
                            'Product Code': complete['partNumber'],
                            'url': complete['url'],
                            'Product Name': complete['name'],
                            'Price': complete['advertisedPrice'],
                            'Stock': 'Instock' if complete['inStock'] else 'Out of Stock', 
                            'Breadcrumb': breadcrumb,
                            'Shipping': 0 if float(complete['advertisedPrice']) > 49 else '4.95',
                            'Image': complete['images'],
                            'Brand': complete['manufacturerName']
                        }
                        print(json.dumps(to_print, indent=4))
                        writer = csv.DictWriter(f, fieldnames=to_print)

                        if head_lines == False:
                            head_lines = True
                            writer.writeheader()
                        writer.writerow(to_print)
                        if complete['firstTimeAutoshipPrice'] != None:
                            to_print['Product Name'] = f"{complete['name']} - Autosend"
                            to_print['Price'] = complete['firstTimeAutoshipPrice']
                            print('--------')
                            print(json.dumps(to_print, indent=4))
                            writer.writerow(to_print)
                        #print(f"{index}: {item['href']}: {product['name']}")
                    except Exception as e:
                        print(e)
                        pass
            except KeyboardInterrupt:

                exit(0)
            print('--------')
    time.sleep(2)
# start time = 02:15
current_time = now.strftime("%H:%M:%S")
print("Start Time =", start_time)
print("Current Time =", current_time)

