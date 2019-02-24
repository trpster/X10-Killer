import socket
from CM11A_Interface import SendCode

TCP_IP = "192.168.1.131"
TCP_PORT = 5005
BUFFER_SIZE = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
print("Socket listening")


def AlexaCheck():
    conn, addr = s.accept()
    print("Connection address: ", addr)
    data = conn.recv(20).decode()
    if len(data)>0:
        print("Alexa Data = ",data)
        dataTuple = data.split('/')
        HC = dataTuple[0].upper()
        DC = dataTuple[1]
        function = dataTuple[2]
        #print("SendCode = ",HC,"/",DC,"/",function)
        SendCode(HC,DC,function)
        #print("Result:", HC, DC, function)
        conn.send(data.encode())    #echo

    conn.close()
