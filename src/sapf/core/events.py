from __future__ import annotations

# For now, the shared step event type is SearchStep.
# Keeping this alias allows future refactors where algorithms emit more granular events.
from ..algorithms.base import SearchStep, SearchStatus

__all__ = ["SearchStep", "SearchStatus"]