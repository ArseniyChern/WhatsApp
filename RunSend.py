from yowsup.stacks import  YowStackBuilder
from yowsup.layers.auth import AuthError
from yowsup.layers import YowLayerEvent
from yowsup.layers.auth import YowAuthenticationProtocolLayer
from yowsup.layers.network import YowNetworkLayer

from yowsup.layers.interface                           import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.protocol_messages.protocolentities  import TextMessageProtocolEntity
from yowsup.common.tools import Jid
import threading
import os
import json
os.chdir("/Users/Arseniy/Desktop/")


class SendLayer(YowInterfaceLayer):

    #This message is going to be replaced by the @param message in YowsupSendStack construction
    #i.e. list of (jid, message) tuples
    PROP_MESSAGES = "org.openwhatsapp.yowsup.prop.sendclient.queue"
    
    
    def __init__(self):
        super(SendLayer, self).__init__()
        self.ackQueue = []
        self.lock = threading.Condition()

    #call back function when there is a successful connection to whatsapp server
    @ProtocolEntityCallback("success")
    def onSuccess(self, successProtocolEntity):
        self.lock.acquire()
        for target in self.getProp(self.__class__.PROP_MESSAGES, []):
        
            #getProp() is trying to retreive the list of (jid, message) tuples, if none exist, use the default []
            phone = target
            message = self.getProp(self.__class__.PROP_MESSAGES, [])[1]
            print(target[1])
            messageEntity = TextMessageProtocolEntity(message, to = Jid.normalize(phone))
            #append the id of message to ackQueue list
            #which the id of message will be deleted when ack is received.
            self.ackQueue.append(messageEntity.getId())
            self.toLower(messageEntity)
        self.lock.release()

    #after receiving the message from the target number, target number will send a ack to sender(us)
    @ProtocolEntityCallback("ack")
    def onAck(self, entity):
        self.lock.acquire()
        #if the id match the id in ackQueue, then pop the id of the message out
        if entity.getId() in self.ackQueue:
            self.ackQueue.pop(self.ackQueue.index(entity.getId()))
            
        if not len(self.ackQueue):
            self.lock.release()
            print("Message sent")
            raise KeyboardInterrupt()

        self.lock.release()


class YowsupSendStack(object):
    def __init__(self, credentials, messages, encryptionEnabled = True):
        """
        :param credentials:
        :param messages: list of (jid, message) tuples
        :param encryptionEnabled:
        :return:
        """
        stackBuilder = YowStackBuilder()

        global stack 
        stack = stackBuilder\
            .pushDefaultLayers(True)\
            .push(SendLayer)\
            .build()

        stack12 = stack

        stack.setProp(SendLayer.PROP_MESSAGES, messages)
        stack.setProp(YowAuthenticationProtocolLayer.PROP_PASSIVE, True)
        stack.setCredentials(credentials)

    def start(self):
        stack.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))
        try:
            print("Working")
            stack.loop()
        except AuthError as e:
            print("Authentication Error: %s" % e.message)


credentials = ("380663358076", "ghDhWjCn+7LLe5kin0Dfjdsj3vg=")


def sendMessage(to, message):
    t = YowsupSendStack(credentials=credentials,messages=(to,message))
    t.start()

with open('whatsAppInfo.json') as data_file:    
    data = json.load(data_file)

to = data["recipient"]
msg = data["message"]

sendMessage(to,msg)

