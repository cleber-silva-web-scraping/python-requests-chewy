import os
import json
import time
import re
from subprocess import PIPE, Popen
from threading import Thread
from datetime import datetime
from helpers import get_path, get_sub_header

reports = {}
path = '/'.join(__file__.split('/')[:-1])
line_done = set()

def consolidate():
    headers = ['Product Code,Sku,url,Price,Shipping,Product Name,Stock,Breadcrumb,Image,Brand,generic_name,product_form,drug_type,prescription_item,autoship,promotional_text,promotional_information,pack_size,msrp,gtin\n']
    pets =  ['dog', 'cat', 'fish', 'bird', 'small-pet', 'reptile', 'horse', 'pharmacy', 'farm-animal']
    file_time = datetime.now().strftime("%y%m%d%H")

    f = open(f'{path}/chewy_all_{file_time}.csv', "w")
    f.writelines(headers)
    f.close()

    for file in os.listdir(path):
        if '_chewy_' in file and file.endswith(".csv"):
            pet = file.split('_chewy_')[0]
            if pet in pets:
                f = open(f'{path}/{file}')
                lines = [l for l in f.read().split('\n') if l != '']
                for line in lines:
                    if f'{pet}|{line}' not in line_done and 'generic_name' not in line:
                        line_done.add(f'{line}')
                        f_append = open(f'{path}/chewy_all_{file_time}.csv', 'a')
                        f_append.write(f'{line}\n')
                        f_append.close()
                f.close()
                os.unlink(f"{path}/{file}")

def run_command(command, wait):
   time.sleep(wait)
   os.environ['PYTHONUNBUFFERED'] = '1'
   process = Popen(command, shell=False, stdout=PIPE, env=os.environ) # Shell doesn't quite matter for this issue
   while True:
      output = process.stdout.readline()
      if process.poll() is not None:
         break
      if output:
            line = output.decode('utf-8')
            if 'uuid' in line:
                data = json.loads(line.replace("'", '"'))
                print(data)
   rc = process.poll()
   return rc

f = open(f"{path}/proxy.list", "r")
proxies = [p for p in f.read().split('\n') if p != '']
proxies.reverse()
f.close()
commands = [] 

sub_header = get_sub_header()
if sub_header == None:
    print(f'Fatal error headers')
    print('Finish')
    exit(0)

site_data = get_path(sub_header['url'])
print(site_data)
if site_data == None or site_data['sufix'] == None:
    print(f'Fatal error sufix')
    print('Finish')
    exit(0)


sufix = site_data['sufix']
min_price = site_data['min_price']
price_is = site_data['price_is']

promo = re.sub("\n|\r", " ", f"{sub_header['sub_header']}").strip()

for pet in ['dog', 'cat']:
    pets = [['python', f'{path}/app.py', '--min_price', min_price, '--price_is', price_is, '-c', pet,  '-p',  f'{index*2}-{(index+1)*2}', '--sufix', sufix, '--promo', f"\"{promo}\"", '--proxy', proxies.pop()] for index in range(0,50)]
    for pet in pets:
        commands.append(pet)


for pet in ['pharmacy', 'fish', 'bird', 'small-pet', 'reptile', 'horse',  'farm-animal']:
    pets = [['python', f'{path}/app.py', '--min_price', min_price, '--price_is', price_is, '-c', pet,  '-p',  f'{index*5}-{(index+1)*5}', '--sufix', sufix, '--promo', f"\"{promo}\"", '--proxy', proxies.pop()] for index in range(0,20)]
    for pet in pets:
        commands.append(pet)
 
now = datetime.now()
start_time = now.strftime("%H:%M:%S")
threads = []

for index, cmd in enumerate(commands):
    threads.append(Thread(target=run_command, args=(cmd,(0))))

for t in threads:
    t.start()

for t in threads:
    t.join()

consolidate()

now = datetime.now()
end_time = now.strftime("%H:%M:%S")

print(f'Start at : {start_time}')
print(f'End at : {end_time}')

