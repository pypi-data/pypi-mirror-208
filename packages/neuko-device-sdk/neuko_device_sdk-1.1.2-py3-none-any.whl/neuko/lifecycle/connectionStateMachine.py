import asyncio
from transitions.extensions.asyncio import AsyncMachine
from ..device.model import DeviceIdentifier
from ..device.telemetricWorker import TelemetricWorker
from ..utility.logger import Logger

logger = Logger("ConnectionStateMachine").set()

# const
class ConnectionStateNachineLifecycle:

    POWER_ON                = 'power_on'
    TEST_INTERNET           = 'test_internet'
    INTERNET_CONNECTED      = 'internet_connected'
    FOUND_SAVED_SETTINGS    = 'found_saved_settings'
    NO_SAVED_SETTINGS       = 'no_saved_settings'
    BOOTSTRAP_CONNECTED     = 'boostrap_connected'
    ERROR_CONNECT_BOOTSTRAP = 'error_connect_bootstrap'
    START_PROV_BOOT_SUCC    = 'start_provisioning_bootstrap_success'
    START_PROV_BOOT_ERR     = 'start_provisioning_bootstrap_error'
    BOOTSTRAP_COMPLETED     = 'bootstrap_completed'
    BOOTSTRAP_IN_PROGRESS   = 'bootstrap_in_progress'
    BOOTSTRAP_DISCONNECTED  = 'bootstrap_disconnected'
    PERPETUAL_CONNECTED     = 'perpetual_connected'
    TELEMETRIC_STATE_INITED = 'telemetric_state_initialized'
    TELEMETRIC_STATE_SYNCED = 'telemetric_state_synchronized'
    TOCK                    = 'tock'
    GOODBYE                 = 'goodbye'

class ConnectionStateMachine:

    transitions = [
        {'trigger': ConnectionStateNachineLifecycle.POWER_ON, 'source': 'off', 'dest': 'idle'},
        {'trigger': ConnectionStateNachineLifecycle.TEST_INTERNET, 'source': ['idle', 'test_internet_connection', 'prepare_bootstrap', 'prepare_perpetual'], 'dest': 'test_internet_connection'},
        {'trigger': ConnectionStateNachineLifecycle.INTERNET_CONNECTED, 'source': ['test_internet_connection'], 'dest': 'bootstrap_junction'},
        {'trigger': ConnectionStateNachineLifecycle.NO_SAVED_SETTINGS, 'source': ['bootstrap_junction'], 'dest': 'prepare_bootstrap'},
        {'trigger': ConnectionStateNachineLifecycle.FOUND_SAVED_SETTINGS, 'source': ['bootstrap_junction'], 'dest': 'prepare_perpetual'},
        {'trigger': ConnectionStateNachineLifecycle.BOOTSTRAP_CONNECTED, 'source': ['prepare_bootstrap'], 'dest': 'prepare_provisioning'},
        {'trigger': ConnectionStateNachineLifecycle.START_PROV_BOOT_SUCC, 'source': ['prepare_provisioning'], 'dest': 'wait_for_claim'},
        {'trigger': ConnectionStateNachineLifecycle.START_PROV_BOOT_ERR, 'source': ['prepare_provisioning'], 'dest': 'test_internet_connection'},
        {'trigger': ConnectionStateNachineLifecycle.BOOTSTRAP_COMPLETED, 'source': ['wait_for_claim'], 'dest': 'tear_down_bootstrap'},
        {'trigger': ConnectionStateNachineLifecycle.BOOTSTRAP_IN_PROGRESS, 'source': ['wait_for_claim'], 'dest': 'wait_for_claim'},
        {'trigger': ConnectionStateNachineLifecycle.BOOTSTRAP_DISCONNECTED, 'source': '*', 'dest': 'test_internet_connection'},
        {'trigger': ConnectionStateNachineLifecycle.PERPETUAL_CONNECTED, 'source': 'prepare_perpetual', 'dest': 'initialize_telemetric_state'},
        {'trigger': ConnectionStateNachineLifecycle.TELEMETRIC_STATE_INITED, 'source': 'initialize_telemetric_state', 'dest': 'sync_telemetric_state'},
        {'trigger': ConnectionStateNachineLifecycle.TELEMETRIC_STATE_SYNCED, 'source': 'sync_telemetric_state', 'dest': 'work'},
        {'trigger': ConnectionStateNachineLifecycle.TOCK, 'source': 'work', 'dest': 'work'},
        {'trigger': ConnectionStateNachineLifecycle.GOODBYE, 'source': '*', 'dest': 'off'},
    ]

    def __init__(self, deviceIdentifier: DeviceIdentifier, worker: TelemetricWorker, listener) -> None:
        self._deviceIdentifier = deviceIdentifier
        self._worker = worker
        self.machine = AsyncMachine(
            model=self,
            states=[
                'off', 
                'turned_on', 
                'sleep', 
                'idle', 
                'test_internet_connection', 
                'bootstrap_junction', 
                'prepare_bootstrap', 
                'prepare_provisioning', 
                'wait_for_claim', 
                'tear_down_bootstrap',
                'prepare_perpetual',
                'initialize_telemetric_state',
                'sync_telemetric_state',
                'work'
            ],
            transitions=ConnectionStateMachine.transitions, 
            initial='off',
            send_event=True,
            after_state_change=listener
        )

    async def start(self):
        await self.power_on()

    async def triggerLifecycle(self, lifecycle: ConnectionStateNachineLifecycle, afterTime: float = 0):
        logger.debug(f'triggerLifecycle: {str(lifecycle)} after {afterTime}s')
        await self._worker.execute(self._deviceIdentifier, f'DEVICE_LIFECYCLE_{str(lifecycle)}', "default", None)
        await asyncio.sleep(afterTime)
        await self.trigger(str(lifecycle))