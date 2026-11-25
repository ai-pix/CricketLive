"""Cricket Live package entry point."""

import uvicorn


def main() -> None:
    """Run the FastAPI scoreboard server."""
    uvicorn.run("cricket_live.server:app", host="127.0.0.1", port=8000, reload=False)
