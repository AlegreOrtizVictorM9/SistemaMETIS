import numpy as np
from scipy.spatial.distance import cdist
from python_tsp.heuristics import solve_tsp_two_opt
from typing import List
from app.core.models import Coordinate

def optimize_route_ml(coordinates: List[Coordinate]) -> List[Coordinate]:
    """
    Optimiza la ruta para una lista determinada de coordenadas utilizando el algoritmo heurístico de 2 puntos basado en el Vehicle Routing Problem.

    Args:
        coordinates (List[Coordinate]): A list of Coordinate objects (lat, lng).

    Returns:
        List[Coordinate]: Una nueva lista de coordenadas reordenadas para la ruta optimizada.
                          Devuelve la lista original si se proporcionan menos de 2 puntos.
    """
    if not coordinates or len(coordinates) < 2:
        return coordinates

    # Convertir objetos de coordenadas a una matriz NumPy para calcular distancias
    points_array = np.array([[coord.lat, coord.lng] for coord in coordinates])

    # Calcular la matriz de distancias euclidianas entre todos los pares de puntos
    distance_matrix = cdist(points_array, points_array, metric='euclidean')
    np.fill_diagonal(distance_matrix, 0) # Ensure distance from a point to itself is 0

    # Aplique la heurística del Vehicle Routing Problem para encontrar una permutación optimizada.
    permutation, _ = solve_tsp_two_opt(distance_matrix)

    # Reordene las coordenadas originales según la permutación optimizada
    optimized_coordinates = [coordinates[i] for i in permutation]

    return optimized_coordinates

