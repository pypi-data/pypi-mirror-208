#!/usr/bin/python3

#
#   Developer : Alexey Zakharov (alexey.zakharov@vectioneer.com)
#   All rights reserved. Copyright (c) 2017-2020 VECTIONEER.
#

import motorcortex
import time
import threading
import logging


def onLog(val):
    print(val[0].value)


def onVar(val):
    print(val[0].value)


def main(id):
    logging.basicConfig(level=logging.DEBUG)

    # Creating empty object for parameter tree
    parameter_tree = motorcortex.ParameterTree()

    # Loading protobuf types and hashes
    motorcortex_types = motorcortex.MessageTypes()

    # Open request connection
    req, sub = motorcortex.connect("wss://192.168.2.100:5568:5567", motorcortex_types, parameter_tree,
                                   certificate="mcx.cert.crt", timeout_ms=1000,
                                   login="", password="")

    start = time.time()
    for x in range(1000):
        # req.setParameter("root/Control/dummyBool", True)
        req.setParameter("root/Control/dummyDouble", x)
        r = req.getParameter("root/Control/dummyDouble")
        # print(r.get())
    end = time.time()

    print("total time: {}".format(end - start))

    # time.sleep(15)

    req.close()
    sub.close()


if __name__ == '__main__':
    # creating thread
    t1 = threading.Thread(target=main, args=(1,))
    t1.start()
    t1.join()
