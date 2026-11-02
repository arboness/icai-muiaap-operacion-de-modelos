"""Estado de sesión de Streamlit aislado para poder probarlo sin Streamlit."""

from __future__ import annotations

from collections.abc import MutableMapping
from typing import get_args

from model_ui.contracts import UiPhase, UiState
from model_ui.telemetry import Telemetry

LAST_STATE_KEY = "last_state"
TELEMETRY_KEY = "telemetry"
LAST_VALUES_KEY = "last_values"


def initialize_session_state(
    session_state: MutableMapping[str, object],
) -> None:
    """TODO: crea solo las entradas de sesión que todavía no existan."""
    session_state[LAST_STATE_KEY] = session_state.get(LAST_STATE_KEY,  UiState(phase=get_args(UiPhase)[0]))
    session_state[TELEMETRY_KEY] = session_state.get(TELEMETRY_KEY, Telemetry())
    session_state[LAST_VALUES_KEY] = session_state.get(LAST_VALUES_KEY, {})

def clear_last_state(session_state: MutableMapping[str, object]) -> None:
    """TODO: vuelve a idle sin perder la telemetría acumulada."""

    session_state[LAST_STATE_KEY] = UiState(phase=get_args(UiPhase)[0])
    session_state[LAST_VALUES_KEY] = {}
