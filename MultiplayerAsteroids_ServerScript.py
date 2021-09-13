import socket
import threading
import json

import time

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
threadLock = threading.Lock()    
    
clients = {}
numClients = 0

def connectionLoop():
    while True:
        threadLock.acquire()

        byteArr, addr = serverSocket.recvfrom(1024)

        #print(byteArr)    

        data = json.loads(byteArr.decode())

        if data['command'] == 1:
            print("Connection request . . .")
        
            global numClients

            clients[numClients] = {}
            clients[numClients]['address'] = addr
            clients[numClients]['networkID'] = numClients
            clients[numClients]['position'] = data['pos']

            print("Client says: ", data['msg'])


            msg = {}
            msg['command'] = 2  # recieving a network ID
            msg['netID'] = clients[numClients]['networkID']
            
            time.sleep(0.5)
            
            serverSocket.sendto(json.dumps(msg).encode('utf-8'), addr)

            time.sleep(0.5)

            # Step 1: Inform new client of all clients in this match
            msg2 = {}
            msg2['command'] = 3
            msg2['subclients'] = []
        
            for c in clients.keys():
                msg2['subclients'].append({"netID": clients[c]['networkID'], "pos": data['pos']})
        
            serverSocket.sendto(json.dumps(msg2).encode('utf-8'), addr)

            time.sleep(0.5)

            # Step 2: Inform all OTHER clients of the new client that just joined
            msg3 = {}
            msg3['command'] = 4
            msg3['subclient'] = {}

            #for c in clients.keys():
               #if clients[c]['networkID'] != numClients:
            msg3['subclient'] = {"netID": clients[numClients]['networkID']}

            for c in clients.keys():
               if clients[c]['networkID'] != numClients:
                   serverSocket.sendto(json.dumps(msg3).encode('utf-8'), clients[c]['address'])

            
            numClients += 1
        # Update clients position on server
        elif data['command'] == 5:
            #print(data)
            clients[data['client']['netID']]['position'] = data['client']['pos']

            msg4 = {}
            msg4['command'] = 6
            msg4['subclients'] = []
            

            for c in clients.keys():
                msg4['subclients'].append({"netID": clients[c]['networkID'], "pos": clients[c]['position'] })
            
            print(msg4)

            # Inform other clients about this clients new position
            for c in clients.keys():
                serverSocket.sendto(json.dumps(msg4).encode('utf-8'), clients[c]['address'])
        # Drop request
        elif data['command'] == 7:
            print("Client requesting to drop . . .")

            msg5 = {}
            msg5['command'] = 8
            msg5['netID'] = data['netID']

            for c in clients.keys():
                serverSocket.sendto(json.dumps(msg5).encode('utf-8'), clients[c]['address'])

            time.sleep(0.5)

            del clients[data['netID']]

    
        threadLock.release()



if __name__ == "__main__":

    # Local IP at port 12345
    serverSocket.bind(('', 12345))

    mainThread = threading.Thread(target=connectionLoop, args=(), daemon=False)
    mainThread.start()
    mainThread.join()
