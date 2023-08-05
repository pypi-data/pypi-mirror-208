# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------

class NotInitializedError(RuntimeError):
    def __init__(self, source: object) -> None:
        super().__init__(f"{source.__class__.__qualname__} is not initialized")
