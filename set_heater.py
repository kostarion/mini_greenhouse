import sys
import shelve

session = shelve.open('greenhouse_connection', flag='r')
try:
    greenhouse = session['key']
    mode = int(sys.argv[1]) # 0 or 1
    result = greenhouse.set_heater_mode(mode)
finally:
    s.close()

print(result)
