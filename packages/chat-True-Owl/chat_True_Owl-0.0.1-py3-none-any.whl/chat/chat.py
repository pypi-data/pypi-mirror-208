
import socket
from threading import Thread

class ChatServer:
    def __init__(self,port):
        self.host='0.0.0.0'
        self.port=port

        self.client_sokets = []

        self.s = socket.socket()

        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        self.s.bind((self.host, self.port))

        self.s.listen()
        print(f'[*] {self.host}:{self.port} 주소에서 통신 대기중...')

    def communication_with_clinet(self,cs):
        while True:
            try:
                message = cs.recv(1024).decode()
            except Exception as e:
                print(f"[!] 에러 발생 {e}")
                self.client_sokets.remove(cs)
            else:
                for client_soket in self.client_sokets:
                    if cs != client_soket:
                        client_soket.send(message.encode())

    def serve(self):
        while True:
            client_socket, client_address = self.s.accept()
            print(f"[+] 연결 완료: {client_address}")
            self.client_sokets.append(client_socket)

            t = Thread(target=self.communication_with_clinet, args=(client_socket,),daemon=True)
            t.start()



class ChatClient:
    def __init__(self,host,port,name='익명'):
        self.host = host
        self.port = port
        self.name = name

        self.s = socket.socket()
        
        print(f"[*] {self.host}:{self.port} 로 연결시도")

        self.s.connect((self.host, self.port))
        print("[+] 연결 완료")

    def communication_with_server(self):
        while True:
            message = self.s.recv(1024).decode()
            print(message)

    def connect(self):
        t = Thread(target=self.communication_with_server, daemon=True)
        t.start()

        while True:
            message = input()
            message = f"{self.name}: {message}"

            self.s.send(message.encode())

        self.s.close()
