class Message():

	def __init__(self):

		self.pregunta_estado_persona = ['como andas?', 'que tal?', 'todo bien?']
		self.saludo = ['hola', 'buenas', 'buen dia', 'buenas tardes', 'buenas noches']
		self.saludo_respuesta = "Hola, como estas?"

	def GetSaludos(self):
		return self.saludo

	def GetSaludoRespuesta(self):
		return self.saludo_respuesta
