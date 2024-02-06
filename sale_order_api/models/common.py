import datetime
import json
import logging

import werkzeug.wrappers

_logger = logging.getLogger(__name__)


def default(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()
    if isinstance(o, bytes):
        return str(o)


def valid_response(data, status=200):
    data = {"count": len(data) if not isinstance(data, str) else 1, "data": data}
    return werkzeug.wrappers.Response(
        status=status, content_type="application/json; charset=utf-8", response=json.dumps(data, default=default),
    )


def invalid_response(typ, message=None, status=401):
    return werkzeug.wrappers.Response(
        status=status,
        content_type="application/json; charset=utf-8",
        response=json.dumps(
            {"type": typ, "message": str(message) if str(message) else "wrong arguments (missing validation)",},
            default=datetime.datetime.isoformat,
        ),
    )