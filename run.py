from yowsup.layers.interface                           import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.protocol_messages.protocolentities  import TextMessageProtocolEntity
from yowsup.layers.protocol_receipts.protocolentities  import OutgoingReceiptProtocolEntity
from yowsup.layers.protocol_acks.protocolentities      import OutgoingAckProtocolEntity


from yowsup.stacks import  YowStackBuilder
from yowsup.layers.auth import AuthError
from yowsup.layers import YowLayerEvent
from yowsup.layers.network import YowNetworkLayer
from yowsup.env import YowsupEnv

import threading

import json
import os
os.chdir("/Users/Arseniy/Desktop/")

class EchoLayer(YowInterfaceLayer):

    def sendMessage(self, to, message):
        outgoingMessageProtocolEntity = TextMessageProtocolEntity(
            message,
            to = to
        )
        print(to)
        self.toLower(outgoingMessageProtocolEntity)
    

    @ProtocolEntityCallback("message")
    def onMessage(self, messageProtocolEntity):

        if True:

            #self.sendMessage(messageProtocolEntity.getFrom(),messageProtocolEntity.getBody())

            print(messageProtocolEntity.getFrom(),messageProtocolEntity.getBody())

            outputJson(messageProtocolEntity.getFrom(),messageProtocolEntity.getBody())
        
    @ProtocolEntityCallback("receipt")
    def onReceipt(self, entity):
        ack = OutgoingAckProtocolEntity(entity.getId(), "receipt", entity.getType(), entity.getFrom())
        self.toLower(ack)

credentials = ("380663358076", "ghDhWjCn+7LLe5kin0Dfjdsj3vg=")

def outputJson(recipient,message):
		fo = open("whatsAppInfo.json", "w")
		outputString = "{\"recipient\" : \""+recipient+"\", \"message\" : \""+message+"\"}"
		fo.write(outputString)
		fo.close()


if __name__==  "__main__":
    stackBuilder = YowStackBuilder()

    stack = stackBuilder\
        .pushDefaultLayers(True)\
        .push(EchoLayer)\
        .build()

    stack.setCredentials(credentials)
    stack.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT)) 

    
    stack.loop()
    









