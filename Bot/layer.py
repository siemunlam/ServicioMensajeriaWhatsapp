# coding=utf-8

from bot_utils import Message
from yowsup.layers.interface import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.protocol_messages.protocolentities import TextMessageProtocolEntity

class EchoLayer(YowInterfaceLayer):

    @ProtocolEntityCallback("message")
    def onMessage(self, messageProtocolEntity):

        if messageProtocolEntity.getType() == 'text':
            self.onTextMessage(messageProtocolEntity)
            #myDict = ['hola', 'buen dia', 'buenas tardes', 'buenas noches']
            #if messageProtocolEntity.getBody().lower() in myDict:
              #if messageProtocolEntity.getBody().lower() == 'Ayuda':
            message = Message()

            if messageProtocolEntity.getBody().lower() in message.GetSaludos(): # va GetSaludo
                self.enviarMensaje(messageProtocolEntity, message.GetSaludoRespuesta()) # GetSaludoRespuesta 
            elif messageProtocolEntity.getBody().lower() == message.pregunta_estado_persona:
                 self.enviarMensaje(messageProtocolEntity, "Muy bien, gracias por preguntar.")               
            else:
                 self.enviarMensaje(messageProtocolEntity, "Palabra reservada no encontrada.")     

            #self.toLower(messageProtocolEntity.forward(protocol_messagesProtocolEntity.getFrom()))
            self.toLower(messageProtocolEntity.ack())
            self.toLower(messageProtocolEntity.ack(True))

        elif messageProtocolEntity.getType() == 'media':
            self.enviarMensaje(messageProtocolEntity, "Formato de mensaje no válido.")

    @ProtocolEntityCallback("receipt")
    def onReceipt(self, entity):
        self.toLower(entity.ack())

    def onTextMessage(self,messageProtocolEntity):
        # just print info
        print("Llego el %s de %s" % (messageProtocolEntity.getBody(), messageProtocolEntity.getFrom(False)))

    def enviarMensaje(self, messageProtocolEntity, mensaje):

        outMessage = TextMessageProtocolEntity(
            mensaje,
            to = messageProtocolEntity.getFrom()
        )

        self.toLower(outMessage)

    """
    def onMediaMessage(self, messageProtocolEntity):
        # just print info
        if messageProtocolEntity.getMediaType() == "image":
            print("Echoing image %s to %s" % (messageProtocolEntity.url, messageProtocolEntity.getFrom(False)))

        elif messageProtocolEntity.getMediaType() == "location":
            print("Echoing location (%s, %s) to %s" % (messageProtocolEntity.getLatitude(), messageProtocolEntity.getLongitude(), messageProtocolEntity.getFrom(False)))

        elif messageProtocolEntity.getMediaType() == "vcard":
            print("Echoing vcard (%s, %s) to %s" % (messageProtocolEntity.getName(), messageProtocolEntity.getCardData(), messageProtocolEntity.getFrom(False)))
    """
