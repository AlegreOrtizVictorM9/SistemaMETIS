import json
from typing import List
from app.core.models import Coordinate
import random # Para la simulación de optimización

def save_coordinates_to_json(coordinates: List[Coordinate], filepath: str):
    """
    Guarda una lista de objetos Coordinate en un archivo JSON.
    """
    # Convertir los objetos Coordinate a diccionarios antes de guardar
    data_to_save = [coord.dict() for coord in coordinates]
    with open(filepath, "w") as f:
        json.dump(data_to_save, f, indent=4)

def load_coordinates_from_json(filepath: str) -> List[Coordinate]:
    """
    Carga una lista de coordenadas desde un archivo JSON y las convierte a objetos Coordinate.
    """
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
            # Convertir los diccionarios cargados a objetos Coordinate
            return [Coordinate(**item) for item in data]
    except FileNotFoundError:
        print(f"Advertencia: El archivo '{filepath}' no fue encontrado. Se devolverá una lista vacía.")
        return []
    except json.JSONDecodeError:
        print(f"Error: El archivo '{filepath}' no es un JSON válido o está vacío.")
        return []

def generate_optimized_route_mock(coordinates: List[Coordinate]) -> List[Coordinate]:
    """
    Función mock para simular la optimización de rutas.
    En el futuro, aquí se integrará el algoritmo de Machine Learning.
    Actualmente, simplemente devuelve una versión aleatoriamente reordenada de las coordenadas.
    """
    if not coordinates:
        return []

    # Crear una copia de las coordenadas para no modificar la lista original directamente
    optimized_coordinates = list(coordinates)

    # Simulación de un algoritmo de optimización:
    # Si hay más de un punto, simula un reordenamiento.
    if len(optimized_coordinates) > 1:
        # Aquí se podría implementar un algoritmo de optimización real,
        # como TSP (Traveling Salesperson Problem).
        # Por ahora, un simple shuffle para demostrar el concepto de reordenamiento.
        random.shuffle(optimized_coordinates)

    print("Ruta optimizada (mock) generada.")
    return optimized_coordinates