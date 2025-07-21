# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict
from sqlalchemy.orm import Session
from app.core.db import get_db, DBCoordinate
from app.core.models import Coordinate, OptimizedRouteResponse
from app.core.utils import generate_optimized_route_mock

router = APIRouter()

@router.post("/coordinates/")
async def add_coordinate(coord: Coordinate, db: Session = Depends(get_db)) -> Dict[str, str]:
    """
    Agrega una nueva coordenada a la base de datos.
    """
    db_coord = DBCoordinate(lat=coord.lat, lng=coord.lng)
    db.add(db_coord)
    db.commit()
    db.refresh(db_coord)
    return {"message": "Coordenada agregada exitosamente.", "id": db_coord.id}

@router.get("/coordinates/", response_model=List[Coordinate])
async def get_coordinates(db: Session = Depends(get_db)) -> List[Coordinate]:
    """
    Obtiene todas las coordenadas actuales de la base de datos, ordenadas por ID.
    """
    coords_from_db = db.query(DBCoordinate).order_by(DBCoordinate.id).all()
    return [Coordinate(lat=c.lat, lng=c.lng) for c in coords_from_db]

@router.post("/coordinates/batch/")
async def add_coordinates_batch(coords: List[Coordinate], db: Session = Depends(get_db)) -> Dict[str, str]:
    """
    Agrega múltiples coordenadas a la base de datos, limpiando las existentes
    para simular la carga de una nueva "ruta".
    """
    db.query(DBCoordinate).delete() # Elimina todas las coordenadas existentes
    db.commit()

    db_coords = []
    for coord in coords:
        db_coord = DBCoordinate(lat=coord.lat, lng=coord.lng)
        db.add(db_coord)
        db_coords.append(db_coord)
    db.commit()
    return {"message": f"{len(coords)} coordenadas agregadas exitosamente."}


@router.delete("/coordinates/")
async def clear_coordinates(db: Session = Depends(get_db)) -> Dict[str, str]:
    """
    Limpia todas las coordenadas de la base de datos.
    """
    db.query(DBCoordinate).delete()
    db.commit()
    return {"message": "Todas las coordenadas han sido eliminadas de la base de datos."}


@router.post("/route/optimize/", response_model=OptimizedRouteResponse)
async def optimize_route(db: Session = Depends(get_db)) -> OptimizedRouteResponse:
    """
    Endpoint para la optimización de rutas.
    Obtiene las coordenadas de la DB, las optimiza (con el módulo ML)
    y luego las guarda de nuevo en la DB, sobrescribiendo la ruta anterior.
    """
    current_coords_db = db.query(DBCoordinate).order_by(DBCoordinate.id).all()
    if not current_coords_db:
        raise HTTPException(status_code=400, detail="No hay coordenadas para optimizar.")

    # Convertir objetos de DB a objetos Coordinate para la función de optimización
    coords_for_optimization = [Coordinate(lat=c.lat, lng=c.lng) for c in current_coords_db]

    # Aplicar la función de optimización de ruta (generate_optimized_route_mock ahora llama al 2-opt real)
    optimized_coords_pydantic = generate_optimized_route_mock(coords_for_optimization)

    # Limpiar la tabla y guardar las coordenadas optimizadas
    db.query(DBCoordinate).delete()
    db.commit()

    db_optimized_coords = []
    for coord in optimized_coords_pydantic:
        db_coord = DBCoordinate(lat=coord.lat, lng=coord.lng)
        db.add(db_coord)
        db_optimized_coords.append(db_coord)
    db.commit()

    return OptimizedRouteResponse(
        message="Ruta optimizada generada y guardada.",
        optimized_route=optimized_coords_pydantic
    )


@router.post("/data/save/")
async def save_data_to_db() -> Dict[str, str]:
    """
    Con la persistencia SQLite, las coordenadas se guardan automáticamente
    con cada operación de adición/modificación.
    Este endpoint simplemente confirma que los datos ya están persistidos.
    """
    return {"message": "Datos ya persistidos en la base de datos SQLite."}

@router.post("/data/load/")
async def load_data_from_db(db: Session = Depends(get_db)) -> Dict[str, str]:
    """
    Carga las coordenadas desde la base de datos.
    Este endpoint se mantiene para la compatibilidad con el botón 'Cargar Ruta' en la UI.
    La UI luego llamará a GET /api/coordinates/ para obtener los datos.
    """
    loaded_coords_count = db.query(DBCoordinate).count()
    if loaded_coords_count == 0:
        raise HTTPException(status_code=404, detail="No hay coordenadas guardadas en la base de datos para cargar.")
    return {"message": f"{loaded_coords_count} coordenadas cargadas exitosamente desde la base de datos."}

