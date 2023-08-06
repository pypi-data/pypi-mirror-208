import logging
from datetime import datetime
from typing import List
from typing import Optional

import pytz
from twisted.internet.defer import Deferred
from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import LoopingCall
from vortex.DeferUtil import vortexLogFailure
from vortex.Tuple import Tuple
from vortex.TupleAction import TupleActionABC

from peek_core_device._private.server.controller.NotifierController import (
    NotifierController,
)
from peek_core_device._private.tuples.BandwidthTestResultTuple import (
    BandwidthTestResultTuple,
)
from peek_plugin_base.storage.RunPyInPg import runPyInPg

logger = logging.getLogger(__name__)


class BandwidthResultController:
    INSERT_SECONDS = 120.0

    def __init__(
        self, dbSessionCreator, notifierController: NotifierController
    ):
        self._dbSessionCreator = dbSessionCreator
        self._notifierController = notifierController

        self._metricUpdateQueue = {}
        self._insertLoopingCall = None

    def start(self):
        self._insertLoopingCall = LoopingCall(self._poll)
        d = self._insertLoopingCall.start(self.INSERT_SECONDS)
        d.addErrback(vortexLogFailure, logger)

    def shutdown(self):
        if self._insertLoopingCall and self._insertLoopingCall.running:
            self._insertLoopingCall.stop()

        self._insertLoopingCall = None
        self._notifierController = None
        self._metricUpdateQueue = {}

    def processTupleAction(self, tupleAction: TupleActionABC) -> List[Tuple]:
        if isinstance(tupleAction, BandwidthTestResultTuple):
            self._metricUpdateQueue[
                tupleAction.deviceToken
            ] = tupleAction.metric
            return []

    @inlineCallbacks
    def _poll(self) -> Optional[Deferred]:
        if not self._metricUpdateQueue:
            return

        toProcess, self._metricUpdateQueue = self._metricUpdateQueue, {}

        startTime = datetime.now(pytz.UTC)
        yield runPyInPg(
            logger, self._dbSessionCreator, self._updateMetric, None, toProcess
        )
        logger.debug(
            "Inserted %s bandwidth metrics in %s",
            len(toProcess),
            datetime.now(pytz.UTC) - startTime,
        )

        self._notifierController.notifyAllDeviceInfos()

    @classmethod
    def _updateMetric(cls, plpy, updates: dict[str, int]) -> None:
        """Process Offline Cache Update

        :rtype: Deferred
        """

        plan = plpy.prepare(
            """UPDATE core_device."DeviceInfo"
            SET "lastBandwidthMetric" = $2
            WHERE "deviceToken" = $1;""",
            ["text", "integer"],
        )
        for deviceToken, metric in updates.items():
            plpy.execute(plan, [deviceToken, metric])
