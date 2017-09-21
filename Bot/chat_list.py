
class list_interactions():
    
	def __init__(self):
		# LISTA CON NUMEROS QUE PASARON POR EL 1ER ESTADO
		self.inicio = []
		archivo_inicio = open('files_chat\inicio.txt', 'r')
		for line in archivo_inicio:
			self.inicio.append(int(line))

		# LISTA CON NUMEROS QUE PASARON POR EL 2DO ESTADO
		self.motivo = []
		archivo_motivo = open('files_chat\motivo.txt', 'r')
		for line in archivo_motivo:
			self.motivo.append(int(line))

		# LISTA CON NUMEROS QUE PASARON POR EL 3ER ESTADO
		self.motivo_rta = []
		archivo_motivo_rta = open('files_chat\motivo_rta.txt', 'r')
		for line in archivo_motivo_rta:
			self.motivo_rta.append(int(line))


	def add_new_interaction(self, from_number, interaccion):
		if interaccion == "Saludo":
			self.inicio.append(int(from_number)) 
			archivo_inicio = open('files_chat\inicio.txt', 'a')
			archivo_inicio.write("%s\n" % str(from_number))

		if interaccion == "Motivo":
			self.motivo.append(int(from_number)) 
			archivo_motivo = open('files_chat\motivo.txt', 'a')
			archivo_motivo.write("%s\n" % str(from_number))

		if interaccion == "Motivo Respuesta":
			self.motivo_rta.append(int(from_number)) 
			archivo_motivo_rta = open('files_chat\motivo_rta.txt', 'a')
			archivo_motivo_rta.write("%s\n" % str(from_number))


	def add_ubicacion(self, from_number, latitud, longitud):
		linea = str(latitud) + ';' + str(longitud)
		arch = 'files_chat/auxilios/' + str(from_number) + '.txt'
		archivo_inicio = open(arch, 'w+')
		archivo_inicio.write("%s\n" % linea)

	
	def add_sintomas(self, from_number, sintomas):
		linea = str(sintomas)
		arch = 'files_chat/auxilios/' + str(from_number) + '.txt'
		archivo_inicio = open(arch, 'a')
		archivo_inicio.write("%s\n" % linea)


	def add_sintomas_rta(self, from_number, sintomas):
		linea = str(sintomas)
		arch = 'files_chat/auxilios/' + str(from_number) + '.txt'
		archivo_inicio = open(arch, 'a')
		archivo_inicio.write("%s\n" % linea)

	
	def get_data_inicio(self):
		return self.inicio


	def get_sintomas(self, from_number):
		lista = []
		file = 'files_chat/auxilios/' + str(from_number) + '.txt'
		arch = open(file,'r')
		i= 1
		for line in arch:
			if i == 2:
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

	
	def is_in_motivo(self, from_number):
		if from_number not in self.motivo:
			return 0
		else:
			return 1

	
	def is_in_motivo_rta(self, from_number):
		if from_number not in self.motivo_rta:
			return 0
		else:
			return 1


	def is_in_sintona_rta(self, from_number):
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