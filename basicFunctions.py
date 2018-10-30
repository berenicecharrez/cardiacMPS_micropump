from time import sleep

try:
	import RPi.GPIO as GPIO
	valves = [4,17,27,22,10,9,11,5,6,13,19,26,21,20,16,12,14,15,18,23,24,25,8]
	GPIO.setmode(GPIO.BCM)
	for x in valves:
	    GPIO.setup(x, GPIO.OUT)
	    GPIO.output(x, 0)
except:
	pass

def set_gpio_output(valve, state):
	try:
		GPIO.output(valve, state)
	except:
		pass#print('cant access GPIO')


def degasing(lock, valve = 5):
	print('degasing started')

	while lock.locked():
		set_gpio_output(valve, 0)

	print('degasing stopped')

def openValves(valve):
	#valves = [4,17,27,22,10,9,11,5,6,13,19,26,21,20,16,12,14,15,18,23,24,25,8]
	print('Valve is opening: {}'.format(valve))
	set_gpio_output(valve, 0)

def closeValves(valve):
	print('valve is closing')

	set_gpio_output(valve, 1)

def pumping(stepTime, lock):

	print('entering pumping valve')
	p1 = 10
	p2 = 9
	p3 = 11

	while lock.locked():
		#pass

		set_gpio_output(p1, 0)
		set_gpio_output(p3, 1)
		sleep(stepTime)
		set_gpio_output(p2, 0)
		sleep(stepTime)
		set_gpio_output(p1, 1)
		set_gpio_output(p3, 0)
		sleep(stepTime)
		set_gpio_output(p2, 1)
		sleep(stepTime)

	print('pumping finished')


def valveMappingNumbers():
	global v1, v2, v3, v4, v5, v6, v7, v8, v9, v10, v11, v12
	global v13, v14, v15, v16, v17, v18, v19, v20 , v21, v22, v23
	v1 = 4 #inlet 1
	v2 = 17 #inlet 2
	v3 = 27 #inlet 3
	v4 = 22 #inlet 4
	v5 = 10 #pump 1
	v6 = 9 #pump 2
	v7 = 11 #pump 3
	v8 = 5 #degasser
	v9 = 6 #outlet 1
	v10 = 13 #outlet 2
	v11 = 19 #outlet 3
	v12 = 26
	v13 = 21
	v14 = 20
	v15 = 16
	v16 = 12 #outlet 4
	v17 = 14 #outlet 5
	v18 = 15 #outlet 6
	v19 = 18 #outlet 7
	v20 = 23 #outlet 8
	v21 = 24
	v22 = 25
	v23 = 8

def valveMappingNames():
	global i1, i2, i3, i4
	global deg
	global o1, o2, o3, o4, o5, o6, o7, o8
	i1 = 4  #inlet 1
	i2 = 17 #inlet 2
	i3 = 27 #inlet 3
	i4 = 22 #inlet 4
	p1 = 10 #pump 1
	p2 = 9  #pump 2
	p3 = 11 #pump 3
	deg = 5 #degasser
	o1 = 6  #outlet 1
	o2 = 13 #outlet 2
	o3 = 19 #outlet 3
	o4 = 12 #outlet 4
	o5 = 14 #outlet 5
	o6 = 15 #outlet 6
	o7 = 18 #outlet 7
	o8 = 23 #outlet 8
