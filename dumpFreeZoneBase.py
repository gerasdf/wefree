import sqlite3
from base64 import decodestring
import sys

def decode(encripted_and_base64):
    encripted = decodestring(encripted_and_base64)
    answer = ''
    l = len(encripted)
    key = encripted[:3]
    for j in range(3,len(encripted)):
        answer += chr(ord(encripted[j]) ^ ord(key[(j-3) % 3]))
    return answer

def main():
    db = sqlite3.connect(sys.argv[1])

    #events = dict()
    #orwell_events = db.execute("pragma table_info('orwell_event')")
    #for data, date, wifi_type, lon, lat, event_id, _id in orwell_events:
        

    for bssid, key in db.execute('select * from hotspot'):
        print bssid, decode(key)

def test():
    print 'tinoycata' == decode('GgwBbmVvdXVie3hg')
    print 'jp01234567890' == decode('Cg4WYH4mOzwlPjsgPTYvOg==')

if __name__ == '__main__':
    test()
    main()
