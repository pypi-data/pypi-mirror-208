
import unittest
import time
import asyncio
from src.neuko.utility.logger import Logger
from src.neuko.device.telemetricState import TelemetricState

logger = Logger("TelemetricStateTest").set()

class TelemetricStateTest(unittest.TestCase):

    def setUp(self):
        logger.debug("Test Start")
        self.outsideFlag = False
        self.asyncloop = asyncio.new_event_loop()

    def test_01_flattening_json_object(self):
        object = {
            'a': 1,
            'b': {
                'a': 1,
                'b': [
                    {
                        'a': 1,
                        'b': {
                            'a': 1,
                            'g': {
                                'v': True
                            }
                        }
                    },
                    {
                        'a': 2,
                        'b': {
                            'a': 2
                        }
                    }
                ]
            },
            'c': [
                {
                    'a': 1,
                    'b': {
                        'a': 1
                    }
                },
                {
                    'a': 2,
                    'b': {
                        'a': 2
                    }
                }
            ]
        }
        flatted = TelemetricState.flattening(object)
        logger.debug(flatted)
        with self.subTest():
            self.assertEqual(flatted['a'], object['a'])
        with self.subTest():
            self.assertEqual(flatted['b.a'], object['b']['a'])
        with self.subTest():
            self.assertEqual(len(flatted['b.b']), 2)
        with self.subTest():
            self.assertEqual(flatted['b.b'][0], object['b']['b'][0])
        with self.subTest():
            self.assertEqual(flatted['b.b'][1], object['b']['b'][1])
        with self.subTest():
            self.assertEqual(len(flatted['c']), 2)
        with self.subTest():
            self.assertEqual(flatted['c'][0], object['c'][0])
        with self.subTest():
            self.assertEqual(flatted['c'][1], object['c'][1])

    def test_02_existed_statename(self):
        state = TelemetricState()
        state._createNewState('state_a')
        self.assertTrue(state._isStateExists('state_a'))

    def test_03_non_existance_statename(self):
        state = TelemetricState()
        state._createNewState('state_a')
        self.assertFalse(state._isStateExists('state_b'))

    def test_04_report_new_state_value(self):
        state = TelemetricState()
        state.report('state_a', 'att.deep', True, int(time.time()))
        with self.subTest():
            self.assertEqual(state.states['desired']['state_a'], {})
        with self.subTest():
            self.assertEqual(state.states['reported']['state_a']['att']['deep'], True)
        with self.subTest():
            self.assertEqual(state.states['delta']['state_a'], {})

    def test_05_report_updated_state_value(self):
        state = TelemetricState()
        state.report('state_a', 'att.deep', True, int(time.time()))
        self.asyncloop.run_until_complete(asyncio.sleep(1))
        state.report('state_a', 'att.deep', False, int(time.time()))
        with self.subTest():
            self.assertEqual(state.states['desired']['state_a'], {})
        with self.subTest():
            self.assertEqual(state.states['reported']['state_a']['att']['deep'], False)
        with self.subTest():
            self.assertEqual(state.states['delta']['state_a'], {})

    def test_06_desired_state_value(self):
        state = TelemetricState()
        state.desire('state_a', 'att.deep', True, int(time.time()))
        with self.subTest():
            self.assertEqual(state.states['reported']['state_a'], {})
        with self.subTest():
            self.assertEqual(state.states['desired']['state_a']['att']['deep'], True)
        with self.subTest():
            self.assertEqual(state.states['delta']['state_a'], {})

    def test_07_desired_and_get_pending(self):
        state = TelemetricState()
        state.desire('state_a', 'att.deep', True, int(time.time()))
        state.desire('state_a', 'att.deep2', 123, int(time.time()))
        firstPending = state.getPendingDesire('state_a')
        with self.subTest():
            self.assertEqual(firstPending['attributeTree'], 'att.deep')
        with self.subTest():
            self.assertEqual(firstPending['value'], True)
        with self.subTest():
            self.assertEqual(state.getPendingDesire('state_a')['attributeTree'], 'att.deep')

    def test_08_desired_and_get_pending_and_report(self):
        state = TelemetricState()
        state.desire('state_a', 'att.deep', True, int(time.time()))
        state.desire('state_a', 'att.deep2', 123, int(time.time()))
        firstPending = state.getPendingDesire('state_a')
        with self.subTest():
            self.assertEqual(firstPending['attributeTree'], 'att.deep')
        with self.subTest():
            self.assertEqual(firstPending['value'], True)
        with self.subTest():
            state.report('state_a', firstPending['attributeTree'], True, int(time.time()))
            self.assertEqual(state.getPendingDesire('state_a')['attributeTree'], 'att.deep2')

    def test_09_report_and_snapshot(self):
        state = TelemetricState()
        state.report('state_a', 'att.deep', True, int(time.time()))
        self.asyncloop.run_until_complete(asyncio.sleep(1))
        state.report('state_a', 'att.deep', False, int(time.time()))
        self.asyncloop.run_until_complete(asyncio.sleep(1))
        state.report('state_a', 'att.deep2', 123, int(time.time()))
        snapshot = state.snapshot('state_a')
        logger.debug(snapshot)
        with self.subTest():
            self.assertEqual(snapshot['state']['reported']['att']['deep'], False)
        with self.subTest():
            self.assertEqual(snapshot['state']['reported']['att']['deep2'], 123)

    def test_10_report_and_snapshot_attribute_only(self):
        state = TelemetricState()
        state.report('state_a', 'att.deep', True, int(time.time()))
        self.asyncloop.run_until_complete(asyncio.sleep(1))
        state.report('state_a', 'att.deep', False, int(time.time()))
        self.asyncloop.run_until_complete(asyncio.sleep(1))
        state.report('state_a', 'att.deep2', 123, int(time.time()))
        snapshot = state.snapshot('state_a', True)
        logger.debug(snapshot)
        with self.subTest():
            self.assertEqual(snapshot['att']['deep'], False)
        with self.subTest():
            self.assertEqual(snapshot['att']['deep2'], 123)

    # REPEAT SAME TEST BUT NOW FOR ARRAY USE CASE
    
    def test_11_report_new_state_array_value(self):
        state = TelemetricState()
        value = [
            {
                "down": 123,
                "upward": {
                    "downward": True
                }
            },
            {
                "down": 456,
                "upward": {
                    "downward": True
                }
            }
        ]
        state.report('state_a', 'att.deep', value, int(time.time()))
        with self.subTest():
            self.assertEqual(type(state.states['reported']['state_a']['att']['deep']) is list, True)
        with self.subTest():
            self.assertEqual(len(state.states['reported']['state_a']['att']['deep']), 2)
        with self.subTest():
            self.assertEqual(state.states['reported']['state_a']['att']['deep'][0], value[0])
        with self.subTest():
            self.assertEqual(state.states['reported']['state_a']['att']['deep'][1], value[1])
        with self.subTest():
            self.assertEqual(state.states['desired']['state_a'], {})
        with self.subTest():
            self.assertEqual(state.states['delta']['state_a'], {})

    def test_12_report_updated_state_value_of_array(self):
        state = TelemetricState()
        value = [
            {
                "down": 123,
                "upward": {
                    "downward": True
                }
            },
            {
                "down": 456,
                "upward": {
                    "downward": True
                }
            }
        ]
        state.report('state_a', 'att.deep', value, int(time.time()))
        value[1]["upward"]["downward"] = False
        state.report('state_a', 'att.deep[1]', value, int(time.time()))
        with self.subTest():
            self.assertEqual(type(state.states['reported']['state_a']['att']['deep']) is list, True)
        with self.subTest():
            self.assertEqual(len(state.states['reported']['state_a']['att']['deep']), 2)
        with self.subTest():
            self.assertEqual(state.states['reported']['state_a']['att']['deep'][0], value[0])
        with self.subTest():
            self.assertEqual(state.states['reported']['state_a']['att']['deep'][1], value[1])
        with self.subTest():
            self.assertEqual(state.states['delta']['state_a'], {})

    def test_13_desired_state_value_array(self):
        state = TelemetricState()
        value = [
            {
                "down": 123,
                "upward": {
                    "downward": True
                }
            },
            {
                "down": 456,
                "upward": {
                    "downward": True
                }
            }
        ]
        state.desire('state_a', 'att.deep', value, int(time.time()))
        with self.subTest():
            self.assertEqual(type(state.states['desired']['state_a']['att']['deep']) is list, True)
        with self.subTest():
            self.assertEqual(len(state.states['desired']['state_a']['att']['deep']), 2)
        with self.subTest():
            self.assertEqual(state.states['desired']['state_a']['att']['deep'][0], value[0])
        with self.subTest():
            self.assertEqual(state.states['desired']['state_a']['att']['deep'][1], value[1])
        with self.subTest():
            self.assertEqual(state.states['reported']['state_a'], {})
        with self.subTest():
            self.assertEqual(state.states['delta']['state_a'], {})

    def test_14_desired_array_and_get_pending(self):
        state = TelemetricState()
        value = [
            {
                "down": 123,
                "upward": {
                    "downward": True
                }
            },
            {
                "down": 456,
                "upward": {
                    "downward": True
                }
            }
        ]
        state.desire('state_a', 'att.deep', value, int(time.time()))
        firstPending = state.getPendingDesire('state_a')
        with self.subTest():
            self.assertEqual(firstPending['attributeTree'], 'att.deep')
        with self.subTest():
            self.assertEqual(type(firstPending['value']) is list, True)
        with self.subTest():
            self.assertEqual(firstPending['value'], value)
        with self.subTest():
            self.assertEqual(state.getPendingDesire('state_a')['attributeTree'], 'att.deep')


    def test_15_array_report_desire_and_get_pending(self):
        state = TelemetricState()
        value = [
            {
                "down": 123,
                "upward": {
                    "downward": True
                }
            },
            {
                "down": 456,
                "upward": {
                    "downward": True
                }
            }
        ]
        newvalue = [
            {
                "down": 123,
                "upward": {
                    "downward": True
                }
            },
            {
                "down": 456,
                "upward": {
                    "downward": False
                }
            }
        ]
        state.report('state_a', 'att.deep', value, int(time.time()))
        state.desire('state_a', 'att.deep', newvalue, int(time.time()))
        # to test reported state
        with self.subTest():
            self.assertEqual(type(state.states['reported']['state_a']['att']['deep']) is list, True)
        with self.subTest():
            self.assertEqual(len(state.states['reported']['state_a']['att']['deep']), 2)
        with self.subTest():
            self.assertEqual(state.states['reported']['state_a']['att']['deep'][0], value[0])
        with self.subTest():
            self.assertEqual(state.states['reported']['state_a']['att']['deep'][1], value[1])

        self.asyncloop.run_until_complete(asyncio.sleep(1))
        firstPending = state.getPendingDesire('state_a')
        with self.subTest():
            self.assertEqual(firstPending['attributeTree'], 'att.deep')
        with self.subTest():
            self.assertEqual(type(firstPending['value']) is list, True)
        with self.subTest():
            self.assertEqual(firstPending['value'], newvalue)
        with self.subTest():
            self.assertEqual(state.getPendingDesire('state_a')['attributeTree'], 'att.deep')

        self.asyncloop.run_until_complete(asyncio.sleep(1))
        state.report('state_a', 'att.deep', firstPending["value"], int(time.time()))
        with self.subTest():
            self.assertEqual(type(state.states['reported']['state_a']['att']['deep']) is list, True)
        with self.subTest():
            self.assertEqual(len(state.states['reported']['state_a']['att']['deep']), 2)
        with self.subTest():
            self.assertEqual(state.states['reported']['state_a']['att']['deep'][0], newvalue[0])
        with self.subTest():
            self.assertEqual(state.states['reported']['state_a']['att']['deep'][1], newvalue[1])