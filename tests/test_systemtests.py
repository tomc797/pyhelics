# -*- coding: utf-8 -*-
import time
import helics as h

from .init import createBroker, createValueFederate, destroyFederate, destroyBroker, createMessageFederate

import os


def rm(filename, force=True):
    if os.path.exists(filename):
        os.remove("demofile.txt")


def isfile(filename):
    return os.path.exists(filename)


def test_system_test_core_creation():
    brk = h.helicsCreateBroker("inproc", "gbrokerc", "--root")

    argv = ["", "--name=gcore", "--timeout=2000", "--broker=gbrokerc"]

    cr = h.helicsCreateCoreFromArgs("inproc", "", argv)
    assert h.helicsCoreGetIdentifier(cr) == "gcore"

    argv = ["--name=gcore2", "--log-level=what_logs?"]

    # @test_throws h.HELICSErrorInvalidArgument cr2 = h.helicsCreateCoreFromArgs("inproc", "", argv)

    h.helicsBrokerDisconnect(brk)
    h.helicsCoreDisconnect(cr)

    assert h.helicsBrokerIsConnected(brk) is False


def test_system_test_broker_creation():

    argv = ["", "--name=gbrokerc", "--timeout=2000", "--root"]

    brk = h.helicsCreateBrokerFromArgs("inproc", "", argv)
    assert h.helicsBrokerGetIdentifier(brk) == "gbrokerc"

    argv[2] = "--name=gbrokerc2"
    argv[3] = "--log-level=what_logs?"

    # @test_throws h.HELICSErrorInvalidArgument brk2 = h.helicsCreateBrokerFromArgs("inproc", "", argv)

    h.helicsBrokerDisconnect(brk)


def test_system_test_broker_global_value():

    brk = h.helicsCreateBroker("inproc", "gbroker", "--root")
    globalVal = "this is a string constant that functions as a global"
    globalVal2 = "this is a second string constant that functions as a global"
    h.helicsBrokerSetGlobal(brk, "testglobal", globalVal)
    q = h.helicsCreateQuery("global", "testglobal")
    res = h.helicsQueryBrokerExecute(q, brk)
    assert res == globalVal

    h.helicsBrokerSetGlobal(brk, "testglobal2", globalVal2)
    h.helicsQueryFree(q)
    q = h.helicsCreateQuery("global", "testglobal2")
    res = h.helicsQueryBrokerExecute(q, brk)
    assert res == globalVal2

    h.helicsBrokerDisconnect(brk)
    h.helicsQueryFree(q)
    assert h.helicsBrokerIsConnected(brk) is False


def test_system_test_core_global_value():

    brk = h.helicsCreateBroker("zmq", "gbrokerc", "--root")
    cr = h.helicsCreateCore("zmq", "gcore", "--broker=gbrokerc")

    globalVal = "this is a string constant that functions as a global"
    _ = "this is a second string constant that functions as a global"

    h.helicsCoreSetGlobal(cr, "testglobal", globalVal)

    # q = h.helicsCreateQuery("global", "testglobal")
    # TODO: This hangs on core execute
    # res = h.helicsQueryCoreExecute(q, cr)
    # assert res == globalVal
    # h.helicsQueryFree(q)
    # @test_broken False

    h.helicsCoreDisconnect(cr)
    h.helicsBrokerDisconnect(brk)

    assert h.helicsBrokerIsConnected(brk) is False


def test_system_test_federate_global_value():

    brk = h.helicsCreateBroker("inproc", "gbrokerc", "--root")
    cr = h.helicsCreateCore("inproc", "gcore", "--broker=gbrokerc")

    # test creation of federateInfo from command line arguments
    argv = ["" "--corename=gcore" "--type=inproc" "--period=1.0"]

    fi = h.helicsCreateFederateInfo()
    h.helicsFederateInfoLoadFromArgs(fi, argv)

    fed = h.helicsCreateValueFederate("fed0", fi)

    argv[3] = "--period=frogs"  # this is meant to generate an error in command line processing

    fi2 = h.helicsFederateInfoClone(fi)
    # @test_throws h.HELICSErrorInvalidArgument h.helicsFederateInfoLoadFromArgs(fi2, argv)

    h.helicsFederateInfoFree(fi2)
    h.helicsFederateInfoFree(fi)

    globalVal = "this is a string constant that functions as a global"
    globalVal2 = "this is a second string constant that functions as a global"
    h.helicsFederateSetGlobal(fed, "testglobal", globalVal)
    q = h.helicsCreateQuery("global", "testglobal")
    res = h.helicsQueryExecute(q, fed)
    assert res == globalVal
    h.helicsFederateSetGlobal(fed, "testglobal2", globalVal2)
    h.helicsQueryFree(q)
    q = h.helicsCreateQuery("global", "testglobal2")
    h.helicsQueryExecuteAsync(q, fed)
    while h.helicsQueryIsCompleted(q) is False:
        time.sleep(0.20)
    res = h.helicsQueryExecuteComplete(q)
    assert res == globalVal2

    q2 = h.helicsCreateQuery("", "isinit")
    h.helicsQueryExecuteAsync(q2, fed)
    while h.helicsQueryIsCompleted(q2) is False:
        time.sleep(0.20)
    res = h.helicsQueryExecuteComplete(q2)
    assert res == "False"

    h.helicsFederateFinalize(fed)

    h.helicsCoreDisconnect(cr)
    h.helicsBrokerDisconnect(brk)

    h.helicsQueryFree(q)
    h.helicsQueryFree(q2)
    assert h.helicsBrokerIsConnected(brk) is False

    h.helicsBrokerDisconnect(brk)
    h.helicsCoreDisconnect(cr)

    assert h.helicsBrokerIsConnected(brk) is False


def test_system_tests_core_logging():
    lfile = "log.txt"
    rm(lfile, force=True)
    core = h.helicsCreateCore("inproc", "clog", "--autobroker --log_level=trace")
    h.helicsCoreSetLogFile(core, lfile)
    h.helicsCoreDisconnect(core)
    h.helicsCloseLibrary()
    assert isfile(lfile)
    rm(lfile, force=True)


def test_system_tests_broker_logging():
    lfile = "log.txt"
    rm(lfile, force=True)
    broker = h.helicsCreateBroker("inproc", "blog", "--log_level=trace")
    h.helicsBrokerSetLogFile(broker, lfile)
    h.helicsBrokerDisconnect(broker)
    h.helicsCloseLibrary()
    assert isfile(lfile)
    rm(lfile, force=True)


def test_system_tests_federate_logging():

    lfile = "log.txt"
    rm(lfile, force=True)
    core = h.helicsCreateCore("inproc", "clogf", "--autobroker --log_level=trace")

    fi = h.helicsCreateFederateInfo()
    h.helicsFederateInfoSetBrokerKey(fi, "key")
    h.helicsFederateInfoSetCoreName(fi, "clogf")
    fed = h.helicsCreateValueFederate("f1", fi)
    h.helicsFederateSetLogFile(fed, lfile)
    h.helicsFederateLogLevelMessage(fed, 7, "hello")
    h.helicsFederateLogErrorMessage(fed, "hello")
    h.helicsFederateLogDebugMessage(fed, "hello")
    h.helicsFederateLogWarningMessage(fed, "hello")
    h.helicsFederateClearMessages(fed)
    h.helicsCoreSetLogFile(core, lfile)
    h.helicsCoreDisconnect(core)
    h.helicsFederateFinalize(fed)
    h.helicsFederateInfoFree(fi)
    h.helicsCloseLibrary()

    assert isfile(lfile)
    rm(lfile, force=True)