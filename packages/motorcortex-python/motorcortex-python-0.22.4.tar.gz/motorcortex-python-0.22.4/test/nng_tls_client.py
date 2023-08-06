#!/usr/bin/python3

from pynng import Sub0, TLSConfig
import threading
import time


def test(identifier, url, crt):
    print("open connection id: {}".format(identifier))
    tls_config = TLSConfig(TLSConfig.MODE_CLIENT, ca_files=crt)
    socket = Sub0(recv_timeout=1000000, tls_config=tls_config)
    socket.dial(url)
    socket.subscribe('')

    for i in range(1000):
        socket.recv()

    socket.close()

    print("close connection id: {}".format(identifier))


if __name__ == '__main__':
    # creating thread

    threads = []
    for i in range(50):
        threads.append(threading.Thread(target=test, args=(i, 'wss://localhost:5555', 'mcx.cert.crt')))
        threads[-1].start()
        time.sleep(0.01)

    for t in threads:
        t.join()
