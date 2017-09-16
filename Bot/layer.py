# coding=utf-8

from random import randint
from time import sleep

from bot_utils import Message
from yowsup.layers.interface import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.protocol_messages.protocolentities import TextMessageProtocolEntity

from chat_list import list_interactions

class EchoLayer(YowInterfaceLayer):

    @ProtocolEntityCallback("message")
    def onMessage(self, messageProtocolEntity):

        # CARGO LAS OPCIONES DE SINTOMAS (FACTORES DE PRECATEGORIZACION)
        opciones = [['Traumatismo','Leve','Intermedio','Intenso'], 
                    ['Cefalea','Leve','Intermedia','Intensa'], 
                    ['Sangrado','Leve','Intermedio','Masivo']]

        # CARGO LAS OPCIONES DE LOS AJUSTES
        opciones_ajustes = [['Edad','Menor a 3 años','Entre 3 y 65 años','Mayor de 65 años'], 
                            ['Ubicación','Hospital','Privada','Vía pública']]


        interacciones = list_interactions()
        #self.printMessage(messageProtocolEntity)

        # TIEMPO RANDOM ENTRE LAS RESPUESTAS PARA QUE NO NOS BLOQUEE WHATSAPP
        sleep(randint(5, 20)) # en segundos
        
        # VERIFICO QUE NO HAYA PASADO POR LA ETAPA 1 DE LA SOLICITUD
        # SI ES EL PRIMER MENSAJE LE DOY LA BIENVENIDA Y LE SOLICITO LA UBICACIÓN
        if interacciones.is_in_inicio(int(messageProtocolEntity.getFrom(False))) == 0:
            self.enviarMensaje(messageProtocolEntity, "Bienvenido a SIEM. Compartime tu ubicación, así sabremos a donde enviar la ambulancia.")
            interacciones.add_new_interaction(messageProtocolEntity.getFrom(False), "Saludo") 
        
        # SI NO ES EL PRIMER MENSAJE Y ME DIO LA UBICACIÓN LE MUESTRO LA LISTA DE MOTIVOS
        elif interacciones.is_in_motivo(int(messageProtocolEntity.getFrom(False))) == 0 and messageProtocolEntity.getType() == 'media' and messageProtocolEntity.getMediaType() == "location":
            interacciones.add_new_interaction(messageProtocolEntity.getFrom(False), "Motivo")
            interacciones.add_ubicacion(messageProtocolEntity.getFrom(False),messageProtocolEntity.getLatitude(),messageProtocolEntity.getLongitude())
            
            msj = "Por favor, indique los síntomas que presenta. Responda con el número correspondiente a la opción separado por coma.\n\n"

            for i in range(0,len(opciones)):
                msj = msj + str(i+1) + '. ' + opciones[i][0] + '\n'

            msj = msj + '\nPor ejemplo: 1,2 si posee ' + opciones[0][0] + ' y ' + opciones[1][0] + '.'

            self.enviarMensaje(messageProtocolEntity, msj) 
        
        # SI NO ES EL PRIMER MENSAJE Y ME DIO LA UBICACIÓN SE LA VUELVO A PEDIR 
        elif interacciones.is_in_motivo(int(messageProtocolEntity.getFrom(False))) == 0 and messageProtocolEntity.getType() == 'text':
            self.enviarMensaje(messageProtocolEntity, "Para enviar la ubicación utilice el clip para datos adjuntos y luego seleccione Enviar mi ubicación actual.")
        
        # SI YA ME ENVIÓ LA UBICACION VERIFICO QUE NO ME HAYA MANDADO LOS SINTOMAS
        elif interacciones.is_in_motivo(int(messageProtocolEntity.getFrom(False))) == 1 and interacciones.is_in_motivo_rta(int(messageProtocolEntity.getFrom(False))) == 0:
            
            # VALIDAR QUE LA RESPUESTA SEA ALGUNA DE LAS OPCIONES
            mensaje = messageProtocolEntity.getBody()
            lista = mensaje.split(",")

            sintomas_rta = ''
            for item in lista:
                if int(item.strip()) > 0 and int(item.strip()) <= len(opciones):
                    sintomas_rta = sintomas_rta + ' ' + opciones[int(item)-1][0]

            if sintomas_rta == '':
                msj = "No ha ingresado una opción válida. "
                msj = msj + "Por favor, indique los síntomas que presenta. Responda con el número correspondiente a la opción separado por coma.\n\n"

                for i in range(0,len(opciones)):
                    msj = msj + str(i+1) + '. ' + opciones[i][0] + '\n'

                msj = msj + '\nPor ejemplo: 1,2 si posee ' + opciones[0][0] + ' y ' + opciones[1][0] + '.'

                self.enviarMensaje(messageProtocolEntity, msj) 
            else:
                #msj = 'Los sintomas que usted presenta son:'+ sintomas_rta + '.'
                interacciones.add_new_interaction(messageProtocolEntity.getFrom(False), "Motivo Respuesta")
                interacciones.add_sintomas(messageProtocolEntity.getFrom(False),sintomas_rta.strip().replace(' ',';'))
                
                msj = "Indique la gravedad de cada sintoma separado por coma y en el orden provisto:\n"

                for i in lista:
                    msj = msj + '\n' + opciones[int(i.strip())-1][0] + ':\n'
                    for j in range(1,len(opciones[int(i.strip())-1])):
                        msj = msj + str(j) + '. ' + opciones[int(i.strip())-1][j] + '\n'
                        j=j+1 
                
                self.enviarMensaje(messageProtocolEntity,msj) 

        # SI YA ME ENVIÓ LOS SINTOMAS Y NO LA GRAVEDAD DE CADA UNO
        #elif interacciones.is_in_motivo_rta(int(messageProtocolEntity.getFrom(False))) == 1 and interacciones.is_in_sintomas_rta(int(messageProtocolEntity.getFrom(False))) == 0:
         

        self.toLower(messageProtocolEntity.ack())
        self.toLower(messageProtocolEntity.ack(True))

    
    @ProtocolEntityCallback("receipt")
    def onReceipt(self, entity):
        self.toLower(entity.ack())

    
    def printMessage(self,messageProtocolEntity):
        if messageProtocolEntity.getType() == 'text':
            print("\nLlego el %s de %s" % (messageProtocolEntity.getBody(), messageProtocolEntity.getFrom(False)))

        if messageProtocolEntity.getType() == 'media':
            if messageProtocolEntity.getMediaType() == "image":
                print("Echoing image %s to %s" % (messageProtocolEntity.url, messageProtocolEntity.getFrom(False)))

            elif messageProtocolEntity.getMediaType() == "location":
                print("Echoing location (%s, %s) to %s" % (messageProtocolEntity.getLatitude(), messageProtocolEntity.getLongitude(), messageProtocolEntity.getFrom(False)))

            elif messageProtocolEntity.getMediaType() == "vcard":
                print("Echoing vcard (%s, %s) to %s" % (messageProtocolEntity.getName(), messageProtocolEntity.getCardData(), messageProtocolEntity.getFrom(False)))


    def enviarMensaje(self, messageProtocolEntity, mensaje):

        outMessage = TextMessageProtocolEntity(
            mensaje,
            to = messageProtocolEntity.getFrom()
        )

        self.toLower(outMessage)
