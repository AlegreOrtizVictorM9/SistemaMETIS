from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List, Dict

from app.api.routes import router as api_router
from app.core.utils import save_coordinates_to_json, load_coordinates_from_json

app = FastAPI(
    title="METIS: Planificación de rutas de distribución logística",
    description="Aplicación web para planificar y optimizar rutas de distribución para el Ejército del Perú.",
    version="1.0.0 Alpha"
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(api_router, prefix="/api")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Renderiza la página principal de la aplicación.
    """
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
