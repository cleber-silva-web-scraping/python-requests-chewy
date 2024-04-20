import uuid
import traceback
import argparse
import time 
import math
from datetime import datetime

from helpers import get_cookies,  get_total_pages, get_sub_header, get_path, get_size, get_promotion, isConflitPromo
from helpers import get_breadcrumb, get_sizes_list, get_product_links, get_product_items, get_feature_flags, get_product_details, get_product_json_data
from helpers import get_product_general_info, get_description_attribute, create_error_product, log, write_to_file, check_exist
from helpers import useFirstTimeAutoshipDiscount

process_uuid = str(uuid.uuid4())
path = '/'.join(__file__.split('/')[:-1])
now = datetime.now()
start_time = now.strftime("%H:%M:%S")
url_done = set()

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

def main(category, perc, f_name, proxy, runner_data = None):
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

    head_lines = False
    cookies = get_cookies(headers, proxy)
    if cookies == None:
        log('Fatal error cookies = None')
        print('Finish')
        exit(0)

    params['groupId'] = f'{category}'

    total = get_total_pages(params, cookies, headers, proxy)
    if total == None:
        log('Fatal error total = None')
        print('Finish')
        exit(0)

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
            products_links_list = []
            for product_link in products_links_list_main:
                log(f"Main Url: {product_link['href']}")
                product_link.update({'url': product_link['href'], 'status':'normal' })
                products_links_list.append(product_link)

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
                        cookies = get_cookies(headers, proxy)
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
                                advertised_price =  product['advertisedPrice'].replace('$','').replace(',','')
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
                                'msrp': None if 'strikeThroughPrice' not in data.keys() else data['strikeThroughPrice'].replace('$','').replace(',','') if data['strikeThroughPrice'] != None else '',
                                'gtin': f"0000000000000{data['gtin']}"[-14:],
                            }

                            variations_products = variations_products + write_to_file(f, to_print, head_lines, data)
                            if head_lines == False:
                                head_lines = True
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


                report = {
                        'uuid': process_uuid, 
                        'total': unique_products, 
                        'variations': variations_products, 
                        'errors': error_products, 
                        'category': category, 
                        'page_init': pageInit, 
                        'page': i, 
                        'page_end': pageEnd
                    }

                print(report)




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

