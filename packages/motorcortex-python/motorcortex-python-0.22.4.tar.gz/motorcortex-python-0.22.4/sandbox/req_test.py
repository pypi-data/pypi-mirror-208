#!/usr/bin/python3

import motorcortex

if __name__ == '__main__':
    parameter_tree = motorcortex.ParameterTree()
    motorcortex_types = motorcortex.MessageTypes()

    # Vectioneer camera
    endpoint_1 = "ws://motorcortex:5558:5557"
    req, sub = motorcortex.connect(endpoint_1, motorcortex_types, parameter_tree,
                                   certificate="mcx.cert.crt", timeout_ms=1000,
                                   login="", password="")


    # Local processing
    endpoint_2 = "wss://localhost:5568:5567"
    req1, sub1 = motorcortex.connect(endpoint_2, motorcortex.MessageTypes(), motorcortex.ParameterTree(),
                                   certificate="mcx.cert.crt", timeout_ms=1000,
                                   login="", password="")

    print("Sending data from {} to {}".format(endpoint_1, endpoint_2))

    counter = 0
    while True:
        ss = req.getParameter("root/Camera/image")
        res = ss.get()
        print("{}: {}".format(counter, len(res.value)))
        handle = req1.setParameter("root/Processing/image", res.value)
        res = handle.get()
        counter = counter + 1

