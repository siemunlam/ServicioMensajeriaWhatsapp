from yowsup.stacks import  YowStackBuilder
from layer import EchoLayer
from yowsup.layers.auth import AuthError
from yowsup.layers import YowLayerEvent
from yowsup.layers.network import YowNetworkLayer

credentials = ("5491166036790", "EEu6kzGfv9x0adOjYWai0A+NF/E=") # replace with your phone and password

if __name__==  "__main__":
	print("")
	print(" *************************************************************")
	print(" Agente Virtual SIEM (Sistema Integral de Emergencias Médicas)")
	print(" *************************************************************")
	print("")
	print(" Escuchando solicitudes...")

	stackBuilder = YowStackBuilder()

	stack = stackBuilder\
		.pushDefaultLayers(True)\
		.push(EchoLayer)\
		.build()

	stack.setCredentials(credentials)	
	stack.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))
	try:
		stack.loop()
	except AuthError as e:
		print("Authentication Error: %s" % e.message)
