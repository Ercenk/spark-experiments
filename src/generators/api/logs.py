"""Log retrieval handler."""

from __future__ import annotations

from flask import jsonify, request

from src.generators.services.log_reader import LogReaderService


def register_logs(bp, log_reader: LogReaderService):
    @bp.get('/logs')
    def logs():  # type: ignore
        limit = request.args.get('limit', '100')
        since = request.args.get('since')
        level = request.args.get('level')
        data = log_reader.read_logs(limit=limit, since=since, level=level)
        return jsonify(data)
