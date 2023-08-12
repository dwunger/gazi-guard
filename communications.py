from abstract_message import AbstractMessage
import time
import sys
import threading
import os
def cls():
    if os.name == 'posix':  # Unix-like (Linux, macOS)
        os.system('clear')
    elif os.name == 'nt':   # Windows
        os.system('cls')
class CommsManager():
    def __init__(self):
        self.running = False
        self.listener_thread = None
        self.message = AbstractMessage()
        self.inbox = {}
    def request(self,item):
        self.send_message(self.message.request(item))
        
        while item not in self.inbox:
            time.sleep(0.01)
        return self.inbox[item]
            
        
    def listen(self):
        '''starts daemon thread '''
        self.running = True
        self.listener_thread = threading.Thread(target=self._listen)
        self.listener_thread.daemon = True
        self.listener_thread.start()

    def stop(self):
        self.running = False
        if self.listener_thread is not None:
            self.listener_thread.join()

    def _listen(self):
        while self.running:
            # Receive messages from the frontend
            stdin = sys.stdin.readline().strip()
            stdin = [line.strip('*') for line in stdin.split('\n') if line.startswith('*')]
            # logger_iter(stdin)
            for line in stdin:
                # Process the received message
                response = self.process_message(line)
                # Send the response back to the frontend
                if response:
                    self.send_message(response)
            
    def process_message(self, data):
        # Add your custom logic here based on the received message
   
        payload_type, payload = data.split(":")
        
        return self.compose_response(payload_type, payload)
    

    def send_message(self, response):
        # Send the response back to the frontend
        
        print(response, flush=True)
        sys.stdout.flush()
        sys.stderr.flush()

    def compose_response(self, payload_type, payload):
        #map message type and payload to a response for return value
        #start with exhaustive switching
        if payload_type == 'request':
            if payload == 'pid':
                return self.message.pid(os.getpid())
        if payload_type == 'pid':
            #no response
            self.inbox[payload_type]=int(payload)
            return None
            