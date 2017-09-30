# coding=utf-8

from random import randint
from time import sleep

from bot_utils import Message
from yowsup.layers.interface import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.protocol_messages.protocolentities import TextMessageProtocolEntity

from chat_list import list_interactions

import urllib.request
import json

class EchoLayer(YowInterfaceLayer):

    @ProtocolEntityCallback("message")
    def onMessage(self, messageProtocolEntity):

        # CARGO LAS OPCIONES DE SINTOMAS (FACTORES DE PRECATEGORIZACION)
        # opciones = [['Traumatismo','Leve','Intermedio','Intenso'], 
        #             ['Cefalea','Leve','Intermedia','Intensa','Suprema'], 
        #             ['Sangrado','Leve','Intermedio','Masivo']]
        url_1 = 'http://siemunlam.pythonanywhere.com/api/rules/motivospc/'
        req_1 = urllib.request.Request(url_1)

        r_1 = urllib.request.urlopen(req_1).read()
        rta_1 = json.loads(r_1.decode('utf-8'))

        cantidad = rta_1['count']
        valores = rta_1['results']

        opciones = []
        opcion_temp = []

        for i in valores:
            opcion_temp.append(i)
            for j in valores[i]:
                opcion_temp.append(j)
            opciones.append(opcion_temp)
            opcion_temp = []


        # CARGO LAS OPCIONES DE LOS AJUSTES
        # opciones_ajustes = [['Edad','Menor a 3 años','Entre 3 y 65 años','Mayor de 65 años'], 
        #                     ['Ubicacion','Privada','Via publica'],
        #                     ['Temperatura','Menor a 38','Mayor a 38']]
        url_2 = 'http://siemunlam.pythonanywhere.com/api/rules/motivosajuste/'
        req_2 = urllib.request.Request(url_2)

        r_2 = urllib.request.urlopen(req_2).read()
        rta_2 = json.loads(r_2.decode('utf-8'))

        cantidad = rta_2['count']
        valores = rta_2['results']

        opciones_ajustes = []
        opcion_temp = []

        for i in valores:
            opcion_temp.append(i)
            for j in valores[i]:
                opcion_temp.append(j)
            opciones_ajustes.append(opcion_temp)
            opcion_temp = []

        interacciones = list_interactions()
        #self.printMessage(messageProtocolEntity)

        # TIEMPO RANDOM ENTRE LAS RESPUESTAS PARA QUE NO NOS BLOQUEE WHATSAPP
        sleep(randint(3, 5)) # en segundos
        
        # VERIFICO QUE NO HAYA PASADO POR LA ETAPA 1 DE LA SOLICITUD
        # SI ES EL PRIMER MENSAJE LE DOY LA BIENVENIDA Y LE SOLICITO LA UBICACIÓN
        if interacciones.is_in_inicio(int(messageProtocolEntity.getFrom(False))) == 0:
            self.enviarMensaje(messageProtocolEntity, "Bienvenido a SIEM. Compartime tu ubicación, así sabremos a donde enviar la ambulancia.")
            interacciones.add_new_interaction(messageProtocolEntity.getFrom(False), "Saludo") 
            print("PASO 1: (%s) Bienvenida." % str(messageProtocolEntity.getFrom(False)))
        
        # SI NO ES EL PRIMER MENSAJE Y ME DIO LA UBICACIÓN LE MUESTRO LA LISTA DE MOTIVOS
        elif interacciones.is_in_motivo(int(messageProtocolEntity.getFrom(False))) == 0 and messageProtocolEntity.getType() == 'media' and messageProtocolEntity.getMediaType() == "location":
            print("PASO 3: (%s) Síntomas." % str(messageProtocolEntity.getFrom(False)))
            interacciones.add_new_interaction(messageProtocolEntity.getFrom(False), "Motivo")
            interacciones.add_ubicacion(messageProtocolEntity.getFrom(False),messageProtocolEntity.getLatitude(),messageProtocolEntity.getLongitude())
            
            msj = "Por favor, indique los síntomas que presenta. Responda con el número correspondiente a la opción separado por coma.\n\n"

            for i in range(0,len(opciones)):
                msj = msj + str(i+1) + '. ' + opciones[i][0] + '\n'

            msj = msj + '\nPor ejemplo: 1,2 si posee ' + opciones[0][0] + ' y ' + opciones[1][0] + '.'

            self.enviarMensaje(messageProtocolEntity, msj) 
        
        # SI NO ES EL PRIMER MENSAJE Y ME DIO LA UBICACIÓN SE LA VUELVO A PEDIR 
        elif interacciones.is_in_motivo(int(messageProtocolEntity.getFrom(False))) == 0 and messageProtocolEntity.getType() == 'text':
            print("PASO 2: (%s) No envió ubicacion." % str(messageProtocolEntity.getFrom(False)))
            self.enviarMensaje(messageProtocolEntity, "Para enviar la ubicación utilice el clip para datos adjuntos y luego seleccione Enviar mi ubicación actual.")
        
        # SI YA ME ENVIÓ LA UBICACION VERIFICO QUE NO ME HAYA MANDADO LOS SINTOMAS
        elif interacciones.is_in_motivo(int(messageProtocolEntity.getFrom(False))) == 1 and interacciones.is_in_motivo_rta(int(messageProtocolEntity.getFrom(False))) == 0:
            print("PASO 4: (%s) Gravedad de cada síntoma." % str(messageProtocolEntity.getFrom(False)))
            # VALIDAR QUE LA RESPUESTA SEA ALGUNA DE LAS OPCIONES
            mensaje = messageProtocolEntity.getBody()
            lista = mensaje.split(",")

            error = 0
            sintomas_rta = ''

            if error == 0:
                for i in range(len(lista)):
                    try:
                        int(lista[i].strip())
                    except ValueError:
                        error = 1

            if error == 0:
                for item in lista:
                    if int(item.strip()) > 0 and int(item.strip()) <= len(opciones):
                        sintomas_rta = sintomas_rta + ' ' + opciones[int(item)-1][0]
                    else:
                        error = 1

            if sintomas_rta == '' or error == 1:
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
        elif interacciones.is_in_motivo_rta(int(messageProtocolEntity.getFrom(False))) == 1 and interacciones.is_in_sintona_rta(int(messageProtocolEntity.getFrom(False))) == 0:
            print("PASO 5: (%s) Primer ajuste." % str(messageProtocolEntity.getFrom(False)))
            sintomas = interacciones.get_sintomas(int(messageProtocolEntity.getFrom(False)))

            lista = []

            for j in range(len(sintomas)):
                for i in range(len(opciones)):
                    if opciones[i][0] == sintomas[j].replace("\n",""):
                        lista.append(i+1)

            mensaje = messageProtocolEntity.getBody()
            sintomas_gravedad = mensaje.split(",")

            error = 0

            if len(lista) != len(sintomas_gravedad):
                error = 1

            if error == 0:
                for i in range(len(sintomas_gravedad)):
                    try:
                        int(sintomas_gravedad[i].strip())
                    except ValueError:
                        error = 1

            if error == 0:
                j = 0
                for i in range(len(lista)):
                    if int(sintomas_gravedad[j].strip()) > len(opciones[int(lista[i])-1])-1:
                        error = 1
                    j = j + 1

            if len(sintomas) != len(sintomas_gravedad):
                msj = "No ha ingresado una opción válida. "
                msj = msj + "Indique la gravedad de cada sintoma separado por coma y en el orden provisto:\n"

                for i in lista:
                    msj = msj + '\n' + opciones[int(i)-1][0] + ':\n'
                    for j in range(1,len(opciones[int(i)-1])):
                        msj = msj + str(j) + '. ' + opciones[int(i)-1][j] + '\n'
                        j=j+1 
                
                self.enviarMensaje(messageProtocolEntity,msj)

            elif error == 1:            
                msj = "No ha ingresado una opción válida. "
                msj = msj + "Indique la gravedad de cada sintoma separado por coma y en el orden provisto:\n"

                for i in lista:
                    msj = msj + '\n' + opciones[int(i)-1][0] + ':\n'
                    for j in range(1,len(opciones[int(i)-1])):
                        msj = msj + str(j) + '. ' + opciones[int(i)-1][j] + '\n'
                        j=j+1 
                    
                self.enviarMensaje(messageProtocolEntity,msj)

            else:
                j=0
                msj = "Ha seleccionado: \n"
                sintomas_rta = ''
                for i in lista:
                    msj = msj + str(opciones[int(i-1)][0]) + ' -> ' + str(opciones[int(i-1)][int(sintomas_gravedad[int(j)])]) + '\n'
                    sintomas_rta = sintomas_rta + ' ' + str(opciones[int(i-1)][int(sintomas_gravedad[int(j)])])
                    j = j + 1

                #self.enviarMensaje(messageProtocolEntity,msj)
                msj = "Le haremos unas últimas preguntas. Responda el número correspondiente a la opción adecuada."
                self.enviarMensaje(messageProtocolEntity,msj)
                interacciones.add_sintomas_rta(messageProtocolEntity.getFrom(False),sintomas_rta.strip().replace(' ',';'))
                ajustes = ''
                for i in range(0,len(opciones_ajustes)):
                    ajustes = ajustes + ' ' + opciones_ajustes[i][0]
                interacciones.add_ajustes(messageProtocolEntity.getFrom(False),ajustes.strip().replace(' ',';'))

                msj = opciones_ajustes[0][0] + ':\n'
                for i in range(1,len(opciones_ajustes[0])):
                    msj = msj + str(i) + '. ' + str(opciones_ajustes[0][i]) + '\n'

                self.enviarMensaje(messageProtocolEntity,msj)
                
                # CREO EL ARCHIVO CON LAS RESPUESTAS A LOS AJUSTES VACIO
                file = 'files_chat/ajustes/' + str(messageProtocolEntity.getFrom(False)) + '.txt'
                try:
                   open(file, 'x')
                except FileExistsError:
                   pass


        # SI YA ME ENVIÓ LOS SINTOMAS Y LA GRAVEDAD AHORA TENGO QUE PREGUNTARLE LOS FACTORES DE AJUSTE
        elif interacciones.is_in_sintona_rta(int(messageProtocolEntity.getFrom(False))) == 1 and interacciones.is_in_ajustes_rta_final(int(messageProtocolEntity.getFrom(False))) == 0:
            print("PASO 6: (%s) Otros ajustes." % str(messageProtocolEntity.getFrom(False)))

            respuesta = messageProtocolEntity.getBody()

            ajustes_opc = interacciones.get_ajustes(int(messageProtocolEntity.getFrom(False)))
            ajustes_respuesta = interacciones.get_ajustes_rta(int(messageProtocolEntity.getFrom(False)))

            aj_opc = len(ajustes_opc)
            aj_rta = len(ajustes_respuesta)

            if aj_opc != aj_rta:

                error = 0

                try:
                    int(respuesta.strip())
                except ValueError:
                    error = 1
                
                if error == 0:
                    if int(respuesta.strip()) > len(opciones_ajustes[aj_rta])-1:
                        error = 1

                #print(error)

                if error == 0:
                    #Guardo respuesta
                    if aj_rta == 0:
                        msj = opciones_ajustes[aj_rta][int(respuesta.strip())] #+ '&'
                    else:
                        msj = ajustes_respuesta[0].replace('\n','')
                        for i in range(1,len(ajustes_respuesta)):
                            msj = msj + '&' + ajustes_respuesta[i].replace('\n','')
                        msj = msj + '&' + opciones_ajustes[aj_rta][int(respuesta.strip())].replace('\n','')

                    interacciones.add_ajustes_rta(messageProtocolEntity.getFrom(False),msj.strip().replace('&',';'))
                    
                    if aj_opc != aj_rta+1:
                        #Muestro opciones siguientes
                        msj = opciones_ajustes[aj_rta+1][0] + ':\n'
                        for i in range(1,len(opciones_ajustes[aj_rta+1])):
                            msj = msj + str(i) + '. ' + str(opciones_ajustes[aj_rta+1][i]) + '\n'
                    else:
                        #Muestro resumen de pedido de auxilio
                        interacciones.add_ajustes_rta_finales(messageProtocolEntity.getFrom(False))
                        msj = 'Auxilio a ingresar:\n\n'

                        file = 'files_chat/auxilios/' + str(messageProtocolEntity.getFrom(False)) + '.txt'
                        arch = open(file,'r')
                        i = 1
                        for line in arch:
                            if i == 2:
                                sint = line.split(";")
                            if i == 3:
                                sint_grav = line.split(";")
                            if i == 4:
                                ajust = line.split(";")
                            if i == 5:
                                ajust_rta = line.split(";")
                            i = i + 1

                        for i in range(len(sint)):
                            msj = msj + sint[i].replace('\n','') + ': ' + sint_grav[i].replace('\n','') + '\n'

                        for i in range(len(ajust)):
                            msj = msj + ajust[i].replace('\n','') + ': ' + ajust_rta[i].replace('\n','') + '\n'

                        msj = msj + '\nPara confirmar envíe OK, de lo contrario envíe la palabra BAJA.'

                    self.enviarMensaje(messageProtocolEntity,msj)

                if error == 1:
                    #Envió error
                    #Muestro nuevamente opciones
                    msj = "Por favor, responda el número correspondiente a la opción.\n\n"
                    msj = msj + opciones_ajustes[aj_rta][0] + ':\n'
                    for i in range(1,len(opciones_ajustes[aj_rta])):
                        msj = msj + str(i) + '. ' + str(opciones_ajustes[aj_rta][i]) + '\n'

                    self.enviarMensaje(messageProtocolEntity,msj)

        # RESPONDIO TODAS LAS PREGUNTAS, SOLO QUEDA LA CONFIRMACION DEL AUXILIOS
        elif interacciones.is_in_ajustes_rta_final(int(messageProtocolEntity.getFrom(False))) == 1 :
            
            respuesta = messageProtocolEntity.getBody()

            if respuesta.strip().upper() == 'OK':
                # INGRESO EL AUXILIO AL SISTEMA
                print("PASO 7: (%s) Confirma ingreso de auxilio." % str(messageProtocolEntity.getFrom(False)))
                codigo_seguimiento = 'JSD35D12' #ingresar_auxilio(messageProtocolEntity.getFrom(False)))
                msj = 'Su auxilio ha sido ingresado al sistema. Puede realizar el seguimiento a través de SIEM Mobile con el código de seguimiento: ' + codigo_seguimiento

            elif respuesta.strip().upper() == 'BAJA':
                # BORRO LAS INTERACCIONES PARA QUE PUEDA SOLICITAR OTROS AUXILIO
                print("PASO 8: (%s) Cancela ingreso de auxilio." % str(messageProtocolEntity.getFrom(False)))
                interacciones.eliminar_solicitud(int(messageProtocolEntity.getFrom(False)))
                msj = 'Su auxilio ha sido cancelado.'

            else:
                #RESPUESTA INCORRECTA, VUELVO A PREGUNTAR SI ESTA OK CON EL AUXILIO
                print("PASO 9: (%s) Error en la confirmación." % str(messageProtocolEntity.getFrom(False)))
                msj = 'Para confirmar el ingreso del auxilio envíe OK, de lo contrario envíe la palabra BAJA.'

            self.enviarMensaje(messageProtocolEntity,msj)
        
        # ENVIO EL ACK Y LEIDO
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
