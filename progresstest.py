from progressbar import ProgressBar
import time
a = 60
p = ProgressBar(a)
status = 0
while status < a:
	time.sleep(2)
	status+=10
	p.update(status)


