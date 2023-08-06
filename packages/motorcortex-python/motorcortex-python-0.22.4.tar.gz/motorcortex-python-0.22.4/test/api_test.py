#!/usr/bin/python3

#
#   Developer : Alexey Zakharov (alexey.zakharov@vectioneer.com)
#   All rights reserved. Copyright (c) 2018 VECTIONEER.
#
import logging
import tempfile
import unittest
import motorcortex
import time

SERVER = 'localhost'


class DefaultMessageTypesTest(unittest.TestCase):

    def test(self):
        motorcortex_types = motorcortex.MessageTypes()
        # check if namespaces exist
        self.assertTrue(motorcortex_types.getNamespace("motorcortex"))
        motorcortex_msg = motorcortex_types.motorcortex()
        self.assertTrue(motorcortex_msg)
        # load user messages with the same module name
        msg_list = motorcortex_types.load([{'proto': './motorcortex-msg/motorcortex_pb2.py',
                                            'hash': './motorcortex-msg/motorcortex_hash.json'}])
        # check if only a single motorcortex exists
        self.assertTrue(len(msg_list) == 1)
        # check if namespaces exist
        self.assertTrue(motorcortex_types.getNamespace("motorcortex"))


class MessageTypesTest(unittest.TestCase):

    def test(self):
        motorcortex_types = motorcortex.MessageTypes()
        motorcortex_msg = motorcortex_types.motorcortex()
        motionsl_msg, = motorcortex_types.load(
            [{'proto': './motorcortex-msg/motionSL_pb2.py', 'hash': './motorcortex-msg/motionSL_hash.json'}])

        # check if namespaces exist
        self.assertTrue(motorcortex_types.getNamespace("motorcortex"))
        self.assertTrue(motorcortex_types.getNamespace("motion_spec"))

        # check if enums are loaded correctly
        self.assertTrue(hasattr(motorcortex_msg, 'OK'))
        # check if types are loaded
        self.assertTrue(hasattr(motorcortex_msg, 'ParameterMsg'))


class OpenRequestConnection(unittest.TestCase):

    def test(self):
        # Open request connection
        motorcortex_types = motorcortex.MessageTypes()
        parameter_tree = motorcortex.ParameterTree()
        req = motorcortex.Request(motorcortex_types, parameter_tree)
        if req.connect("ws://%s:5558" % SERVER).get(1000):
            print("Request connection is etablished")
        else:
            print("Failed to establish Request connection")
            self.assertTrue(False)

        req.close()


class OpenSubscribeConnection(unittest.TestCase):

    def test(self):
        # Open subscribe connection
        motorcortex_types = motorcortex.MessageTypes()
        motorcortex_msg = motorcortex_types.motorcortex()
        parameter_tree = motorcortex.ParameterTree()
        req = motorcortex.Request(motorcortex_types, parameter_tree)
        req.connect("ws://%s:5558" % SERVER)
        sub = motorcortex.Subscribe(req, motorcortex_types)
        if sub.connect("ws://%s:5557" % SERVER).get(1000):
            print("Subscribe connection is etablished")
        else:
            print("Failed to establish Subscribe connection")
            self.assertTrue(False)

        sub.close()
        req.close()


class Reconnection(unittest.TestCase):

    def stateChange(self, req, sub, state):
        print(f"obj: {req} state change: {state}")
        if state == motorcortex.ConnectionState.CONNECTION_OK:
            print("connected")
            res = req.login("root", "vectioneer").get()
            sub.resubscribe()
            print(res)
        if state == motorcortex.ConnectionState.CONNECTION_LOST:
            print("connection lost")
        if state == motorcortex.ConnectionState.DISCONNECTED:
            print(f"disconnected")

    def notify(self, x):
        print(x)

    def test(self):
        # Open subscribe connection
        # Creating empty object for parameter tree
        parameter_tree = motorcortex.ParameterTree()

        # Loading protobuf types and hashes
        motorcortex_types = motorcortex.MessageTypes()

        # Open request connection
        req, sub = motorcortex.connect("wss://127.0.0.1:5568:5567", motorcortex_types, parameter_tree,
                                       certificate="mcx.cert.crt", timeout_ms=5000,
                                       login="root", password="vectioneer")

        sub.subscribe(["root/Comm_task/actual_cycle_max"], "test", 2000).notify(lambda x: print(f"1:{x}"))
        sub.subscribe(["root/Comm_task/actual_cycle_max"], "test1", 2000).notify(lambda x: print(f"2:{x}"))
        time.sleep(10000)
        sub.close()
        req.close()


