import os
import time
from subprocess import PIPE, Popen
from threading import Thread
from datetime import datetime

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

f = open("proxy.list", "r")
proxies = [p for p in f.read().split('\n') if p != '']

commands = [] 

for pet in ['dog']:
    pets = [['python', 'app.py', '-c', pet,  '-p',  f'{index*2}-{(index+1)*2}', '--proxy', proxies.pop()] for index in range(0,50)]
    for pet in pets:
        commands.append(pet)


# for pet in ['dog', 'cat']:
#     pets = [['python', 'app.py', '-c', pet,  '-p',  f'{index*5}-{(index+1)*5}', '--proxy', f"{'.'.join(proxies.pop().split('.')[:-1])}.xxx:8080"] for index in range(0,20)]
#     for pet in pets:
#         commands.append(pet)
# 
# 
# for pet in ['fish', 'bird', 'small-pet', 'reptile', 'horse', 'pharmacy', 'farm-animal']:
#     pets = [['python', 'app.py', '-c', pet,  '-p',  f'{index*10}-{(index+1)*10}', '--proxy', f"{'.'.join(proxies.pop().split('.')[:-1])}.xxx:8080"] for index in range(0,10)]
#     for pet in pets:
#         commands.append(pet)
# 
# 

for cmd in commands:
    print(' '.join(cmd))

exit(0)

now = datetime.now()
start_time = now.strftime("%H:%M:%S")
threads = []

for index, cmd in enumerate(commands):
    threads.append(Thread(target=run_command, args=(cmd,(index * 20))))

for t in threads:
    t.start()

for t in threads:
    t.join()

now = datetime.now()
end_time = now.strftime("%H:%M:%S")

print(f'Start at : {start_time}')
print(f'End at : {end_time}')

