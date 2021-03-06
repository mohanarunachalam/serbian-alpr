#!/usr/bin/env python

###############################################################################
# Fajl startuje car-in sistem sa predefinisanim brojem kamera koje ucestvuju. #
###############################################################################

import ConfigParser
import multiprocessing
import time

from carinaLibs import IPStream


config = ConfigParser.ConfigParser()
config.read(".carinaConfig.ini")
sections = config.sections()
threads = []

items = [
    'name',
    'ip',
    'protocol',
    'username',
    'passwd',
    'vendor',
    'resolution',
    'rotation',
    'roi',
    'detectregion',
    'fps',
    'sensitivity']

for camera in sections:
    if camera.startswith('Camera'):
        params = {}
        for key in items:
            try:
                params[key] = config.get(camera, key)
            except:
                params[key] = None

        if params['roi']:
            r = params['roi'].split(",")
            params['roi'] = [a for a in r if a] if len(r) > 2 else None

        if params['detectregion']:
            dr = params['detectregion'].split(",")
            params['detectregion'] = [
                a for a in dr if a] if len(dr) > 2 else None
        params['image_location'] = config.get('storage', 'image')
        params['thumbnail_location'] = config.get('storage', 'thumbnail')

        # print params
        st = IPStream.IPStream(params)

        p = multiprocessing.Process(target=st.start)
        p.start()
        threads.append([p, params, True])

reseter = 0
while True:
    if reseter > 200:
        reseter = 0
        print "Vreme da menjamo tredove"
        try:
            for t in threads:
                t[0].terminate()
                t[0].join()
                st = IPStream.IPStream(t[1])

                p = multiprocessing.Process(target=st.start)
                t[2] = False
                p.start()
                threads.append(
                    [p, t[1], True])
                print p
                time.sleep(2)

                threads = [t for t in threads if t[2]]
            time.sleep(2)
        except Exception as e:
            print e
            exit(0)
    else:
        # print "Ovde sam"
        try:
            for t in threads:
                if not t[0].is_alive():
                    print "Greska u tredu, menjamo ga."
                    t[0].terminate()
                    t[0].join()
                    st = IPStream.IPStream(t[1])

                    p = multiprocessing.Process(target=st.start)
                    t[2] = False
                    p.start()
                    threads.append(
                        [p, t[1], True])

            threads = [t for t in threads if t[2]]
            reseter += 1
            time.sleep(10)
        except Exception as e:
            print e
            continue

print "Izlazim iz glavne petlje"
