# src/core/limiter.py
"""Limiter compartido (slowapi) para endpoints públicos sensibles a abuso."""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
