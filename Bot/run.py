from yowsup.stacks import  YowStackBuilder
from layer import EchoLayer
from yowsup.layers.auth import AuthError
from yowsup.layers import YowLayerEvent
from yowsup.layers.network import YowNetworkLayer
#from yowsup.demos.cli.layer import YowsupCliLayer

credentials = ("5491166036790", "EEu6kzGfv9x0adOjYWai0A+NF/E=") # replace with your phone and password
#credentials = ("5491168128304", "ahcSVXF7xcKL3cYEHITXEqhoWzQ=") # replace with your phone and password

if __name__==  "__main__":
	print("")
	print("*************************************************************")
	print("Agente Virtual SIEM (Sistema Integral de Emergencias Médicas)")
	print("*************************************************************")
	print("")
	print("Escuchando solicitudes...")

	stackBuilder = YowStackBuilder()

	stack = stackBuilder\
		.pushDefaultLayers(True)\
		.push(EchoLayer)\
		.build()

	stack.setCredentials(credentials)
	# stack.profile_setPicture("profile_pic/SIEM_Icono_3.png")
	# stack.profile_setStatus("SIEM")
	stack.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))

	try:
		stack.loop()
		# while 1 == 1:
		# 	try:
		# 		stack.loop()
		# 	except:
		# 		print("Formato no reconocido")
	except AuthError as e:
		print("Authentication Error: %s" % e.message)
