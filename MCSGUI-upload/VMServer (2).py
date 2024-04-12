from threading import Condition
import socket
from threading import Thread
from time import sleep
PORT = 1234


#Protocol defines:
CLOSE_APP = 666
OPEN_APP = 111
SUCCESS = b'1111'
FAILURE = b'1112'
USE_PROCESS_POWER = 909
STOP_USE_PROCESS_POWER_FROM_SHARING = 808
STOP_USE_PROCESS_POWER_FROM_SHARED = 908
GET_CPU_LIST = 907
OK_TO_USE = 189
NOT_OK_TO_USE = 188
clientsCPU = 555
I_WANT_TO_USE_YOUR_PROCESS_POWER = "8099"
I_WANT_TO_GET_YOUR_CPU = "5050"
HERE_IS_CPU_LIST = "4040"
HERE_IS_CLIENTS_CPU = 555
PC_FOUND = b'1909'
PC_NOT_FOUND = b'1908'
THE_USER_STOPPED_SHARING = b'707'
THE_USER_NOT_INTERESTED_SHARING_ANYMORE = b'8080'


class MCSServer:

    # Creates MCSServer object
    def __init__(self):
        self._connectedUsers = {}
        self._busyUsers = []
        self._askedUsers = []
        self._cond = Condition()
        self._queRcvMessages = []
        self._liveRequests = []
        self.cpu_list = {}
        self._helper = Helper()
        self._ip = self._helper.get_ip_address()
        # Create a TCP/IP socket
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        checkOnlineUsers = Thread(target=self.checkOnlineUsers)
        checkOnlineUsers.start()

    def checkOnlineUsers(self):
        while(True):
            offlineUsers = []
            for conn in self._connectedUsers:
                try:
                    self._connectedUsers[conn].sendall(I_WANT_TO_GET_YOUR_CPU.encode('ascii'))
                except Exception as e:
                    offlineUsers.append(conn)
            for offlineUser in offlineUsers:
                del self._connectedUsers[offlineUser]
                del self.cpu_list[offlineUser]
            sleep(1)

    # Listening on port for incoming connection
    def bindAndListen(self):
        # Bind the socket to the port
        server_address = (self._ip, PORT)
        self._socket.bind(server_address)
        # Listen for incoming connections

    # The function opens the listening socket, open thread that handles received messages, and calls accept client function
    def Server(self):
        self.bindAndListen()
        thread1 = Thread(target= self.handleReceivedMessages, name="HandleMessagesThread")
        thread1.start()
        while(True):
            print("Waiting for connection")
            self.accept()

    # The function is being called when a new connection established, and create a thread to handle connection
    def accept(self):
        self._socket.listen(1)
        connection, client_address = self._socket.accept()
        thread2 = Thread(target= self.clientHandler, name= "HandleClientsThread", args=(connection, ))
        thread2.start()

    # The function handles messages that was sent from user, builds messages objects from them, and calls a function that adds them to messages list
    def clientHandler(self, connection):
        receivedMessage = None
        messageCode = self._helper.getMessageTypeCode(connection) #get message tyoe code
        try:
            while(not (messageCode == CLOSE_APP)):
                receivedMessage = self.buildReceivedMessage(connection, messageCode) # create message object from message
                self.addReceivedMessage(receivedMessage) # calls function that adding the message to the messages list
                messageCode = self._helper.getMessageTypeCode(connection)
        except:
            pass

    # The function builds a message object from user's messages
    def buildReceivedMessage(self, connection, messageCode):
        arguments = []
        if messageCode == OPEN_APP:
            usernameLength = self._helper.getIntPartFromSocket(connection, 2)
            username = (self._helper.getPartFromSocket(connection, int(usernameLength))).decode('ascii')
            arguments.append(username)
        elif messageCode == USE_PROCESS_POWER:
            usernameLength = self._helper.getIntPartFromSocket(connection, 2)
            username = (self._helper.getPartFromSocket(connection, int(usernameLength))).decode('ascii')
            ipLength = self._helper.getIntPartFromSocket(connection, 2)
            ipAddress = (self._helper.getPartFromSocket(connection, int(ipLength))).decode('ascii')
            arguments.append(username)
            arguments.append(ipAddress)
        elif messageCode == STOP_USE_PROCESS_POWER_FROM_SHARING:
            usernameLength = self._helper.getIntPartFromSocket(connection, 2)
            username = (self._helper.getPartFromSocket(connection, int(usernameLength))).decode('ascii')
            arguments.append(username)
        elif messageCode == STOP_USE_PROCESS_POWER_FROM_SHARED:
            usernameLength = self._helper.getIntPartFromSocket(connection, 2)
            username = (self._helper.getPartFromSocket(connection, int(usernameLength))).decode('ascii')
            arguments.append(username)
        elif messageCode == HERE_IS_CLIENTS_CPU:
            cpu = (self._helper.getPartFromSocket(connection, 2)).decode('ascii')
            usernameLength = self._helper.getIntPartFromSocket(connection, 2)
            username = (self._helper.getPartFromSocket(connection, int(usernameLength))).decode('ascii')
            arguments.append(username)
            arguments.append(cpu)
        message = Message(connection,arguments ,messageCode)
        return message

    # The function adds a message to received messages list
    def addReceivedMessage(self, Message):
        self._cond.acquire() # lock
        self._queRcvMessages.insert(-1, Message) # add message to message list
        self._cond.notify_all() # notify received messages handler
        self._cond.release() # unlock
        pass

    # The function handles messages that were pushed to received messages list
    def handleReceivedMessages(self):

        while(True):
            self._cond.acquire() # lock
            while(len(self._queRcvMessages) == 0):
                self._cond.wait() #unlock and wait until notified
            message = self._queRcvMessages.pop(0)
            self._cond.release() # unlock

            print(message._arguments,message._messageCode)
            if(message._messageCode == OPEN_APP):
                if(message._arguments[0] in self._connectedUsers):
                    (message._socket).sendall(FAILURE)
                else:
                    self._connectedUsers[message._arguments[0]] = message._socket
                    (message._socket).sendall(SUCCESS)

            elif(message._messageCode == USE_PROCESS_POWER):
                if not (self.handle_use_process_power(message)):
                    message._socket.sendall(PC_NOT_FOUND)

            elif(message._messageCode == STOP_USE_PROCESS_POWER_FROM_SHARING):
                self.handle_stop_use_process_power_from_sharing(message)
            elif(message._messageCode == GET_CPU_LIST):
                self.handle_get_cpu_list(message)
            elif(message._messageCode == OK_TO_USE or message._messageCode == NOT_OK_TO_USE):

                if(message._messageCode == OK_TO_USE):
                    self.handle_ok_to_use(message)
                else:
                    self.handle_not_ok_to_use(message)
            elif(message._messageCode == STOP_USE_PROCESS_POWER_FROM_SHARED):
                self.handle_stop_use_process_power_from_shared(message)
            elif(message._messageCode == HERE_IS_CLIENTS_CPU):
                self.cpu_list[message._arguments[0]] = message._arguments[1]


    def handle_use_process_power(self, message):
        found = False
        for user in self._connectedUsers:
            if((not (user == message._arguments[0])) and (user not in self._busyUsers) and (user not in self._askedUsers)):
                toSend = (I_WANT_TO_USE_YOUR_PROCESS_POWER + str(len(message._arguments[1])).zfill(2) + message._arguments[1] + str(len(message._arguments[0])).zfill(2) + message._arguments[0]).encode('ascii')
                self._connectedUsers[user].sendall(toSend)
                request = (user, self._connectedUsers[user], message._arguments, message._socket)
                self._liveRequests.append(request)
                print("_______________________________")
                print(self._liveRequests)
                self._askedUsers.append(user)
                found = True
                break
        return found

    def handle_stop_use_process_power_from_sharing(self, message):
        req = None
        print("banana1")
        for request in self._liveRequests:
            if(request[0] == message._arguments[0]):
                req = request
        del self._liveRequests[self._liveRequests.index(req)]
        if(req[0] in self._busyUsers):
            del self._busyUsers[self._busyUsers.index(req[0])]

    def handle_stop_use_process_power_from_shared(self, message):
        req = None
        for request in self._liveRequests:
            print(request)
            print("_______________________________")
            print(message._arguments[0])
            if(request[2][0] == message._arguments[0]):
                req = request
        del self._liveRequests[self._liveRequests.index(req)]
        if(req[0] in self._busyUsers):
            del self._busyUsers[self._busyUsers.index(req[0])]
        req[1].sendall(THE_USER_NOT_INTERESTED_SHARING_ANYMORE)


    def handle_get_cpu_list(self,message):
        toSend = ""
        for connected in self.cpu_list:
            toSend = toSend + str(len(connected)).zfill(2) + connected + self.cpu_list[connected]
        message._socket.sendall((HERE_IS_CPU_LIST + toSend).encode('ascii'))

    def handle_ok_to_use(self, message):
        print("ok to use")
        req = None
        for request in self._liveRequests:
            print(request)
            if request[1] == message._socket:
                request[3].sendall(PC_FOUND)
                print("sent pc found")
                self._busyUsers.append(request[0])
                req = request
                break
        del self._askedUsers[self._askedUsers.index(req[0])]

    def handle_not_ok_to_use(self, message):
        print("banana2")
        req = None
        for request in self._liveRequests:
            if request[1] == message._socket:
                if len(self._busyUsers) == len(self._connectedUsers):
                    request[3].sendall(PC_NOT_FOUND)
                else:
                    self._busyUsers.append(request[0])
                    msg = Message(request[3], request[2],USE_PROCESS_POWER)
                    found = self.handle_use_process_power(msg)
                    if(not found):
                        request[3].sendall(PC_NOT_FOUND)
                req = request
                req = request
                break


        del self._liveRequests[self._liveRequests.index(req)]
        del self._askedUsers[self._askedUsers.index(req[0])]


class Helper:

    # receives the type code of the message from socket (first byte)
    # and returns the code. if no message found in the socket, returns 0 (which means the client disconnected)
    def getMessageTypeCode(self, connection):
        s = self.getPartFromSocket(connection, 3)
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

    # The function gets byteSize and a number, and returns a string of the number with zero before it according to byteSize.
    #For example: parameters: byteSize = 4, toFill = 12 | return Value: "0012".
    #Another example: parameters: byteSize = 4, toFill = 1 | return Value: "0001".
    def get_ip_address(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]


class Message:
    def __init__(self, connection, arguments, messageCode):
        self._arguments = []
        self._socket = connection
        for argument in arguments:
            self._arguments.append(argument)
        self._messageCode = messageCode
    _socket = None
    _messageCode = None
    _arguments = []

class User:
    _name = None
    _virtualMachine = None
    _socket = None


def main():
    mcsserver = MCSServer()
    mcsserver.Server()

main()
