from flask import Flask
from flask import jsonify
from flask import request

import sys
import time
import threading
from queue import Queue


class Action(threading.Thread):

    def __init__(self):
        super().__init__(target=self.run)
        self.queue = Queue()

    def send(self, msg):
        self.queue.put(msg)
        # print(f"sent: {msg}")  # DEBUG

    # def close(self):
    #     print()  # DEBUG
    #     self.send('STOP')

    def run(self):
        for msg in iter(self.queue.get, 'STOP'):
            pass


class PrintAction(Action):
    def run(self):
        for msg in iter(self.queue.get, 'STOP'):
            print(f"UPDATE NOTIFICATION: {msg}")  # DEBUG


    

app = Flask(__name__)

@app.route('/', methods=['GET'])
def update_notifier():
    args = request.args
    pa = PrintAction()
    pa.start()
    pa.send(args)
    time.sleep(2)
    pa.join()
    # print(args)
    return jsonify({'message' : 'The update request sent successfully !'})

if __name__ == "__main__":
    app.run(debug=True)