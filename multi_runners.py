import os
import time
from subprocess import PIPE, Popen
from threading import Thread
from datetime import datetime

path = '/'.join(__file__.split('/')[:-1])
line_done = set()
def consolidate():
    headers = ['Product Code,Sku,url,Product Name,Price,Stock,Breadcrumb,Shipping,Image,Brand,generic_name,product_form,drug_type,prescription_item,autoship,promotional_text,promotional_information:,pack_size,msrp,gtin\n']
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


def run_command(command, wait):
   time.sleep(wait)
   print('STARTING NEW PROCESS ***')
   os.environ['PYTHONUNBUFFERED'] = '1'
   process = Popen(command, shell=False, stdout=PIPE, env=os.environ) # Shell doesn't quite matter for this issue
   while True:
      output = process.stdout.readline()
      if process.poll() is not None:
         break
      if output:
         print(output.decode("utf-8").replace('\n',''))
   rc = process.poll()
   return rc

f = open(f"{path}/proxy.list", "r")
proxies = [p for p in f.read().split('\n') if p != '']
f.close()
commands = [] 

for pet in ['dog', 'cat']:
    pets = [['python', f'{path}/app.py', '-c', pet,  '-p',  f'{index*2}-{(index+1)*2}', '--proxy', proxies.pop()] for index in range(0,50)]
    for pet in pets:
        commands.append(pet)


for pet in ['fish', 'bird', 'small-pet', 'reptile', 'horse', 'pharmacy', 'farm-animal']:
    pets = [['python', f'{path}/app.py', '-c', pet,  '-p',  f'{index*5}-{(index+1)*5}', '--proxy', proxies.pop()] for index in range(0,20)]
    for pet in pets:
        commands.append(pet)


now = datetime.now()
start_time = now.strftime("%H:%M:%S")
threads = []

for index, cmd in enumerate(commands):
    threads.append(Thread(target=run_command, args=(cmd,(index * 20))))

for t in threads:
    t.start()

for t in threads:
    t.join()

consolidate()

now = datetime.now()
end_time = now.strftime("%H:%M:%S")

print(f'Start at : {start_time}')
print(f'End at : {end_time}')

