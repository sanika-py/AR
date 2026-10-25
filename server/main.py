"""Serve the FastAPI API and the built React application from one process."""

from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.app import app

FRONTEND_DIST = Path(__file__).resolve().parents[1] / "frontend" / "dist"
FRONTEND_ASSETS = FRONTEND_DIST / "assets"

if FRONTEND_DIST.is_dir():
    if FRONTEND_ASSETS.is_dir():
        app.mount(
            "/assets",
            StaticFiles(directory=FRONTEND_ASSETS),
            name="frontend-assets",
        )

    @app.get("/{asset_path:path}", include_in_schema=False)
    async def frontend_asset(asset_path: str) -> FileResponse:
        """Return a built asset or the SPA entry point for browser routes."""
        root = FRONTEND_DIST.resolve()
        requested = (root / asset_path).resolve()
        if root not in requested.parents and requested != root:
            raise HTTPException(status_code=404, detail="Asset not found")
        if requested.is_file():
            return FileResponse(requested)
        index = root / "index.html"
        if not index.is_file():
            raise HTTPException(status_code=503, detail="Build the frontend first")
        return FileResponse(index)
