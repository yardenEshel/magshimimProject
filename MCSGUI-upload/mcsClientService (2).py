import socket
from virtualbox import VirtualBox,Session,library
from threading import Thread
from os import environ
from time import sleep
from win32api import GetCursorPos
from tkinter import Tk, Label, Button, StringVar
import io
from PIL import Image
import win32gui
import win32ui
from resizeimage import resizeimage
from ctypes import windll
from psutil import cpu_percent



#protocol
SUCCESS = "1111"
USER_WANTS_TO_USE_MY_PROCESS_POWER = 8099
I_AGREE_TO_USE_MY_PROCESS_POWER = "189"
I_DONT_AGREE_TO_USE_MY_PROCESS_POWER = "188"
HERE_IS_MY_CPU = "555"
ASKED_TO_STOP_MY_SHARING = 8080
STOP_USING_MY_PROCESS_POWER = "808"
I_WANT_TO_USE_CPU = "909"
I_WANT_TO_STOP_USE_CPU = "908"
I_WANT_TO_GET_LIST_OF_CPU = "907"
CLIENT_FOUND = 1909
CLIENT_NOT_FOUND = 1908
SERVER_WANTS_MY_CPU = 5050
CLIENT_STOPPED_SHARING = 8080
CPU_LIST_FOUND = 4040
PNUM = 20

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

HOST = "192.168.1.10"
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
                        button1=Button(self._app,text="Stop sharing" ,width=25, command=self.Agree)
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
            elif(response == SERVER_WANTS_MY_CPU):
                percent = int(cpu_percent())
                if percent > 99:
                    percent = 99
                self._serverSock.sendall((HERE_IS_MY_CPU + str(percent).zfill(2) + str(len(self._pcName)).zfill(2) + self._pcName).encode('ascii'))
            elif(response == CPU_LIST_FOUND):
                data = self._serverSock.recv(1024)
                self._clientSock.sendall(data)

    def checkISharedUserAskedToStop(self):
        helper = Helper()
        response = helper.getMessageTypeCode(self._serverSock)
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
        screenThread = Thread(target=self.screenShare, args=(session,ipAddress,askingUsersUsername,))
        mouseAndKeyboardThread = Thread(target=self.mouseAndKeyboardShare, args=(session,ipAddress,))
        screenThread.start()
        mouseAndKeyboardThread.start()
        screenThread.join()
        mouseAndKeyboardThread.join()
        #Taking snapshot...
        #x, p = session.machine.take_snapshot("test1", "test2", True)
        #x.wait_for_completion()
        #session.machine.save_state()
        self._serverSock.sendall((STOP_USING_MY_PROCESS_POWER + str(len(self._pcName)) + self._pcName).encode('ascii'))

        self._sharing = False
        self._toStop = False

    def screenShare(self,session,ipAddress,askingUsersUsername):
        # Create a UDP socket at client side
        # Create a TCP/IP socket
        ipAddress = (ipAddress.decode('ascii')).encode('ascii')
        print(ipAddress)
        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = (ipAddress, 3456)
        buffer = bytearray()
        prev = bytearray()
        compare = 0
        exception = True
        hwnd = ''
        saveDC = ''
        w = ''
        h = ''
        mfcDC = ''
        hwndDC = ''
        while(exception):
                try:
                    name = askingUsersUsername.decode('ascii') + ' (test1) [Running] - Oracle VM VirtualBox'
                    hwnd = win32gui.FindWindow(None, name)
                    left, top, right, bot = win32gui.GetWindowRect(hwnd)
                    w = right - left
                    h = bot - top
                    exception = False
                    hwndDC = win32gui.GetWindowDC(hwnd)
                    mfcDC  = win32ui.CreateDCFromHandle(hwndDC)
                    saveDC = mfcDC.CreateCompatibleDC()
                    saveBitMap = win32ui.CreateBitmap()
                    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
                    saveDC.SelectObject(saveBitMap)
                except Exception as e:
                    print(e)
                    sleep(3)
                    sent = sock.sendto((self._ip).encode("ascii"), server_address)
                    exception = True
        while(not self._toStop):
            result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 0)
            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)
            im = Image.frombuffer('RGB',(bmpinfo['bmWidth'], bmpinfo['bmHeight']),bmpstr, 'raw', 'BGRX', 0, 1)
            cover = resizeimage.resize_cover(im, [w, h])
            bg_w, bg_h = cover.size
            #flags, hcursor, (x,y) = win32gui.GetCursorInfo()
            #cover.paste(cursor, (x,y))
            prev = buffer
            if result == 1:
                imgByteArr = io.BytesIO()
                cover.save(imgByteArr, format='PNG')
                buffer = imgByteArr.getvalue()
            buffer = buffer.ljust(len(buffer) + PNUM - len(buffer) % PNUM, b'\x00')
            sizeOfOnePacket = int(len(buffer) / PNUM)
            if(not len(prev)  == len(buffer)):
                print(buffer[-10:-1])
                sizeStr = str(sizeOfOnePacket).zfill(5)
                sent = sock.sendto(sizeStr.encode('ascii'), server_address)
                print(str(sizeOfOnePacket))
                for i in range(PNUM):
                    pass
                    sent = sock.sendto(buffer[i*sizeOfOnePacket : (i*sizeOfOnePacket + sizeOfOnePacket)], server_address)
            else:
                print("same!")
        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)

    def mouseAndKeyboardShare(self, session ,ipAddress):
        # Create a datagram socket
        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        # Bind to address and ip
        print(self._ip)
        UDPServerSocket.bind((self._ip, 5678))
        # Listen for incoming datagrams
        while(not self._toStop):
            try:
                print("waiting")
                message = UDPServerSocket.recv(1)
                print("stopped")
                message = message.decode("ascii")
                if(message == "m"):
                    print("message")
                    message = UDPServerSocket.recv(1)
                    message = message.decode("ascii")
                    if(message == 'm'):
                        message = UDPServerSocket.recv(10)
                        message = message.decode("ascii")
                        print(int(message[:5]), int(message[5:]))
                        session.console.mouse.put_mouse_event_absolute(int(message[:5]), int(message[5:]) - 50 ,0,0,0)
                    elif(message == 'c'):
                        print("click")
                        message = UDPServerSocket.recv(1)
                        message = message.decode("ascii")
                        if(message == "0"):
                            session.console.mouse.put_mouse_event(0,0,0,0,4)
                        elif(message == "1"):
                            session.console.mouse.put_mouse_event(0,0,0,0,1)
                        elif(message == "2"):
                            session.console.mouse.put_mouse_event(0,0,0,0,2)
                        elif(message == "3"):
                            session.console.mouse.put_mouse_event(0,0,0,0,0)
                        else:
                            pass
                elif(message == "k"):
                    print("keyboard")
                    message = UDPServerSocket.recv(4)
                    message = chr(int(message.decode('ascii')))
                    session.console.keyboard.put_keys(message)
            except Exception as e:
                print(e)

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
            elif(data == "3"):
                self._serverSock.sendall(I_WANT_TO_GET_LIST_OF_CPU.encode('ascii'))


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

    def chunkIt(self,seq, num):
        avg = len(seq) / float(num)
        out = []
        last = 0.0

        while last < len(seq):
            out.append(seq[int(last):int(last + avg)])
            last += avg
        return out

def main():
    c = clientService()
main()

