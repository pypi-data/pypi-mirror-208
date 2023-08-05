"""
Main interface for ivs-realtime service.

Usage::

    ```python
    from boto3.session import Session
    from mypy_boto3_ivs_realtime import (
        Client,
        ivsrealtimeClient,
    )

    session = Session()
    client: ivsrealtimeClient = session.client("ivs-realtime")
    ```
"""
from .client import ivsrealtimeClient

Client = ivsrealtimeClient

__all__ = ("Client", "ivsrealtimeClient")
