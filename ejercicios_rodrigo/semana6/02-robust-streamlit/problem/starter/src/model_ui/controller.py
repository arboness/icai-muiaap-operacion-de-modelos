"""TODOs del controlador de estados independiente de Streamlit."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from time import perf_counter
from uuid import uuid4

from model_ui.contracts import UiState
from model_ui.gateway import InferenceGateway
from model_ui.telemetry import Telemetry

StateEmitter = Callable[[UiState], None]
Clock = Callable[[], float]
RequestIdFactory = Callable[[], str]


class PredictionController:
    """Orquesta loading, gateway, errores y telemetría."""

    def __init__(
        self,
        gateway: InferenceGateway,
        *,
        telemetry: Telemetry | None = None,
        clock: Clock = perf_counter,
        request_id_factory: RequestIdFactory | None = None,
    ) -> None:
        self.gateway = gateway
        self.telemetry = telemetry or Telemetry()
        self._clock = clock
        self._request_id_factory = request_id_factory or (lambda: uuid4().hex[:10])

    def submit(
        self,
        values: Mapping[str, object],
        *,
        emit: StateEmitter | None = None,
    ) -> UiState:
        """TODO: emite loading, mide, valida la salida y devuelve success/error."""

        raise NotImplementedError(
            "TODO: implementa la transición loading -> success/error"
        )
