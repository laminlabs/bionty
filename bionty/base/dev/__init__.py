"""Dev.

.. autosummary::
   :toctree: .

   InspectResult
"""


def __getattr__(name: str):
    if name == "InspectResult":
        from lamindb.models.can_curate import InspectResult

        return InspectResult
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