class Login(unittest.TestCase):

    def test(self):
        # Open request connection
        motorcortex_types = motorcortex.MessageTypes()
        motorcortex_msg, motionsl_msg = motorcortex_types.load(
            [{'proto': './motorcortex-msg/motorcortex_pb2.py', 'hash': './motorcortex-msg/motorcortex_hash.json'},
             {'proto': './motorcortex-msg/motionSL_pb2.py', 'hash': './motorcortex-msg/motionSL_hash.json'}])

        parameter_tree = motorcortex.ParameterTree()
        req = motorcortex.Request(motorcortex_types, parameter_tree)
        if req.connect("ws://%s:5558" % SERVER).get(1000):
            print("Request connection is etablished")
        else:
            print("Failed to establish Request connection")
            self.assertTrue(False)

        reply = req.login("operator", "operat")
        result = reply.get()
        if result.status == motorcortex_msg.OK:
            print("Login successfull")
        else:
            print("Failed to login")
            self.assertTrue(False)

        req.close()


class DecodeEncode(unittest.TestCase):

    def test(self):
        motorcortex_types = motorcortex.MessageTypes()
        motorcortex_msg = motorcortex_types.motorcortex()
        motionsl_msg, = motorcortex_types.load(
            [{'proto': './motorcortex-msg/motionSL_pb2.py', 'hash': './motorcortex-msg/motionSL_hash.json'}])

        # check if namespaces exist
        self.assertTrue(motorcortex_types.getNamespace("motorcortex"))
        self.assertTrue(motorcortex_types.getNamespace("motion_spec"))

        # check if enums are loaded correctly
        self.assertTrue(hasattr(motorcortex_msg, 'OK'))
        # check if types are loaded
        self.assertTrue(hasattr(motorcortex_msg, 'ParameterMsg'))

        login_msg = motorcortex_types.createType('motorcortex.LoginMsg')
        login_msg.login = 'operator'
        login_msg.password = 'operat'
        res = login_msg.SerializeToString()

        login_msg1 = motorcortex_types.createType('motorcortex.LoginMsg')
        login_msg1.ParseFromString(res)

        self.assertTrue(login_msg.login == login_msg1.login)
        self.assertTrue(login_msg.password == login_msg1.password)

        # param_tree_msg = motorcortex_types.createType('motorcortex.ParameterTreeMsg')
        # param_tree_msg.hash = 01245
        # param_tree_msg.status = 1
        # res = param_tree_msg.SerializeToString()
        #
        # param_tree_msg1 = motorcortex_types.createType('motorcortex.ParameterTreeMsg')
        # param_tree_msg1.ParseFromString(res)
        #
        # self.assertTrue(param_tree_msg.hash == param_tree_msg1.hash)
        # self.assertTrue(param_tree_msg.status == param_tree_msg1.status)


