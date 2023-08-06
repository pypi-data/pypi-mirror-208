from pickle import TRUE
import unittest
import asyncio
from src.neuko.utility.logger import Logger
from src.neuko.device.model import DeviceIdentifier, TelemetricStateChangeParameter
from src.neuko.device.telemetricWorker import TelemetricWorker

logger = Logger("TelemetricWorkerTest").set()

class TelemetricWorkerTest(unittest.TestCase):

    def setUp(self):
        self.asyncloop = asyncio.new_event_loop()
        self.addCleanup(self.asyncloop.close)

    def test_01_add_wildcard(self):
        deviceId = DeviceIdentifier("acc_i8Ga2RzmtQ8X", "prj_vH5VmqBjWYJU", "sch_V5HoA4ZtuwCQ", "SP0002")
        worker = TelemetricWorker()

        worker.add(self, deviceId, 'state_test', '*')
        self.assertEquals(len(worker._TelemetricWorker__workers), 1)

    def test_02_add_sync_wildcard_and_execute(self):
        deviceId = DeviceIdentifier("acc_i8Ga2RzmtQ8X", "prj_vH5VmqBjWYJU", "sch_V5HoA4ZtuwCQ", "SP0002")
        worker = TelemetricWorker()
        def callback(value: TelemetricStateChangeParameter):
            logger.debug(f'callback: {value}')
            return True

        worker.add(self, deviceId, 'state_test', '*', callback)
        res = self.asyncloop.run_until_complete(worker.execute(deviceId, 'state_test', 'att.att2', True))
        self.assertTrue(res)

    def test_03_add_async_wildcard_and_execute(self):
        deviceId = DeviceIdentifier("acc_i8Ga2RzmtQ8X", "prj_vH5VmqBjWYJU", "sch_V5HoA4ZtuwCQ", "SP0002")
        worker = TelemetricWorker()
        async def callback(value: TelemetricStateChangeParameter):
            logger.debug(f'callback: {value}')
            return True

        worker.add(self, deviceId, 'state_test', '*', callback)
        res = self.asyncloop.run_until_complete(worker.execute(deviceId, 'state_test', 'att.att2', True))
        self.assertTrue(res)

    def test_04_add_wildcard_and_execute_to_expect_failure(self):
        deviceId = DeviceIdentifier("acc_i8Ga2RzmtQ8X", "prj_vH5VmqBjWYJU", "sch_V5HoA4ZtuwCQ", "SP0002")
        worker = TelemetricWorker()
        async def callback(value: TelemetricStateChangeParameter):
            logger.debug(f'callback: {value}')
            return False

        worker.add(self, deviceId, 'state_test', '*', callback)
        res = self.asyncloop.run_until_complete(worker.execute(deviceId, 'state_test', 'att.att2', True))
        self.assertFalse(res)

    def test_05_add_callback_and_execute(self):
        deviceId = DeviceIdentifier("acc_i8Ga2RzmtQ8X", "prj_vH5VmqBjWYJU", "sch_V5HoA4ZtuwCQ", "SP0002")
        worker = TelemetricWorker()
        async def callback(value: TelemetricStateChangeParameter):
            logger.debug(f'callback: {value}')
            return True

        worker.add(self, deviceId, 'state_test', 'att.att2', callback)
        res = self.asyncloop.run_until_complete(worker.execute(deviceId, 'state_test', 'att.att2', True))
        self.assertTrue(res)

    def test_06_add_callback_and_execute_tp_expect_failure(self):
        deviceId = DeviceIdentifier("acc_i8Ga2RzmtQ8X", "prj_vH5VmqBjWYJU", "sch_V5HoA4ZtuwCQ", "SP0002")
        worker = TelemetricWorker()
        async def callback(value: TelemetricStateChangeParameter):
            logger.debug(f'callback: {value}')
            return False

        worker.add(self, deviceId, 'state_test', 'att.att2', callback)
        res = self.asyncloop.run_until_complete(worker.execute(deviceId, 'state_test', 'att.att2', True))
        self.assertFalse(res)

    def test_07_add_callback_and_execute_different_statename(self):
        deviceId = DeviceIdentifier("acc_i8Ga2RzmtQ8X", "prj_vH5VmqBjWYJU", "sch_V5HoA4ZtuwCQ", "SP0002")
        worker = TelemetricWorker()
        async def callback(value: TelemetricStateChangeParameter):
            logger.debug(f'callback: {value}')
            return True

        worker.add(self, deviceId, 'state_test', 'att.att2', callback)
        res = self.asyncloop.run_until_complete(worker.execute(deviceId, 'state_no', 'att.att2', True))
        self.assertTrue(res)

