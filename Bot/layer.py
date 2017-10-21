# coding=utf-8

from random import randint
from time import sleep

from yowsup.layers.interface import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.protocol_messages.protocolentities import TextMessageProtocolEntity

from chat_list import list_interactions

import urllib.request
import json
import requests

from datetime import datetime

class EchoLayer(YowInterfaceLayer):

    @ProtocolEntityCallback("message")
    def onMessage(self, messageProtocolEntity):

        # CARGO LAS OPCIONES DE SINTOMAS (FACTORES DE PRECATEGORIZACION)
        # print("CARGO LAS OPCIONES DE SINTOMAS (FACTORES DE PRECATEGORIZACION)")
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

        #print(opciones)

        # CARGO LAS OPCIONES DE LOS AJUSTES
        # print("CARGO LAS OPCIONES DE LOS AJUSTES")
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
            opcion_temp.append("Sin información")
            opciones_ajustes.append(opcion_temp)
            opcion_temp = []
			
		# ORDENO DE ACUERDO A LA PRIMERA COLUMNA PORQUE LA API ENVIA ALEATORIAMENTE
        opciones_ajustes = sorted(opciones_ajustes, key=lambda x: x[0], reverse=False)

        #print(opciones_ajustes)

        interacciones = list_interactions()
		
        # TIEMPO RANDOM ENTRE LAS RESPUESTAS PARA QUE NO NOS BLOQUEE WHATSAPP
        sleep(randint(2, 3)) # en segundos
        
        # VERIFICO QUE NO HAYA PASADO POR LA ETAPA 1 DE LA SOLICITUD
        # SI ES EL PRIMER MENSAJE LE DOY LA BIENVENIDA Y LE SOLICITO LA UBICACIÓN
        if interacciones.is_in_inicio(int(messageProtocolEntity.getFrom(False))) == 0:
            print("(%s) Bienvenida." % str(messageProtocolEntity.getFrom(False)))
            self.log("(" + str(messageProtocolEntity.getFrom(False)) + ") Bienvenida.")
            self.enviarMensaje(messageProtocolEntity, "Bienvenido a _*SIEM*_, compartime tu ubicación así podremos asistirte. Hace clic en el botón 📎 o ➕ y luego en *Ubicación.*\nPara cancelar la solicitud podés enviar la palabra *BAJA* en cualquier momento. *_Los mensajes de voz y videos serán omitidos._*")
            interacciones.add_new_interaction(messageProtocolEntity.getFrom(False), "Saludo")
        
        # DURANTE CUALQUIER MOMENTO PUEDE CANCELAR EL AUXILIO Y REINICIAR LAS OPCIONES
        elif self.is_text(messageProtocolEntity) == 1 and interacciones.is_in_inicio(int(messageProtocolEntity.getFrom(False))) == 1 and self.envio_baja(messageProtocolEntity) == 1:
			# BORRO LAS INTERACCIONES PARA QUE PUEDA SOLICITAR OTROS AUXILIO
            print("(%s) Cancela ingreso de auxilio." % str(messageProtocolEntity.getFrom(False)))
            self.log("(" + str(messageProtocolEntity.getFrom(False)) + ") Cancela ingreso de auxilio.")
            mensaje = messageProtocolEntity.getBody()
            interacciones.eliminar_solicitud(int(messageProtocolEntity.getFrom(False)))
            msj = 'Tu auxilio ha sido cancelado. Enviá un mensaje para solicitar uno nuevo.'
            self.enviarMensaje(messageProtocolEntity, msj) 
		
		# SI NO ES EL PRIMER MENSAJE Y NO ME DIO LA UBICACIÓN SE LA VUELVO A PEDIR 
        elif interacciones.is_in_inicio(int(messageProtocolEntity.getFrom(False))) == 1 and interacciones.is_in_ubic(int(messageProtocolEntity.getFrom(False))) == 0 and self.is_location(messageProtocolEntity) == 0:
            print("(%s) Error (No compartio coordenadas)." % str(messageProtocolEntity.getFrom(False)))
            self.log("(" + str(messageProtocolEntity.getFrom(False)) + ") Error (No compartio coordenadas).")
            self.enviarMensaje(messageProtocolEntity, "Hace clic en el botón 📎 o ➕ y luego en *Ubicación*")
			
		# SI NO ES EL PRIMER MENSAJE Y ME DIO LA UBICACIÓN LE PIDO DETALLES ADICIONALES SOBRE LA DIRECCION
        elif interacciones.is_in_inicio(int(messageProtocolEntity.getFrom(False))) == 1 and interacciones.is_in_ubic(int(messageProtocolEntity.getFrom(False))) == 0 and self.is_location(messageProtocolEntity) == 1:
            print("(%s) Se solicita ubicacion especifica (referencia)." % str(messageProtocolEntity.getFrom(False)))
            self.log("(" + str(messageProtocolEntity.getFrom(False)) + ") Se solicita ubicacion especifica (referencia).")
            interacciones.add_ubicacion(messageProtocolEntity.getFrom(False),messageProtocolEntity.getLatitude(),messageProtocolEntity.getLongitude())

            # LE MUESTRO LA DIRECCION QUE SE OBTUVO CON LAS COORDENADAS Y LE PIDO MÁS DETALLE
            lat = messageProtocolEntity.getLatitude()
            lon = messageProtocolEntity.getLongitude()
            url = 'https://maps.googleapis.com/maps/api/geocode/json?latlng=' + str(lat) + ',' + str(lon) + '&sensor=true&key=AIzaSyAtqaY7C-E04P3SMY9ANVaQMDsB2I24w8o'
            req = urllib.request.Request(url)
            r = urllib.request.urlopen(req).read()
            rta = json.loads(r.decode('utf-8'))
            ubi = rta['results'][0]['formatted_address']

            location = rta['results'][0]['address_components'][1]['short_name'] + ' ' + rta['results'][0]['address_components'][0]['short_name'] + ', ' + rta['results'][0]['address_components'][2]['short_name'] + ', ' + rta['results'][0]['address_components'][5]['short_name']

            msj = 'Con la ubicación enviada hemos identificado la siguiente dirección: *_' + location + '._*'
            msj = msj + '\nSi es correcta enviá *OK*, de lo contrario enviá tu dirección exacta y cualquier detalle adicional.\nPor ej: _Av. Rivadavia 1500 3 A puerta blanca_'
            # msj = "Por favor, adicionalmente envíe su dirección y cualquier detalle adicional para facilitar la localización.\nPor ejemplo: _Av. Rivadavia 1500 3 A puerta blanca_"
            self.enviarMensaje(messageProtocolEntity, msj) 
		
		# SI ME DIO LA UBICACION Y LA UBICACION ESPECIFICA, MUESTRO LOS SINTOMAS
        elif interacciones.is_in_ubic(int(messageProtocolEntity.getFrom(False))) == 1 and interacciones.is_in_ubic_espec(int(messageProtocolEntity.getFrom(False))) == 0 and self.is_text(messageProtocolEntity) == 1:
            try:
                mensaje = messageProtocolEntity.getBody()
                mensaje = str(mensaje).strip()
                interacciones.add_ubicacion_esp(messageProtocolEntity.getFrom(False),mensaje)

                msj = "Responde los números correspondientes a los síntomas que presentas separados por coma.\n\n"
                # validar cantidad de opciones disponibles
                for i in range(0,len(opciones)):
                    msj = msj + str(i+1) + '. ' + opciones[i][0] + '\n'

                if len(opciones) > 1:
                    msj = msj + '\nEj: 1,2 para indicar ' + opciones[0][0] + ' y ' + opciones[1][0] + '.'
                else:
                    msj = msj + '\nEj: 1 para indicar ' + opciones[0][0] + '.'
                print("(%s) Se envia lista de sintomas." % str(messageProtocolEntity.getFrom(False)))
                self.log("(" + str(messageProtocolEntity.getFrom(False)) + ") Se envia lista de sintomas.")

            except:
                msj = 'Por favor enviá tu dirección exacta para mayor precisión.\nPor ej: _Av. Rivadavia 1500 3 A puerta blanca_'
                print("(%s) Se solicita nuevamente ubicacion especifica (referencia)." % str(messageProtocolEntity.getFrom(False)))
                self.log("(" + str(messageProtocolEntity.getFrom(False)) + ") Se solicita nuevamente ubicacion especifica (referencia).")

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
                self.log("(" + str(messageProtocolEntity.getFrom(False)) + ") Error (Opcion incorrecta de Sintoma).")
                msj = ""#"Opción incorrecta. "
                msj = msj + "Responde los números correspondientes a los síntomas que presentas separados por coma.\n\n"

                for i in range(0,len(opciones)):
                    msj = msj + str(i+1) + '. ' + opciones[i][0] + '\n'

                if len(opciones) > 1:
                    msj = msj + '\nEj: 1,2 para indicar ' + opciones[0][0] + ' y ' + opciones[1][0] + '.'
                else:
                    msj = msj + '\nEj: 1 para indicar ' + opciones[0][0] + '.'

                self.enviarMensaje(messageProtocolEntity, msj) 
            else:

                #LE MUESTRO LA PRIMER LISTA DE SINTOMAS
                print("(%s) Se envia gravedad del primer sintoma." % str(messageProtocolEntity.getFrom(False)))
                self.log("(" + str(messageProtocolEntity.getFrom(False)) + ") Se envia gravedad del primer sintoma.")
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

                # AGREGO LOS SINTOMAS AL ARCHIVO DEL AUXILIO
                interacciones.add_sintomas(messageProtocolEntity.getFrom(False),sintomas_rta.strip().replace('#',';'))

                # CREO EL ARCHIVO CON LAS RESPUESTAS A LOS SINTOMAS VACIO
                file = 'files_chat/motivos_pc/' + str(messageProtocolEntity.getFrom(False)) + '.txt'
                try:
                   open(file, 'x')
                except FileExistsError:
                   pass
                
                msj = "Indique la gravedad del síntoma:\n"

                # LE MUESTRO LAS OPCIONES DEL PRIMER MOTIVO DE PRECATEGORIZACIÓN
                msj = msj + '\n' + opciones[lista[0]-1][0] + ':'
                for j in range(1,len(opciones[lista[0]-1])):
                    msj = msj + '\n' + str(j) + '. ' + opciones[lista[0]-1][j] 

                self.enviarMensaje(messageProtocolEntity,msj) 

        # SI YA ME ENVIÓ LOS SINTOMAS Y NO LA GRAVEDAD DE CADA UNO
        elif interacciones.is_in_motivo_rta(int(messageProtocolEntity.getFrom(False))) == 1 and interacciones.is_in_sintona_rta(int(messageProtocolEntity.getFrom(False))) == 0 and self.is_text(messageProtocolEntity) == 1:
            # sintomas = interacciones.get_sintomas(int(messageProtocolEntity.getFrom(False)))

            # RECIBO LA RESPUESTA DE LA GRAVEDAD DEL SINTOMA
            # TENGO QUE VALIDAR LA RESPUESTA 
            # DESPUES MUESTRO LAS OPCIONES DEL SIGUIENTE SINTOMA
            # SI NO HAY MAS SINTOMAS PARA MOSTRAR ENTONCES ENVIO LAS OPCIONES DEL PRIMER AJUSTE

            respuesta = messageProtocolEntity.getBody()

            #print("Sintomas_rta, motivos_rta")

            sintomas_rta = interacciones.get_sintomas(int(messageProtocolEntity.getFrom(False)))
            #print(sintomas_rta)

            motivos_rta = interacciones.get_sintomas_rta_aux(int(messageProtocolEntity.getFrom(False)))
            #print(motivos_rta)

            sin_rta = len(sintomas_rta)
            mot_rta = len(motivos_rta)

            indice = len(motivos_rta)
            busqueda = 0
            error = 0

            # VEO QUE LA RESPUESTA SEA UN NRO ENTERO POSITIVO
            try:
                int(respuesta.strip())
            except ValueError:
                error = 1

            try:
                if int(respuesta.strip()) <= 0:
                    error = 1
            except:
                error = 1

            if error == 0:
                # VEO QUE SEA UNA OPCION VALIDA DEL SINTOMA
                # BUSCO EL INDICE DEL SINTOMA AL QUE ME RESPONDE
                for i in range(len(opciones)):
                    if sintomas_rta[indice].replace('\n','') == opciones[i][0]:
                        busqueda = i
                        #print(indice)
                        #print(busqueda)

                if int(respuesta.strip()) > (int(len(opciones[busqueda])) - 1):
                    error = 1

            if error == 0:
                # PASO TODOS LOS CONTROLES, GUARDO LA RESPUESTA
                if mot_rta == 0:
                    msj = opciones[busqueda][abs(int(respuesta.strip()))] #+ '&'
                else:
                    msj = motivos_rta[0].replace('\n','')
                    for i in range(1,len(motivos_rta)):
                        msj = msj + '&' + motivos_rta[i].replace('\n','')
                    msj = msj + '&' + opciones[busqueda][abs(int(respuesta.strip()))].replace('\n','')

                interacciones.add_sintomas_rta_aux(messageProtocolEntity.getFrom(False),msj.strip().replace('&',';'))

                # VERIFICO SI ES LA ULTIMA RESPUESTA DE LOS SINTOMAS
                if sin_rta == (mot_rta + 1):
                    # NO TENGO MAS PREGUNTAS PARA HACERLE
                    # TENGO QUE INGRESAR LOS MOTIVOS AL ARCHIVO DEL AUXILIO
                    interacciones.add_sintomas_rta(messageProtocolEntity.getFrom(False),msj.strip().replace('&',';'))

                    # LE ENVIO EL PRIMER AJUSTE
                    print("(%s) Se solicita primer ajuste." % str(messageProtocolEntity.getFrom(False)))
                    self.log("(" + str(messageProtocolEntity.getFrom(False)) + ") Se solicita primer ajuste.")
                    
                    msj = "Te haremos unas últimas preguntas. Responde únicamente con el número de la opción adecuada."
                    self.enviarMensaje(messageProtocolEntity,msj)
                    
                    ajustes = ''
                    for i in range(0,len(opciones_ajustes)):
                        ajustes = ajustes + ' ' + opciones_ajustes[i][0]
                    interacciones.add_ajustes(messageProtocolEntity.getFrom(False),ajustes.strip().replace(' ',';'))

                    msj = opciones_ajustes[0][0] + ':\n'
                    for i in range(1,len(opciones_ajustes[0])):
                        msj = msj + str(i) + '. ' + str(opciones_ajustes[0][i]) + '\n'
                    
                    # CREO EL ARCHIVO CON LAS RESPUESTAS A LOS AJUSTES VACIO
                    file = 'files_chat/ajustes/' + str(messageProtocolEntity.getFrom(False)) + '.txt'
                    try:
                       open(file, 'x')
                    except FileExistsError:
                       pass

                else:
                    # TENGO QUE MOSTRARLE LAS SIGUIENTES OPCIONES DE LOS SINTOMAS
                    # LE MUESTRO LAS OPCIONES DEL PRIMER MOTIVO DE PRECATEGORIZACIÓN

                    # BUSCO EL INDICE DEL SIGUIENTE SINTOMA
                    print("(%s) Se envia gravedad de otro sintoma." % str(messageProtocolEntity.getFrom(False)))
                    self.log("(" + str(messageProtocolEntity.getFrom(False)) + ") Se envia gravedad de otro sintoma.")

                    busqueda = 0
                    for i in range(len(opciones)):
                        if sintomas_rta[indice + 1].replace('\n','') == opciones[i][0]:
                            busqueda = i

                    msj = opciones[busqueda][0] + ':'
                    for j in range(1,len(opciones[busqueda])):
                        msj = msj + '\n' + str(j) + '. ' + opciones[busqueda][j] 
                    

            if error == 1:
                # RESPUESTA INCORRECTA
                print("(%s) Opción incorrecta de sintoma." % str(messageProtocolEntity.getFrom(False)))
                self.log("(" + str(messageProtocolEntity.getFrom(False)) + ") Opción incorrecta de sintoma.")
                msj = "No has ingresado una opción valida."

            self.enviarMensaje(messageProtocolEntity,msj)


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
                        self.log("(" + str(messageProtocolEntity.getFrom(False)) + ") Se solicita otro ajuste.")
                        msj = opciones_ajustes[aj_rta+1][0] + ':\n'
                        for i in range(1,len(opciones_ajustes[aj_rta+1])):
                            msj = msj + str(i) + '. ' + str(opciones_ajustes[aj_rta+1][i]) + '\n'
                    else:
                        #Muestro resumen de pedido de auxilio
                        print("(%s) Se envia resumen de auxilio." % str(messageProtocolEntity.getFrom(False)))
                        self.log("(" + str(messageProtocolEntity.getFrom(False)) + ") Se envia resumen de auxilio.")
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
                                location = rta['results'][0]['address_components'][1]['short_name'] + ' ' + rta['results'][0]['address_components'][0]['short_name'] + ', ' + rta['results'][0]['address_components'][2]['short_name'] + ', ' + rta['results'][0]['address_components'][5]['short_name']
                                ubicacion = '_Ubicación:_ ' + location #rta['results'][0]['formatted_address']
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
                            if ajust_rta[i].replace('\n','') != "Sin información":
                                msj = msj + '_' + ajust[i].replace('\n','') + '_: ' + ajust_rta[i].replace('\n','') + '\n'

                        msj = msj + '\nPara confirmar enviá *OK*, de lo contrario, enviá *BAJA*.'

                    self.enviarMensaje(messageProtocolEntity,msj)

                if error == 1:
                    #Envió error
                    print("(%s) Error (No envio opcion valida de ajuste)." % str(messageProtocolEntity.getFrom(False)))
                    self.log("(" + str(messageProtocolEntity.getFrom(False)) + ") Error (No envio opcion valida de ajuste).")
                    # MUESTRO NUEVAMENTE LAS OPCIONES
                    msj = "Por favor, responde únicamente con el número de la opción adecuada.\n\n"
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
                self.log("(" + str(messageProtocolEntity.getFrom(False)) + ") Ingreso auxilio a SIEM.")
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
                        location = rta['results'][0]['address_components'][1]['short_name'] + ' ' + rta['results'][0]['address_components'][0]['short_name'] + ', ' + rta['results'][0]['address_components'][2]['short_name'] + ', ' + rta['results'][0]['address_components'][5]['short_name']
                        ubicacion = location #rta['results'][0]['formatted_address']
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
                    if str(ajust_rta[i]).replace('\n','').strip() != "Sin información":
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
                msj = 'Tu auxilio ha sido ingresado.\nPodés ver el seguimiento desde la aplicación *_SIEM Mobile_* con el código: ' + codigo_seguimiento
                self.log("(" + str(messageProtocolEntity.getFrom(False)) + ") Ingreso auxilio a SIEM - " + codigo_seguimiento)

                # ELIMINO LA SOLICUTUD PORQUE YA FUE INGRESADA A SIEM
                arch.close()
                interacciones.eliminar_solicitud(int(messageProtocolEntity.getFrom(False)))
				
            else:
                #RESPUESTA INCORRECTA, VUELVO A PREGUNTAR SI ESTA OK CON EL AUXILIO
                print("(%s) Error (No confirma ingreso de auxilio)." % str(messageProtocolEntity.getFrom(False)))
                self.log("(" + str(messageProtocolEntity.getFrom(False)) + ") Error (No confirma ingreso de auxilio).")
                msj = 'Para confirmar enviá *OK*, de lo contrario, enviá *BAJA*.'

            self.enviarMensaje(messageProtocolEntity,msj)
				
        else:
            print("(%s) Error (Formato inválido)." % str(messageProtocolEntity.getFrom(False)))
            self.log("(" + str(messageProtocolEntity.getFrom(False)) + ") Error (Formato invalido).")
            msj = 'Lo sentimos, el formato no es reconocido por *_SIEM_*. Intenta nuevamente por favor.'
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
        try:
            if messageProtocolEntity.getType() == 'text':
                retorno = 1
        except:
            retorno = 0
        return retorno
	
	
    def is_location(self, messageProtocolEntity):
        retorno = 0
        try:
            if messageProtocolEntity.getType() == 'media':
                if messageProtocolEntity.getMediaType() == "location":
                    retorno = 1
        except:
            retorno = 0
        return retorno
	
	
    def envio_baja(self, messageProtocolEntity):
        retorno = 0
        try:
            mensaje = messageProtocolEntity.getBody()
        except:
            pass
		
        try:
            if self.is_text(messageProtocolEntity) == 1:
                if mensaje.strip().upper() == 'BAJA': 
                    retorno = 1
        except:
            retorno = 0
        return retorno
    
    def log(self, msj):
        time = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        log_msj = time + ' - ' + msj
        log_file = 'logFile.log'
        # SI NO EXISTE LO CREO
        try:
            archivo_log = open(log_file, 'a')
        except:
            archivo_log = open(log_file, 'w+')
        archivo_log.write("%s\n" % log_msj)
        archivo_log.close()

