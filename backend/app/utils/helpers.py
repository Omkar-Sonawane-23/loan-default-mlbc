"""Misc helper functions."""
import datetime


def utc_now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()
