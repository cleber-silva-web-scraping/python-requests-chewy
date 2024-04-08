from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

class Handler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.split('/')[-1] == "app.py":
            proc = subprocess.Popen(['python', 'app.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            print(str(proc.communicate()[0]).replace('\\n', '\n'))

observer = Observer()
observer.schedule(Handler(), ".")
observer.start()


try:
    while True:
        pass
except KeyboardInterrupt:
    observer.stop()

observer.join()

