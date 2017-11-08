from threading import Timer
from time import sleep



timerOn = False

def p():
	print 'Hello'
	global timerOn
	timerOn = False

while 1:
	if not timerOn:
		timerOn = True
		t = Timer(10.0, p)
		t.start()

	print 'World'
	sleep(5.0)
