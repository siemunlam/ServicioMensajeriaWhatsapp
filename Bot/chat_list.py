import os

class list_interactions():
    
	def __init__(self):
		# LISTA CON NUMEROS QUE PASARON POR EL 1ER ESTADO
		self.inicio = []
		archivo_inicio = open('files_chat\inicio.txt', 'r')
		for line in archivo_inicio:
			self.inicio.append(int(line))


	# METODOS PARA AGREGAR DATOS AL ARCHIVO
	def add_new_interaction(self, from_number, interaccion):
		if interaccion == "Saludo":
			self.inicio.append(int(from_number)) 
			archivo_inicio = open('files_chat\inicio.txt', 'a')
			archivo_inicio.write("%s\n" % str(from_number))


	def add_ubicacion(self, from_number, latitud, longitud):
		linea = str(latitud) + ';' + str(longitud)
		arch = 'files_chat/auxilios/' + str(from_number) + '.txt'
		archivo_inicio = open(arch, 'w+')
		archivo_inicio.write("%s\n" % linea)
		archivo_inicio.close()

		
	def add_ubicacion_esp(self, from_number, ubicacion):
		linea = str(ubicacion)
		arch = 'files_chat/auxilios/' + str(from_number) + '.txt'
		archivo_inicio = open(arch, 'a')
		archivo_inicio.write("%s\n" % linea)
		archivo_inicio.close()
		

	def add_sintomas(self, from_number, sintomas):
		linea = str(sintomas)
		arch = 'files_chat/auxilios/' + str(from_number) + '.txt'
		archivo_inicio = open(arch, 'a')
		archivo_inicio.write("%s\n" % linea)
		archivo_inicio.close()


	def add_sintomas_rta(self, from_number, sintomas):
		linea = str(sintomas)
		arch = 'files_chat/auxilios/' + str(from_number) + '.txt'
		archivo_inicio = open(arch, 'a')
		archivo_inicio.write("%s\n" % linea)
		archivo_inicio.close()


	def add_ajustes(self, from_number, ajustes):
		linea = str(ajustes)
		arch = 'files_chat/auxilios/' + str(from_number) + '.txt'
		archivo_inicio = open(arch, 'a')
		archivo_inicio.write("%s\n" % linea)
		archivo_inicio.close()


	def add_ajustes_rta(self, from_number, ajustes):
		linea = str(ajustes)
		arch = 'files_chat/ajustes/' + str(from_number) + '.txt'
		archivo_inicio = open(arch, 'w')
		archivo_inicio.write("%s\n" % linea)
		archivo_inicio.close()


	def add_cod_seg(self, from_number, codigo):
		linea = codigo.strip()
		arch = 'files_chat/auxilios/' + str(from_number) + '.txt'
		archivo_inicio = open(arch, 'a')
		archivo_inicio.write("%s\n" % linea)
		archivo_inicio.close()


	def add_ajustes_rta_finales(self, from_number):
		file = 'files_chat/ajustes/' + str(from_number) + '.txt'
		arch = open(file,'r')
		file2 = 'files_chat/auxilios/' + str(from_number) + '.txt'
		arch2 = open(file2, 'a')
		i = 1
		for line in arch:
			if i == 1:
				arch2.write("%s" % line)
			i = i+1


	# METODOS GETS
	def get_data_inicio(self):
		return self.inicio
		
		
	def get_sintomas(self, from_number):
		lista = []
		file = 'files_chat/auxilios/' + str(from_number) + '.txt'
		arch = open(file,'r')
		i= 1
		for line in arch:
			if i == 3:
				line.replace("\n","")
				lista = line.split(";")
			i = i+1
		return lista


	def get_sintomas_rta(self, from_number):
		lista = []
		file = 'files_chat/auxilios/' + str(from_number) + '.txt'
		arch = open(file,'r')
		i= 1
		for line in arch:
			if i == 4:
				line.replace("\n","")
				lista = line.split(";")
			i = i+1
		return lista


	def get_ajustes(self, from_number):
		lista = []
		file = 'files_chat/auxilios/' + str(from_number) + '.txt'
		arch = open(file,'r')
		i= 1
		for line in arch:
			if i == 5:
				line.replace("\n","")
				lista = line.split(";")
			i = i+1
		return lista


	def get_ajustes_rta(self, from_number):
		lista = []
		file = 'files_chat/ajustes/' + str(from_number) + '.txt'
		try:
			arch = open(file,'r')
			for line in arch:
				line.replace("\n","")
				lista = line.split(";")
		except ValueError:
			lista = []
		return lista


	def get_ajustes_rta_final(self, from_number):
		lista = []
		file = 'files_chat/auxilios/' + str(from_number) + '.txt'
		arch = open(file,'r')
		i= 1
		for line in arch:
			if i == 6:
				line.replace("\n","")
				lista = line.split(";")
			i = i+1
		return lista


	# METODOS DE BUSQUEDA
	def is_in_inicio(self, from_number):
		if from_number not in self.inicio:
			return 0
		else:
			return 1


	def is_in_motivo_rta(self, from_number):
		lista = []
		file = 'files_chat/auxilios/' + str(from_number) + '.txt'
		arch = open(file,'r')
		i = 1
		for line in arch:
			if i == 3:
				line.replace("\n","")
				lista = line.split(";")
			i = i+1

		if len(lista) == 0:
			return 0
		else:
			return 1


	def is_in_sintona_rta(self, from_number):
		lista = []
		file = 'files_chat/auxilios/' + str(from_number) + '.txt'
		arch = open(file,'r')
		i = 1
		for line in arch:
			if i == 4:
				line.replace("\n","")
				lista = line.split(";")
			i = i+1

		if len(lista) == 0:
			return 0
		else:
			return 1


	def is_in_ajustes_rta_final(self, from_number):
		lista = []
		file = 'files_chat/auxilios/' + str(from_number) + '.txt'
		arch = open(file,'r')
		i = 1
		for line in arch:
			if i == 6:
				line.replace("\n","")
				lista = line.split(";")
			i = i+1

		if len(lista) == 0:
			return 0
		else:
			return 1
			

	def is_in_ubic(self, from_number):
		lista = []
		file = 'files_chat/auxilios/' + str(from_number) + '.txt'
		try:
			arch = open(file,'r')
		except:
			return 0
		i = 1
		for line in arch:
			if i == 1:
				line.replace("\n","")
				lista = line.split(";")
			i = i+1

		if len(lista) != 2:
			return 0
		else:
			return 1
		

	def is_in_ubic_espec(self, from_number):
		ubi = ''
		file = 'files_chat/auxilios/' + str(from_number) + '.txt'
		arch = open(file,'r')
		i = 1
		for line in arch:
			if i == 2:
				line.replace("\n","")
				ubi = line.strip()
			i = i+1

		if ubi == '':
			return 0
		else:
			return 1
			

	def is_in_cod_seg(self, from_number):
		cod = ''
		file = 'files_chat/auxilios/' + str(from_number) + '.txt'
		arch = open(file,'r')
		i = 1
		for line in arch:
			if i == 7:
				line.replace("\n","")
				cod = line.strip()
			i = i+1

		if cod == '':
			return 0
		else:
			return 1


	# METODO PARA REINICIAR LA CONVERSACION
	def eliminar_solicitud(self, from_number):

		# INICIO
		archivo_inicio = open('files_chat\inicio.txt', 'r')
		lines_inicio = archivo_inicio.readlines()
		archivo_inicio.close()

		archivo_inicio = open('files_chat\inicio.txt', 'w')
		for line in lines_inicio:
			if line!=str(from_number)+"\n":
				archivo_inicio.write(line)
		archivo_inicio.close()
		
		# AUXILIO Y AJUSTE
		arch_auxilios = 'files_chat/auxilios/' + str(from_number) + '.txt'
		arch_ajustes = 'files_chat/ajustes/' + str(from_number) + '.txt'
		try:
			os.remove(arch_auxilios)
			os.remove(arch_ajustes)
		except:
			pass

