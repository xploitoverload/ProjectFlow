# app/search/__init__.py
"""
Search and filtering system.
"""

from .search_engine import (
    SearchEngine,
    FilterBuilder,
    SavedSearch
)

__all__ = [
    'SearchEngine',
    'FilterBuilder',
    'SavedSearch'
]
