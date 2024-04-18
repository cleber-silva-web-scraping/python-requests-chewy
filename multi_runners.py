import os
import json
import time
import re
from subprocess import PIPE, Popen
from threading import Thread
from datetime import datetime
from rich.console import Console
from rich.live import Live
from rich.table import Table
from helpers import get_path, get_sub_header

reports = {}

def create_process_table() -> Table:
    table = Table(
        "Category", "Total", "Expected", "% Done", "Errors", "Files/Proccess"
    )
    categories = {
         '288': 'dog',
         '325': 'cat',
         '885': 'fish',
         '941': 'bird',
         '977': 'small-pet',
        '1025': 'reptile',
        '8403': 'farm-animal',
        '1663': 'horse',
        '2515': 'pharmacy',
    }


    for pet in reports.keys():
        uuids = reports[pet]['records'].keys()
        total = 0
        expected = 0
        done = '0%'
        errors = 0
        files = len(uuids)
        for uuid in uuids:
            total = total + reports[pet]['records'][uuid]['total']
            errors = errors + reports[pet]['records'][uuid]['errors']
            expected = expected + ((reports[pet]['records'][uuid]['page_end'] - reports[pet]['records'][uuid]['page_init']) * 36)
            if expected > 0:
                done = total / expected * 100

        table.add_row(
            categories[pet],
            f'{total}',
            f'{expected}',
            f'{ "%.2f" % done}',
            f'{errors}',
            f'{files}'
        )

    return table




path = '/'.join(__file__.split('/')[:-1])
line_done = set()
def consolidate():
    headers = ['Status, Reference, Product Code,Sku,url,Product Name,Price,Stock,Breadcrumb,Shipping,Image,Brand,generic_name,product_form,drug_type,prescription_item,autoship,promotional_text,promotional_information:,pack_size,msrp,gtin\n']
    pets =  ['dog', 'cat', 'fish', 'bird', 'small-pet', 'reptile', 'horse', 'pharmacy', 'farm-animal']
    for pet in pets:
        f = open(f'{path}/{pet}_all.csv', "w")
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
                        line_done.add(f'{pet}|{line}')
                        f_append = open(f'{pet}_all.csv', 'a')
                        f_append.write(f'{line}\n')
                        f_append.close()
                f.close()
finished = False
def run_command(command, wait):
   global reports, finished 
   time.sleep(wait)
   os.environ['PYTHONUNBUFFERED'] = '1'
   process = Popen(command, shell=False, stdout=PIPE, env=os.environ) # Shell doesn't quite matter for this issue
   while True:
      output = process.stdout.readline()
      if process.poll() is not None:
         break
      if output:
            if 'uuid' in output.decode('utf-8'):
                data = json.loads(output.decode('utf-8').replace("'", '"'))
                print(data)
                if data['category'] not in reports.keys():
                    reports.update({ f"{data['category']}" : { 'records' : {} } })
                reports[f"{data['category']}"]['records'].update({ f"{data['uuid']}" : data })
   rc = process.poll()
   finished = True 
   return rc

f = open(f"{path}/proxy.list", "r")
proxies = [p for p in f.read().split('\n') if p != '']
f.close()
commands = [] 

sub_header = get_sub_header()
if sub_header == None:
    print(f'Fatal error headers')
    print('Finish')
    exit(0)

sufix = get_path(sub_header['url'])
if sufix == None:
    print(f'Fatal error sufix')
    print('Finish')
    exit(0)
promo = re.sub("\n|\r", " ", f"{sub_header['sub_header']}").strip()


for pet in ['dog', 'cat']:
    pets = [['python', f'{path}/app.py', '-c', pet,  '-p',  f'{index*2}-{(index+1)*2}', '--sufix', sufix, '--promo', f"\"{promo}\"", '--proxy', proxies.pop()] for index in range(0,50)]
    for pet in pets:
        commands.append(pet)


for pet in ['pharmacy', 'fish', 'bird', 'small-pet', 'reptile', 'horse',  'farm-animal']:
    pets = [['python', f'{path}/app.py', '-c', pet,  '-p',  f'{index*5}-{(index+1)*5}', '--sufix', sufix, '--promo', f"\"{promo}\"", '--proxy', proxies.pop()] for index in range(0,20)]
    #for pet in pets:
    #    print(' '.join(pet))
    for pet in pets:
        commands.append(pet)

now = datetime.now()
start_time = now.strftime("%H:%M:%S")
threads = []

for index, cmd in enumerate(commands):
    threads.append(Thread(target=run_command, args=(cmd,(index))))

for t in threads:
    t.start()

#for t in threads:
#    t.join()

console = Console()
with Live(console=console, screen=True, auto_refresh=False) as live:
    while finished == False:
        live.update(create_process_table(), refresh=True)
        time.sleep(1)

consolidate()

now = datetime.now()
end_time = now.strftime("%H:%M:%S")

print(f'Start at : {start_time}')
print(f'End at : {end_time}')

