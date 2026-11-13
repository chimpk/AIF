"""Invalid plugin double whose factory returns a non-TankAgent object (Owner: B)."""


def create_agent() -> object:
    """Return an invalid object type."""
    return {"not": "an agent"}
