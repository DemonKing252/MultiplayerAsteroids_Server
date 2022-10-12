from pydoc import cli
import threading
import json
import socket
import time

bullets = {}
clients = {}
matches = []

clientsConnected = 0
bulletId = 0

match = {'numBullets': 0, 'numAsteroids': 0 }
id1 = {}
id2 = {}

def getMatchWithId(id):
    global matches
    for i in range(len(matches)):
        if matches[i]['client1']['id'] == id or matches[i]['client2']['id'] == id:
            return matches[i], i
    
    return -1, -1

def gameLoop():
    while True:
        mutex.acquire()

        byte, addr = sock.recvfrom(4096)
        
        s = byte.decode()
        clientMsg = json.loads(s)
        global clientsConnected
        global bulletId
        global id1
        global id2
        global match
        cmd = clientMsg['commandSignifier']

        if cmd == 0:  # Hand shake
            clients[clientsConnected] = {}
            clients[clientsConnected]['addr'] = addr
            clients[clientsConnected]['pos'] = { 'x': 0.0, 'y': 0.0 }

            global id1
            global id2
            global match
            
            data = { 'commandSignifier': 1, 'id': clientsConnected }
            sock.sendto(json.dumps(data).encode('utf-8'), addr)
      
            print('client joined with id: ', clientsConnected)
            clientsConnected += 1
        # Request matchmaking
        if cmd == 2:

            cli_id = clientMsg['clientId']
            
            print('client id joined the match, giving id = ', cli_id)

            if 'id' in id2.keys():
                id1 = {'id': cli_id, 'addr': addr}
                match['client1'] = id1
                id1 = {}
                id2 = {}
                matches.append(match)

                data = {'commandSignifier': 100, 'message': 'Match has been made!', 'id1': match['client1']['id'], 'id2': match['client2']['id'], 'player': '1' }
                sock.sendto(json.dumps(data).encode('utf-8'), match['client1']['addr'])
                
                data = {'commandSignifier': 100, 'message': 'Match has been made!', 'id1': match['client1']['id'], 'id2': match['client2']['id'], 'player': '2' }
                sock.sendto(json.dumps(data).encode('utf-8'), match['client2']['addr'])

                match = {'numBullets': 0, 'numAsteroids': 0 }
            else:
                id2 = {'id': cli_id, 'addr': addr}
                match['client2'] = id2

                
            ids = []
            for i in matches:
                ids.append(i['client1']['id'])
                ids.append(i['client2']['id'])
            print('matches ids: ', ids)  
        # Position update
        elif cmd == 4: 
            our_match, idx = getMatchWithId(clientMsg['clientId'])

            if 1 == 1:
                ids = []
                for i in matches:
                    ids.append(i['client1']['id'])
                    ids.append(i['client2']['id'])

                print('matches ids: ', ids)                

                if clientMsg['playerId'] == 1:
                    data = {'commandSignifier': 5, 'pos': clientMsg['pos'], 'playerId': 1}
                    sock.sendto(json.dumps(data).encode('utf-8'), our_match['client2']['addr'])
                else:                
                    data = {'commandSignifier': 5, 'pos': clientMsg['pos'], 'playerId': 2}
                    sock.sendto(json.dumps(data).encode('utf-8'), our_match['client1']['addr'])

        
        # Client dropped
        elif cmd == 6:
            dropClient = {'commandSignifier': 7, 'id': clientMsg['netId']}

            for c in clients.keys():
                if clients[c]['addr'] == addr:
                    del clients[c]
                    break
            
            our_match, idx = getMatchWithId(clientMsg['netId'])
            if 1 == 1:
                if our_match != -1: # This was the last match found, so we dont need to tell any clients to disconnect.
                    if clientMsg['playerId'] == 1:
                        sock.sendto(json.dumps(dropClient).encode('utf-8'), our_match['client2']['addr'])
                    elif clientMsg['playerId'] == 2:
                        sock.sendto(json.dumps(dropClient).encode('utf-8'), our_match['client1']['addr'])

                    matches.pop(idx)
                else:
                    id1 = {}
                    id2 = {}
                    our_match = {'numBullets': 0, 'numAsteroids': 0}
        # Spawn bullet by client
        elif cmd == 8:
            our_match, idx = getMatchWithId(clientMsg['netId'])

            id = our_match['numBullets']
            our_match['numBullets'] += 1
            data = { 'commandSignifier': 9, 'playerId': clientMsg['playerId'], 'bullet':  {'id': id, 'pos': clientMsg['pos'], 'vel': clientMsg['vel'] }}
            
            sock.sendto(json.dumps(data).encode('utf-8'), our_match['client1']['addr'])
            sock.sendto(json.dumps(data).encode('utf-8'), our_match['client2']['addr'])
                
        # Delete bullet out of bounds, eventually bullets that hit asteroids too.
        elif cmd == 10:            
            our_match, idx = getMatchWithId(clientMsg['netId'])
            if our_match != -1:
                bullet_id = clientMsg['bullet']['id']
                data = {'commandSignifier': 11, 'playerId': clientMsg['playerId'], 'bullet': {'id': bullet_id, 'pos': clientMsg['bullet']['pos'], 'vel': clientMsg['bullet']['vel']}}
                
                sock.sendto(json.dumps(data).encode('utf-8'), our_match['client1']['addr'])
                sock.sendto(json.dumps(data).encode('utf-8'), our_match['client2']['addr'])
        
        # Spawn asteroid
        elif cmd == 12:
            
            our_match, idx = getMatchWithId(clientMsg['netId'])
            if our_match != -1:
                # code here
                curr_id = our_match['numAsteroids']
                our_match['numAsteroids'] += 1
                
                data = {'commandSignifier': 13, 'netId': clientMsg['netId'], 'playerId': clientMsg['playerId'], 'asteroid': {'id': curr_id, 'pos': clientMsg['asteroid']['pos'], 'vel': clientMsg['asteroid']['vel']}}

                print('asteroid data: ', data)

                # send to players in match
                sock.sendto(json.dumps(data).encode('utf-8'), our_match['client1']['addr'])
                sock.sendto(json.dumps(data).encode('utf-8'), our_match['client2']['addr'])
        # Delete asteroid
        elif cmd == 14:
            our_match, idx = getMatchWithId(clientMsg['netId'])
            if our_match != -1:
                asteroid_id = clientMsg['asteroid']['id']
                
                data = { 'commandSignifier': 15, 'netId': asteroid_id, 'playerId': clientMsg['playerId'], 'deletionFlags': clientMsg['deletionFlags'], 'asteroid': {'id': asteroid_id, 'pos': clientMsg['asteroid']['pos'], 'vel': clientMsg['asteroid']['vel']}}
                
                # send to players in match
                sock.sendto(json.dumps(data).encode('utf-8'), our_match['client2']['addr'])

        mutex.release()



if __name__ == "__main__":
    mutex = threading.Lock()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print('starting server...')
    sock.bind(('', 5491))

    serverThread = threading.Thread(target=gameLoop, args=())

    serverThread.start()
    serverThread.join()
 