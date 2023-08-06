"""Helpers for command-line utilities."""

import minknow_api.manager


def connect_to_manager(host):
    host_parts = host.split(":", 1)
    host = host_parts[0]
    port = host_parts[1] if len(host_parts) > 1 else None
    return minknow_api.manager.Manager(host, port)


def find_position(manager, position_name):
    pos_name_lower = position_name.lower()
    candidates = [
        pos
        for pos in manager.flow_cell_positions()
        if pos.name.lower() == pos_name_lower
    ]
    assert len(candidates) < 2
    if candidates:
        return candidates[0]
    return None