class ParameterTree(unittest.TestCase):

    def test(self):
        # Open request connection
        motorcortex_types = motorcortex.MessageTypes()
        motorcortex_msg, motionsl_msg = motorcortex_types.load(
            [{'proto': './motorcortex-msg/motorcortex_pb2.py', 'hash': './motorcortex-msg/motorcortex_hash.json'},
             {'proto': './motorcortex-msg/motionSL_pb2.py', 'hash': './motorcortex-msg/motionSL_hash.json'}])

        parameter_tree = motorcortex.ParameterTree()
        req = motorcortex.Request(motorcortex_types, parameter_tree)
        if req.connect("ws://%s:5558" % SERVER).get(1000):
            print("Request connection is etablished")
        else:
            print("Failed to establish Request connection")
            self.assertTrue(False)

        reply = req.login("operator", "operat")
        result = reply.get()
        if result.status == motorcortex_msg.OK:
            print("Login successfull")
        else:
            print("Failed to login")
            self.assertTrue(False)

        # Requesting a parameter tree
        reply = req.getParameterTree()
        result = reply.get()
        parameter_tree.load(result)
        if result.status == motorcortex_msg.OK:
            print("Got parameter tree")
        else:
            print("Failed to get parameter tree")
            self.assertTrue(False)

        req.close()

    def test_hash(self):

        motorcortex.logger.setLevel(logging.DEBUG)
        motorcortex_types = motorcortex.MessageTypes()
        parameter_tree = motorcortex.ParameterTree()

        # logging.basicConfig(level=logging.INFO)
        # Open request connection
        req, sub = motorcortex.connect("wss://localhost:5568:5567", motorcortex_types, parameter_tree,
                                       certificate="mcx.cert.crt", timeout_ms=1000, login="", password="")

        path = tempfile.gettempdir() + '/' + 'mcx-python-ParameterTree-hash'
        tree = req.getParameterTree().get()
        req.saveParameterTreeFile(path, tree)
        loaded_tree = req.loadParameterTreeFile(path, motorcortex_types)

        assert (tree == loaded_tree)


class SetGetParameter(unittest.TestCase):

    def test(self):
        # Open request connection
        motorcortex_types = motorcortex.MessageTypes()
        motorcortex_msg, motionsl_msg = motorcortex_types.load(
            [{'proto': './motorcortex-msg/motorcortex_pb2.py', 'hash': './motorcortex-msg/motorcortex_hash.json'},
             {'proto': './motorcortex-msg/motionSL_pb2.py', 'hash': './motorcortex-msg/motionSL_hash.json'}])

        parameter_tree = motorcortex.ParameterTree()
        req = motorcortex.Request(motorcortex_types, parameter_tree)
        if req.connect("ws://%s:5558" % SERVER).get(1000):
            print("Request connection is etablished")
        else:
            print("Failed to establish Request connection")
            self.assertTrue(False)

        reply = req.login("operator", "operat")
        result = reply.get()
        if result.status == motorcortex_msg.OK:
            print("Login successfull")
        else:
            print("Failed to login")
            self.assertTrue(False)

        # Requesting a parameter tree
        reply = req.getParameterTree()
        result = reply.get()
        parameter_tree.load(result)
        if result.status == motorcortex_msg.OK:
            print("Got parameter tree")
        else:
            print("Failed to get parameter tree")
            self.assertTrue(False)

        reply = req.getParameter('asdasd')
        msg = reply.get()
        self.assertTrue(msg.value is None)

        reply = req.getParameter('root/MyModule1/input1')
        msg = reply.get()
        value = msg.value[0]

        value = not value
        reply = req.setParameter('root/MyModule1/input1', value)
        reply.get()

        reply = req.getParameter('root/MyModule1/input1')
        msg = reply.get()
        new_value = msg.value[0]

        self.assertTrue(value == new_value)

        req.close()


