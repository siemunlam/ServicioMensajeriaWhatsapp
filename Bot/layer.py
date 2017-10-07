# coding=utf-8

from random import randint
from time import sleep

from bot_utils import Message
from yowsup.layers.interface import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.protocol_messages.protocolentities import TextMessageProtocolEntity

from chat_list import list_interactions

import urllib.request
import json
import requests

class EchoLayer(YowInterfaceLayer):

    @ProtocolEntityCallback("message")
    def onMessage(self, messageProtocolEntity):

        # CARGO LAS OPCIONES DE SINTOMAS (FACTORES DE PRECATEGORIZACION)
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

		# ORDENO DE ACUERDO A LA PRIMERA COLUMNA PORQUE LA API ENVIA ALEATORIAMENTE
        opciones = sorted(opciones, key=lambda x: x[0], reverse=False)

        # CARGO LAS OPCIONES DE LOS AJUSTES
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
            opcion_temp.append("Sin informacion")
            opciones_ajustes.append(opcion_temp)
            opcion_temp = []
			
		# ORDENO DE ACUERDO A LA PRIMERA COLUMNA PORQUE LA API ENVIA ALEATORIAMENTE
        opciones_ajustes = sorted(opciones_ajustes, key=lambda x: x[0], reverse=False)

        interacciones = list_interactions()
		
        # TIEMPO RANDOM ENTRE LAS RESPUESTAS PARA QUE NO NOS BLOQUEE WHATSAPP
        sleep(randint(2, 4)) # en segundos
        
        # VERIFICO QUE NO HAYA PASADO POR LA ETAPA 1 DE LA SOLICITUD
        # SI ES EL PRIMER MENSAJE LE DOY LA BIENVENIDA Y LE SOLICITO LA UBICACIÓN
        if interacciones.is_in_inicio(int(messageProtocolEntity.getFrom(False))) == 0:
            print("(%s) Bienvenida." % str(messageProtocolEntity.getFrom(False)))
            self.enviarMensaje(messageProtocolEntity, "Bienvenido a *_SIEM_*! Compartime tu ubicación así podremos asistirte. En cualquier momento de la conversación podés enviar la palabra *BAJA* para cancelar la solicitud.")
            interacciones.add_new_interaction(messageProtocolEntity.getFrom(False), "Saludo")
        
        # DURANTE CUALQUIER MOMENTO PUEDE CANCELAR EL AUXILIO Y REINICIAR LAS OPCIONES
        elif self.is_text(messageProtocolEntity) == 1 and interacciones.is_in_inicio(int(messageProtocolEntity.getFrom(False))) == 1 and self.envio_baja(messageProtocolEntity) == 1:
			# BORRO LAS INTERACCIONES PARA QUE PUEDA SOLICITAR OTROS AUXILIO
            print("(%s) Cancela ingreso de auxilio." % str(messageProtocolEntity.getFrom(False)))
            mensaje = messageProtocolEntity.getBody()
            interacciones.eliminar_solicitud(int(messageProtocolEntity.getFrom(False)))
            msj = 'Su auxilio ha sido cancelado. Envíe un mensaje para solicitar un nuevo auxilio.'
            self.enviarMensaje(messageProtocolEntity, msj) 
		
		# SI NO ES EL PRIMER MENSAJE Y NO ME DIO LA UBICACIÓN SE LA VUELVO A PEDIR 
        elif interacciones.is_in_inicio(int(messageProtocolEntity.getFrom(False))) == 1 and interacciones.is_in_ubic(int(messageProtocolEntity.getFrom(False))) == 0 and self.is_location(messageProtocolEntity) == 0:
            print("(%s) Error (No compartio coordenadas)." % str(messageProtocolEntity.getFrom(False)))
            self.enviarMensaje(messageProtocolEntity, "Para compartir la ubicación seleccione la opción para datos adjuntos y luego *Ubicación*")
			
		# SI NO ES EL PRIMER MENSAJE Y ME DIO LA UBICACIÓN LE PIDO DETALLES ADICIONALES SOBRE LA DIRECCION
        elif interacciones.is_in_inicio(int(messageProtocolEntity.getFrom(False))) == 1 and interacciones.is_in_ubic(int(messageProtocolEntity.getFrom(False))) == 0 and self.is_location(messageProtocolEntity) == 1:
            print("(%s) Se solicita ubicacion especifica (referencia)." % str(messageProtocolEntity.getFrom(False)))
            interacciones.add_ubicacion(messageProtocolEntity.getFrom(False),messageProtocolEntity.getLatitude(),messageProtocolEntity.getLongitude())

            # pegarle a la api de google y mostrarle la ubicacion
            # mensaje = Con la ubicacion enviada hemos identificado la siguiente direccion: 
            # Para mayor presicion, envie su direccion exacta. Por ejemplo: ...

            msj = "Por favor, adicionalmente envíe su dirección y cualquier detalle adicional para facilitar la localización.\nPor ejemplo: _Av. Rivadavia 1500 3 A puerta blanca_"
            self.enviarMensaje(messageProtocolEntity, msj) 
		
		# SI ME DIO LA UBICACION Y LA UBICACION ESPECIFICA, MUESTRO LOS SINTOMAS
        elif interacciones.is_in_ubic(int(messageProtocolEntity.getFrom(False))) == 1 and interacciones.is_in_ubic_espec(int(messageProtocolEntity.getFrom(False))) == 0 and self.is_text(messageProtocolEntity) == 1:
            print("(%s) Se envia lista de sintomas." % str(messageProtocolEntity.getFrom(False)))
            #interacciones.add_new_interaction(messageProtocolEntity.getFrom(False), "Motivo")
            mensaje = messageProtocolEntity.getBody()
            mensaje = str(mensaje).strip()
            interacciones.add_ubicacion_esp(messageProtocolEntity.getFrom(False),mensaje)

            msj = "Para indicar los síntomas responda con el número correspondiente a la opción separado por coma.\n\n"
            # validar cantidad de opciones disponibles
            for i in range(0,len(opciones)):
                msj = msj + str(i+1) + '. ' + opciones[i][0] + '\n'

            msj = msj + '\nPor ejemplo: 1,2 si posee ' + opciones[0][0] + ' y ' + opciones[1][0] + '.'

            self.enviarMensaje(messageProtocolEntity, msj) 

        # SI YA ME ENVIÓ LA UBICACION VERIFICO QUE NO ME HAYA MANDADO LOS SINTOMAS
        elif interacciones.is_in_ubic_espec(int(messageProtocolEntity.getFrom(False))) == 1 and interacciones.is_in_motivo_rta(int(messageProtocolEntity.getFrom(False))) == 0 and self.is_text(messageProtocolEntity) == 1:
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
                    if abs(int(item.strip())) > 0 and abs(int(item.strip())) <= len(opciones):
                        sintomas_rta = sintomas_rta + ' ' + opciones[abs(int(item))-1][0]
                    else:
                        error = 1

            if sintomas_rta == '' or error == 1:
                print("(%s) Error (Opcion incorrecta de Sintoma)." % str(messageProtocolEntity.getFrom(False)))
                msj = "No ha ingresado una opción válida. "
                msj = msj + "Para indicar los síntomas responda con el número correspondiente a la opción separado por coma.\n\n"

                for i in range(0,len(opciones)):
                    msj = msj + str(i+1) + '. ' + opciones[i][0] + '\n'

                msj = msj + '\nPor ejemplo: 1,2 si posee ' + opciones[0][0] + ' y ' + opciones[1][0] + '.'

                self.enviarMensaje(messageProtocolEntity, msj) 
            else:
                print("(%s) Se envia gravedad de cada sintoma." % str(messageProtocolEntity.getFrom(False)))
                lista_2 = []
                # ELIMINO LOS DUPLICADOS PARA QUE NO MUESTRE OPCIONES SI PONGO EL MISMO SINTOMA VARIAS VECES
                for i in lista:
                    lista_2.append(abs(int(i.strip())))
                    
                lista = list(set(lista_2))

                sintomas_rta = ''
                j = 0
                for item in lista:
                    if j == 0:
                        sintomas_rta = opciones[item-1][0]
                        j = j + 1
                    else:
                        sintomas_rta = sintomas_rta + '#' + opciones[item-1][0]

                interacciones.add_sintomas(messageProtocolEntity.getFrom(False),sintomas_rta.strip().replace('#',';'))
                
                msj = "Indique la gravedad de cada síntoma separado por coma y en el orden provisto:\n"

                for i in lista:
                    msj = msj + '\n' + opciones[i-1][0] + ':\n'
                    for j in range(1,len(opciones[i-1])):
                        msj = msj + str(j) + '. ' + opciones[i-1][j] + '\n'
                        j=j+1 
                
                # ver de armar un ejemplo con las dos primeras opciones
                self.enviarMensaje(messageProtocolEntity,msj) 

        # SI YA ME ENVIÓ LOS SINTOMAS Y NO LA GRAVEDAD DE CADA UNO
        elif interacciones.is_in_motivo_rta(int(messageProtocolEntity.getFrom(False))) == 1 and interacciones.is_in_sintona_rta(int(messageProtocolEntity.getFrom(False))) == 0 and self.is_text(messageProtocolEntity) == 1:
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
                    if abs(int(sintomas_gravedad[j].strip())) > len(opciones[int(lista[i])-1])-1:
                        error = 1
                    j = j + 1

            if len(sintomas) != len(sintomas_gravedad):
                print("(%s) Error (Opcion erronea de gravedad de sintoma)." % str(messageProtocolEntity.getFrom(False)))
                msj = "No ha ingresado una opción valida. "
                msj = msj + "Indique la gravedad de cada síntoma separado por coma y en el orden provisto:\n"

                for i in lista:
                    msj = msj + '\n' + opciones[abs(int(i))-1][0] + ':\n'
                    for j in range(1,len(opciones[abs(int(i))-1])):
                        msj = msj + str(j) + '. ' + opciones[ans(int(i))-1][j] + '\n'
                        j=j+1 
                
                self.enviarMensaje(messageProtocolEntity,msj)

            elif error == 1:   
                print("(%s) Error (Opción erronea de gravedad de sintoma)." % str(messageProtocolEntity.getFrom(False)))
                msj = "No ha ingresado una opción válida. "
                msj = msj + "Indique la gravedad de cada síntoma separado por coma y en el orden provisto:\n"

                for i in lista:
                    msj = msj + '\n' + opciones[abs(int(i))-1][0] + ':\n'
                    for j in range(1,len(opciones[abs(int(i))-1])):
                        msj = msj + str(j) + '. ' + opciones[abs(int(i))-1][j] + '\n'
                        j=j+1 
                    
                self.enviarMensaje(messageProtocolEntity,msj)

            else:
                print("(%s) Se solicita primer ajuste." % str(messageProtocolEntity.getFrom(False)))
                j=0
                msj = "Ha seleccionado: \n"
                sintomas_rta = ''
                for i in lista:
                    msj = msj + str(opciones[int(i-1)][0]) + ' -> ' + str(opciones[int(i-1)][abs(int(sintomas_gravedad[int(j)]))]) + '\n'
                    sintomas_rta = sintomas_rta + ' ' + str(opciones[int(i-1)][abs(int(sintomas_gravedad[int(j)]))])
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
        elif interacciones.is_in_sintona_rta(int(messageProtocolEntity.getFrom(False))) == 1 and interacciones.is_in_ajustes_rta_final(int(messageProtocolEntity.getFrom(False))) == 0 and self.is_text(messageProtocolEntity) == 1:

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
                    if abs(int(respuesta.strip())) > len(opciones_ajustes[aj_rta])-1:
                        error = 1

                if error == 0:
                    #Guardo respuesta
                    if aj_rta == 0:
                        msj = opciones_ajustes[aj_rta][abs(int(respuesta.strip()))] #+ '&'
                    else:
                        msj = ajustes_respuesta[0].replace('\n','')
                        for i in range(1,len(ajustes_respuesta)):
                            msj = msj + '&' + ajustes_respuesta[i].replace('\n','')
                        msj = msj + '&' + opciones_ajustes[aj_rta][abs(int(respuesta.strip()))].replace('\n','')

                    interacciones.add_ajustes_rta(messageProtocolEntity.getFrom(False),msj.strip().replace('&',';'))
                    
                    if aj_opc != aj_rta+1:
                        #Muestro opciones siguientes
                        print("(%s) Se solicita otro ajuste." % str(messageProtocolEntity.getFrom(False)))
                        msj = opciones_ajustes[aj_rta+1][0] + ':\n'
                        for i in range(1,len(opciones_ajustes[aj_rta+1])):
                            msj = msj + str(i) + '. ' + str(opciones_ajustes[aj_rta+1][i]) + '\n'
                    else:
                        #Muestro resumen de pedido de auxilio
                        print("(%s) Se envia resumen de auxilio." % str(messageProtocolEntity.getFrom(False)))
                        interacciones.add_ajustes_rta_finales(messageProtocolEntity.getFrom(False))
                        msj = '*Auxilio a ingresar:*\n'

                        file = 'files_chat/auxilios/' + str(messageProtocolEntity.getFrom(False)) + '.txt'
                        arch = open(file,'r')
                        i = 1
                        for line in arch:
                            if i == 1:
                                geo = line.split(";")
                                lat = geo[0].replace('\n','').strip()
                                lon = geo[1].replace('\n','').strip()
                                url = 'https://maps.googleapis.com/maps/api/geocode/json?latlng=' + str(lat) + ',' + str(lon) + '&sensor=true&key=AIzaSyAtqaY7C-E04P3SMY9ANVaQMDsB2I24w8o'
                                req = urllib.request.Request(url)
                                r = urllib.request.urlopen(req).read()
                                rta = json.loads(r.decode('utf-8'))
                                ubicacion = '_Ubicación:_ ' + rta['results'][0]['formatted_address']
                            if i == 2:
                                ubicacion_esp = line.replace('\n','').strip()
                                ubicacion_especifica = '_Referencia_: ' + ubicacion_esp
                            if i == 3:
                                sint = line.split(";")
                            if i == 4:
                                sint_grav = line.split(";")
                            if i == 5:
                                ajust = line.split(";")
                            if i == 6:
                                ajust_rta = line.split(";")
                            i = i + 1

                        msj = msj + ubicacion + '\n' + ubicacion_especifica + '\n'

                        for i in range(len(sint)):
                            msj = msj + '_' + sint[i].replace('\n','') + '_: ' + sint_grav[i].replace('\n','') + '\n'

                        for i in range(len(ajust)):
                            if ajust_rta[i].replace('\n','') != "Sin informacion":
                                msj = msj + '_' + ajust[i].replace('\n','') + '_: ' + ajust_rta[i].replace('\n','') + '\n'

                        msj = msj + '\nPara confirmar envíe *OK*, de lo contrario envíe la palabra *BAJA*.'

                    self.enviarMensaje(messageProtocolEntity,msj)

                if error == 1:
                    #Envió error
                    print("(%s) Error (No envio opcion valida de ajuste)" % str(messageProtocolEntity.getFrom(False)))
                    #Muestro nuevamente opciones
                    msj = "Por favor, responda el número correspondiente a la opcion.\n\n"
                    msj = msj + opciones_ajustes[aj_rta][0] + ':\n'
                    for i in range(1,len(opciones_ajustes[aj_rta])):
                        msj = msj + str(i) + '. ' + str(opciones_ajustes[aj_rta][i]) + '\n'

                    self.enviarMensaje(messageProtocolEntity,msj)

        # RESPONDIO TODAS LAS PREGUNTAS, SOLO QUEDA LA CONFIRMACION DEL AUXILIOS
        elif interacciones.is_in_ajustes_rta_final(int(messageProtocolEntity.getFrom(False))) == 1 and self.is_text(messageProtocolEntity) == 1 and interacciones.is_in_cod_seg(int(messageProtocolEntity.getFrom(False))) == 0:
            
            respuesta = messageProtocolEntity.getBody()

            if respuesta.strip().upper() == 'OK':
                # INGRESO EL AUXILIO AL SISTEMA
                print("(%s) Ingreso auxilio a SIEM." % str(messageProtocolEntity.getFrom(False)))
                
                # ARMO EL STRING CON FORMATO JSON
                file = 'files_chat/auxilios/' + str(messageProtocolEntity.getFrom(False)) + '.txt'
                arch = open(file,'r')
                i = 1
                for line in arch:
                    if i == 1:
                        geo = line.split(";")
                        lat = geo[0].replace('\n','').strip()
                        lon = geo[1].replace('\n','').strip()
                        url = 'https://maps.googleapis.com/maps/api/geocode/json?latlng=' + str(lat) + ',' + str(lon) + '&sensor=true&key=AIzaSyAtqaY7C-E04P3SMY9ANVaQMDsB2I24w8o'
                        req = urllib.request.Request(url)
                        r = urllib.request.urlopen(req).read()
                        rta = json.loads(r.decode('utf-8'))
                        ubicacion = rta['results'][0]['formatted_address']
                    if i == 2:
                        ubicacion_especifica = line.replace('\n','').strip()
                    if i == 3:
                        sint = line.split(";")
                    if i == 4:
                        sint_grav = line.split(";")
                    if i == 5:
                        ajust = line.split(";")
                    if i == 6:
                        ajust_rta = line.split(";")
                    i = i + 1

                motivos_str = ''

                for i in range(len(sint)):
                    motivos_str = motivos_str + '\\"' + str(sint[i]).replace('\n','').strip() + '\\":\\"' + str(sint_grav[i]).replace('\n','').strip() + '\\",'

                for i in range(len(ajust)):
                    if str(ajust_rta[i]).replace('\n','').strip() != "Sin informacion":
                        motivos_str = motivos_str + '\\"' + str(ajust[i]).replace('\n','').strip() + '\\":\\"' + str(ajust_rta[i]).replace('\n','').strip() + '\\",'

                motivos_str = motivos_str[:-1]
                contacto_tel = str(messageProtocolEntity.getFrom(False))
                auxilio_json = '{' + '"ubicacion":"' + ubicacion + '",' + '"ubicacion_especifica":"' + ubicacion_especifica + '",' + '"latitud_gps":"' + lat + '",' + '"longitud_gps":"' + lon + '",' + '"contacto":"' + contacto_tel + '",' + '"motivo":"{' + motivos_str + '}",' + '"origen":"2"' +'}'
                data = json.loads(auxilio_json)
                r = requests.post('http://siemunlam.pythonanywhere.com/api/auxilios/', json=data)
                respuesta_json = json.loads(r.text)
                # ME DEVUELVE EL CODIGO DE SUSCRIPCION
                codigo_seguimiento = respuesta_json['codigo_suscripcion']
                #codigo_seguimiento = 'JJJJJJJ1234'
                # AGREGO EL CODIGO DE SEGUIMIENTO AL ARCHIVO
                interacciones.add_cod_seg(int(messageProtocolEntity.getFrom(False)), codigo_seguimiento)
                msj = 'Su auxilio ha sido ingresado a *_SIEM._*\nPuede realizar el seguimiento utilizando la aplicación *_SIEM Mobile_* con el código: ' + codigo_seguimiento

                # ELIMINO LA SOLICUTUD PORQUE YA FUE INGRESADA A SIEM
                arch.close()
                interacciones.eliminar_solicitud(int(messageProtocolEntity.getFrom(False)))
				
            else:
                #RESPUESTA INCORRECTA, VUELVO A PREGUNTAR SI ESTA OK CON EL AUXILIO
                print("(%s) Error (No confirma ingreso de auxilio)." % str(messageProtocolEntity.getFrom(False)))
                msj = 'Para confirmar el ingreso del auxilio envíe *OK*, de lo contrario envíe la palabra *BAJA*.'

            self.enviarMensaje(messageProtocolEntity,msj)
				
        else:
            print("(%s) Error (Formato inválido)." % str(messageProtocolEntity.getFrom(False)))
            msj = 'Lo sentimos, el formato no es reconocido por *_SIEM_*. Intente nuevamente por favor.'
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
		
	
    def is_text(self, messageProtocolEntity):
        retorno = 0
        if messageProtocolEntity.getType() == 'text':
            retorno = 1
        return retorno
	
	
    def is_location(self, messageProtocolEntity):
        retorno = 0
        if messageProtocolEntity.getType() == 'media':
            if messageProtocolEntity.getMediaType() == "location":
                retorno = 1
        return retorno
	
	
    def envio_baja(self, messageProtocolEntity):
        retorno = 0
        mensaje = messageProtocolEntity.getBody()
		
        if self.is_text(messageProtocolEntity) == 1:
            if mensaje.strip().upper() == 'BAJA': 
                retorno = 1
        return retorno
	
	