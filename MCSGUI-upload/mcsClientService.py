import socket
from virtualbox import VirtualBox,Session,library
from threading import Thread
from os import environ
from time import sleep
from win32api import GetCursorPos
from tkinter import Tk, Label, Button, StringVar
from hashlib import md5


#protocol
SUCCESS = "1111"
USER_WANTS_TO_USE_MY_PROCESS_POWER = 8099
I_AGREE_TO_USE_MY_PROCESS_POWER = "189"
I_DONT_AGREE_TO_USE_MY_PROCESS_POWER = "188"
ASKED_TO_STOP_MY_SHARING = 8080
STOP_USING_MY_PROCESS_POWER = "808"
I_WANT_TO_USE_CPU = "909"
I_WANT_TO_STOP_USE_CPU = "908"
CLIENT_FOUND = 1909
CLIENT_NOT_FOUND = 1908
CLIENT_STOPPED_SHARING = 8080
FPS = 0.03333333333

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

HOST = "192.168.1.19"
SERVER_PORT = 1234
CLIENT_PORT = 2345




class clientService():

    def __init__(self):
        self._active = False
        checkUsersActivity = Thread(target=self.checkUsersActivityFunc)
        checkUsersActivity.start()
        # Create a TCP/IP sockets for client and server.
        self._serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (HOST, SERVER_PORT)
        client_address = ("127.0.0.1", CLIENT_PORT)
        self._serverSock.connect(server_address)
        self._clientSock.bind(client_address)
        self._agree = False
        self._app = None
        self._sharing = False
        self._ip = get_ip_address()
        self._pcName = environ['COMPUTERNAME']
        message = ((str)('111' + str(len(self._pcName)).zfill(2) +  self._pcName)).encode('ascii')
        #loop for login
        while(True):
            self._serverSock.sendall(message)
            response = (self._serverSock.recv(4)).decode('ascii')
            if(response == SUCCESS):
                break
            else:
                sleep(60)

        connectionWithUIThread = Thread(target=self.listenServer)
        connectionWithUIThread.start()
        connectionWithServer = Thread(target=(self.listenClient))
        connectionWithServer.start()

    def listenClient(self):
        #loop for connection
        helper = Helper()
        while(True):
            response = helper.getMessageTypeCode(self._serverSock)
            if(response == USER_WANTS_TO_USE_MY_PROCESS_POWER):
                ipLength = helper.getIntPartFromSocket(self._serverSock, 2)
                ipAddress = helper.getPartFromSocket(self._serverSock, ipLength)
                usernameLength = helper.getIntPartFromSocket(self._serverSock, 2)
                username = (helper.getPartFromSocket(self._serverSock, usernameLength)).lower()
                if(self._active):
                    self._app = Tk()
                    labelText=StringVar()
                    labelText.set("Do you agree to use your pc right now?")
                    labelDir=Label(self._app, textvariable=labelText, height=4)
                    labelDir.pack(side="left")
                    button1=Button(self._app,text="Yes" ,width=25, command=self.Agree)
                    button1.pack(side="left")
                    button2=Button(self._app,text="No" ,width=25, command=self.NotAgree)
                    button2.pack(side="left")
                    self._app.mainloop()
                    if(self._agree):
                        self._serverSock.sendall(I_AGREE_TO_USE_MY_PROCESS_POWER.encode('ascii'))
                        self._app = Tk()
                        labelText.set("Do you want to stop sharing your pc?")
                        labelDir=Label(self._app, textvariable=labelText, height=4)
                        labelDir.pack(side="left")
                        button1=Button(self._app,text="Yes" ,width=25, command=self.Agree)
                        button1.pack(side="left")
                        OpenVm = Thread(target=self.openVm, args=(username,ipAddress,))
                        OpenVm.start()
                        self._sharing = True
                        self._agree = False
                        self._toStop = False
                        checkISharedUserAskedToStop= Thread(target=self.checkISharedUserAskedToStop)
                        checkISharedUserAskedToStop.start()
                        self._app.mainloop()
                        if(self._agree):
                            self._toStop = True
                    else:
                        self._serverSock.sendall(I_DONT_AGREE_TO_USE_MY_PROCESS_POWER.encode('ascii'))
                else:
                    self._serverSock.sendall(I_DONT_AGREE_TO_USE_MY_PROCESS_POWER.encode('ascii'))
            elif(response == CLIENT_FOUND):
                self._clientSock.sendall('11'.encode('ascii'))
            elif(response == CLIENT_NOT_FOUND):
                self._clientSock.sendall('12'.encode('ascii'))
            elif(response == CLIENT_STOPPED_SHARING):
                self._clientSock.sendall('33'.encode('ascii'))

    def checkISharedUserAskedToStop(self):
        helper = Helper()
        response = helper.getMessageTypeCode(self._serverSock)
        print("yosef")
        if response == ASKED_TO_STOP_MY_SHARING:
            try:
                self._app.destroy()
            except Exception as e:
                self._toStop = True
            self._toStop = True

    def openVm(self, askingUsersUsername, ipAddress):
        # Create vm object...
        vbox = VirtualBox()
        # Opening session...
        session = Session()
        # Finding machine...
        vm = vbox.find_machine(askingUsersUsername)
        # Run gui...
        progress = vm.launch_vm_process(session, 'gui', '')
        h, w, _, _, _, _ = session.console.display.get_screen_resolution(0)
        screenThread = Thread(target=self.screenShare, args=(session,h,w,ipAddress,))
        mouseAndKeyboardThread = Thread(target=self.mouseAndKeyboardShare, args=(session,ipAddress,))
        screenThread.start()
        mouseAndKeyboardThread.start()
        screenThread.join()
        mouseAndKeyboardThread.join()
        # Taking snapshot...
        x, p = session.machine.take_snapshot("test1", "test2", True)
        x.wait_for_completion()
        session.machine.save_state()
        self._serverSock.sendall((STOP_USING_MY_PROCESS_POWER + str(len(self._pcName)) + self._pcName).encode('ascii'))
        self._sharing = False
        self._toStop = False
	
    def screenShare(self,session,h,w,ipAddress):
        serverAddressPort  = (ipAddress, 3456)
        # Create a UDP socket at client side
        UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        currM = md5()
        prvM = md5()
        currPng = ""
        prvPng = ""
        while(not self._toStop):
            currPng = session.console.display.take_screen_shot_to_array(0, h, w, library.BitmapFormat.png)
            currM.update(currPng)
            prvM.update(prvPng)
            if(currM.hexdigest() == prvM.hexdigest()):
                pass
            else:
                # Send to server using created UDP socket
                UDPClientSocket.sendto(str.encode(currPng), serverAddressPort)
                prvPng = currPng
                sleep(FPS)

    def mouseAndKeyboardShare(self, session ,ipAddress):
        # Create a datagram socket
        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        # Bind to address and ip
        UDPServerSocket.bind((ipAddress, 4567))
        # Listen for incoming datagrams
        while(not self._toStop):
            bytesAddressPair = UDPServerSocket.recvfrom(1024)
            message = bytesAddressPair[0]
            if(message[:2] == "mm"):
                session.console.mouse.put_mouse_event(float(message[1:-4]), float(message[-4:]),0,0,0)
            elif(message[:2] == "mc"):
                if(message[2:] == "00"):
                    session.console.mouse.put_mouse_event(0,0,0,0,0)
                elif(message[2:] == "10"):
                    session.console.mouse.put_mouse_event(0,0,0,0,1)
                elif(message[2:] == "01"):
                    session.console.mouse.put_mouse_event(0,0,0,0,2)
                else:
                    session.console.mouse.put_mouse_event(0,0,0,0,4)
            elif(message[0] == "k"):
                session.console.keyboard.put_keys(message[1:])


    def checkUsersActivityFunc(self):
        count = 0
        savedpos = GetCursorPos()
        while(True):
            while(True):
                if count>6000:   # break after 5 minutes
                    break
                curpos = GetCursorPos()
                if savedpos != curpos:
                    savedpos = curpos
                    self._active = True
                    count = 0
                sleep(0.05)
                count +=1
            if not self._sharing:
                self._active = False
            count = 0

    def Agree(self):
        self._agree = True
        self._app.destroy()

    def NotAgree(self):
        self._agree = False
        self._app.destroy()

    def listenServer(self):
        # Start listening on socket
        self._clientSock.listen(1)
        # Wait for client
        conn, addr = self._clientSock.accept()
        self._clientSock = conn
        # Receive data from client
        while True:
            data = (self._clientSock.recv(1)).decode('ascii')
            if(data == "1"):
                self._serverSock.sendall((I_WANT_TO_USE_CPU + str(len(self._pcName)).zfill(2) + self._pcName + str(len(self._ip)) + self._ip).encode('ascii'))
            elif(data == "2"):
                self._serverSock.sendall((I_WANT_TO_STOP_USE_CPU + str(len(self._pcName)).zfill(2) + self._pcName).encode('ascii'))


class Helper:
    # receives the type code of the message from socket (first byte)
    # and returns the code. if no message found in the socket, returns 0 (which means the client disconnected)
    def getMessageTypeCode(self, connection):
        s = self.getPartFromSocket(connection, 4)
        msg = str(s)
        if msg == "":
            return 0
        return int(s)

    # get int data from socket
    def getIntPartFromSocket(self, connection, bytesNum):
        s = self.getPartFromSocket(connection, bytesNum)
        return int(s)

    # get string data from socket
    def getPartFromSocket(self, connection, bytesNum):
        if (bytesNum == 0):
            return None
        data = connection.recv(bytesNum)
        return data

def main():
    c = clientService()
main()