class OverwriteReleaseParameter(unittest.TestCase):

    def test(self):
        # Creating empty object for parameter tree
        parameter_tree = motorcortex.ParameterTree()

        # Loading protobuf types and hashes
        motorcortex_types = motorcortex.MessageTypes()

        # Open request connection
        req, sub = motorcortex.connect("wss://127.0.0.1:5568:5567", motorcortex_types, parameter_tree,
                                       certificate="mcx.cert.crt", timeout_ms=5000,
                                       login="root", password="vectioneer")

        ## test non-existing path
        # reply = req.overwriteParameter('asdasd', True)
        # msg = reply.get()
        # self.assertTrue(msg.value is None)

        # reply = req.releaseParameter('asdasd')
        # msg = reply.get()
        # self.assertTrue(msg.value is None)

        # test with overwrite on
        test_path = 'root/Control/dummyDouble'
        value0 = 0.0

        reply = req.setParameter(test_path, value0)
        reply.get()

        value1 = 6.0
        reply = req.overwriteParameter(test_path, value1, True)
        reply.get()

        reply = req.getParameter(test_path)
        msg = reply.get()
        new_value = msg.value[0]
        self.assertTrue(new_value == value1)  # new_value == value1

        value2 = 5.0
        reply = req.setParameter(test_path, value2)
        reply.get()

        reply = req.getParameter(test_path)
        msg = reply.get()
        new_value = msg.value[0]

        self.assertTrue(new_value != value2)  # new_value != value2
        self.assertTrue(new_value == value1)  # new_value == value1

        # test after releasing overwrite
        reply = req.releaseParameter(test_path)
        reply.get()

        reply = req.setParameter(test_path, value2)
        reply.get()

        reply = req.getParameter(test_path)
        msg = reply.get()
        new_value = msg.value[0]

        print("new_value = {}".format(new_value))
        self.assertTrue(new_value == value2)  # new_value == value2

        sub.close()
        req.close()


class StreamTest(unittest.TestCase):

    def cameraVal(self, val, id):
        print(id, val[0].timestamp, len(val[0].value))

    def test(self):
        # Creating empty object for parameter tree
        parameter_tree = motorcortex.ParameterTree()

        # Loading protobuf types and hashes
        motorcortex_types = motorcortex.MessageTypes()

        # Open request connection
        req, sub = motorcortex.connect("ws://localhost:5558:5557", motorcortex_types, parameter_tree,
                                       certificate="mcx.cert.crt", timeout_ms=5000,
                                       login="", password="")

        subscription = sub.subscribe(["root/Comm_task/utilization_max",
                                      "root/Control/Camera/fameCounter"], "test", 1)
        subscription.get()
        subscription1 = sub.subscribe("root/test/varD", "camera", 1)
        subscription1.get()
        subscription.notify(lambda a: newVal(a, 0))
        subscription1.notify(lambda a: self.cameraVal(a, 1))
        time.sleep(500)

        req.close()
        sub.close()


class ConnectionTimeout(unittest.TestCase):
    def stateChange(self, req, state):
        print(f"obj: {req} state change: {state}")
        if state == motorcortex.ConnectionState.CONNECTION_OK:
            print("connected")
            res = req.login("root", "vectioneer").get()
            print(res)
        if state == motorcortex.ConnectionState.CONNECTION_LOST:
            print("connection lost")
        if state == motorcortex.ConnectionState.DISCONNECTED:
            print(f"disconnected")

    def done(self, arg1):
        print(f"Connection done: {arg1}")

    def failed(self):
        print("Connection failed")

    def test(self):
        # Creating empty object for parameter tree
        parameter_tree = motorcortex.ParameterTree()

        # Loading protobuf types and hashes
        motorcortex_types = motorcortex.MessageTypes()

        # Open request connection
        req, sub = motorcortex.connect("wss://localhost:5568:5567", motorcortex_types, parameter_tree,
                                       certificate="mcx.cert.crt", timeout_ms=5000,
                                       login="test", password="test", state_update=self.stateChange)

        while True:
            res = req.getParameter("root/Control/testB/input2")
            val = res.get()
            if val.status == motorcortex.OK:
                print(val.value)
            time.sleep(1)

        req.close()


