# -*- coding: utf-8 -*-
from pydantic import BaseModel
from typing import List

class Coordinate(BaseModel):
    """
    Modelo Pydantic para representar una coordenada (latitud, longitud).
    """
    lat: float
    lng: float

class OptimizedRouteResponse(BaseModel):
    """
    Modelo Pydantic para la respuesta del endpoint de optimización de ruta.
    """
    message: str
    optimized_route: List[Coordinate]