class GetParameter(unittest.TestCase):
    def test(self):
        # Creating empty object for parameter tree
        parameter_tree = motorcortex.ParameterTree()

        # Loading protobuf types and hashes
        motorcortex_types = motorcortex.MessageTypes()

        # Open request connection
        req, sub = motorcortex.connect("wss://192.168.179.85:5568:5567", motorcortex_types, parameter_tree,
                                       certificate="mcx.cert.crt", timeout_ms=5000,
                                       login="test", password="test")

        rep = req.getParameterList(["root/Logic/mode",
                                    "root/Logic/modeCommand"]).get()
        print(f"{rep}")

        rep.close()


class SubParameter(unittest.TestCase):
    counter = 0

    def newValue(self, value):
        self.counter = self.counter + 1

    def test(self):
        # Open request connection
        motorcortex_types = motorcortex.MessageTypes()
        motorcortex_msg, motionsl_msg = motorcortex_types.load(
            [{'proto': './motorcortex-msg/motorcortex_pb2.py', 'hash': './motorcortex-msg/motorcortex_hash.json'},
             {'proto': './motorcortex-msg/motionSL_pb2.py', 'hash': './motorcortex-msg/motionSL_hash.json'}])

        parameter_tree = motorcortex.ParameterTree()
        req = motorcortex.Request(motorcortex_types, parameter_tree)
        if req.connect("wss://%s:5568" % SERVER, certificate="mcx.cert.crt").get(5000):
            print("Request connection is etablished")
        else:
            print("Failed to establish Request connection")
            self.assertTrue(False)

        reply = req.login("operator", "operat")
        result = reply.get()
        if result.status == motorcortex_msg.OK:
            print("Login successfull")
        else:
            print("Failed to login")
            self.assertTrue(False)

        # Requesting a parameter tree
        reply = req.getParameterTree()
        result = reply.get()
        parameter_tree.load(result)
        if result.status == motorcortex_msg.OK:
            print("Got parameter tree")
        else:
            print("Failed to get parameter tree")
            self.assertTrue(False)

        sub = motorcortex.Subscribe(req, motorcortex_types)
        if sub.connect("wss://%s:5567" % SERVER, certificate="mcx.cert.crt").get(1000):
            print("Subscribe connection is etablished")
        else:
            print("Failed to establish Subscribe connection")
            self.assertTrue(False)

        subscription = sub.subscribe(['fsdf'], 'group1', 100)
        self.assertTrue(subscription.get() is None)

        subscription = sub.subscribe(['root/Control/dummyDouble'], 'group1', 100)
        self.assertTrue(subscription.get())

        subscription.notify(self.newValue)
        timestamp = 0
        for x in range(400):
            print(f"timestamp: {subscription.read()[0].timestamp}, value: {subscription.read()[0].value}")
            time.sleep(1)

        self.assertTrue(sub.unsubscribe(subscription).get().status == motorcortex.OK)

        self.assertTrue(self.counter > 0)
        self.assertTrue(timestamp.sec > 0)

        sub.close()
        req.close()


class SetString(unittest.TestCase):
    def test(self):
        parameter_tree = motorcortex.ParameterTree()
        # Open request and subscribe connection
        req, sub = motorcortex.connect("wss://localhost:5568:5567", motorcortex.MessageTypes(), parameter_tree,
                                       certificate="mcx.cert.crt", timeout_ms=1000,
                                       login="root", password="secret")
        res = req.setParameter("root/Control/dummyChar", "Hallo robot!")
        res.get()


class SetParameterWithOffset(unittest.TestCase):
    def test(self):
        parameter_tree = motorcortex.ParameterTree()
        # Open request and subscribe connection
        req, sub = motorcortex.connect("wss://localhost:5568:5567", motorcortex.MessageTypes(), parameter_tree,
                                       certificate="mcx.cert.crt", timeout_ms=1000,
                                       login="root", password="secret")
        res = req.setParameter("root/Control/hostInJointTrajectory", [6, 5])
        res.get()


if __name__ == '__main__':
    unittest.main()
