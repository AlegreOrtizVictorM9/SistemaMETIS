// Initialize the Leaflet map
const map = L.map('map').setView([0, 0], 2); // Initial view centered on the world

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

let markers = [];
let polyline = null;
const coordinateInputsDiv = document.getElementById('coordinate-inputs');
const messageArea = document.getElementById('message-area');

// --- CONSTANTES PARA CÁLCULO DE RUTA Y CONSUMO (MAN TGM) ---
const EARTH_RADIUS_KM = 6371; // Radio medio de la Tierra en kilómetros

// Características aproximadas para un camión MAN TGM (valores de ejemplo)
const MAN_TGM_AVG_SPEED_KMH = 60; // Velocidad promedio en carretera/rural en km/h
const MAN_TGM_FUEL_CONSUMPTION_L_PER_100KM = 30; // Consumo de combustible en Litros por cada 100 km

// --- FUNCIONES DE UTILIDAD ---

// Función para mostrar mensajes en el área de mensajes de la UI
function showMessage(message, isError = false) {
    messageArea.textContent = message;
    messageArea.style.backgroundColor = isError ? '#f8d7da' : '#e2f0d9';
    messageArea.style.color = isError ? '#721c24' : '#28a745';
    messageArea.style.borderColor = isError ? '#f5c6cb' : '#28a745';
    setTimeout(() => {
        messageArea.textContent = '';
        messageArea.style.backgroundColor = '';
        messageArea.style.color = '';
        messageArea.style.borderColor = '';
    }, 5000); // Message disappears after 5 seconds
}

// Función para añadir un nuevo par de campos de entrada de latitud/longitud
function addCoordinateInput(lat = '', lng = '') {
    const div = document.createElement('div');
    div.classList.add('coordinate-input-group');

    div.innerHTML = `
        <label>Lat:</label>
        <input type="number" step="any" placeholder="Latitud" value="${lat}" required>
        <label>Lng:</label>
        <input type="number" step="any" placeholder="Longitud" value="${lng}" required>
        <button class="button danger remove-point-btn">X</button>
    `;
    coordinateInputsDiv.appendChild(div);

    div.querySelector('.remove-point-btn').addEventListener('click', (e) => {
        e.preventDefault();
        div.remove();
        drawRoute(); // Redraw the route if a point is removed
    });
}

// Función para obtener todas las coordenadas de los campos de entrada de la UI
function getCoordinatesFromInputs() {
    const coords = [];
    document.querySelectorAll('#coordinate-inputs .coordinate-input-group').forEach(group => {
        const latInput = group.querySelector('input[type="number"]:first-of-type');
        const lngInput = group.querySelector('input[type="number"]:last-of-type');
        
        const lat = parseFloat(latInput.value);
        const lng = parseFloat(lngInput.value);

        if (!isNaN(lat) && !isNaN(lng)) {
            coords.push({ lat, lng });
        }
    });
    return coords;
}

// Función para actualizar los campos de entrada de la UI con nuevas coordenadas
function updateInputsWithCoordinates(coords) {
    coordinateInputsDiv.innerHTML = '';
    coords.forEach(coord => {
        addCoordinateInput(coord.lat, coord.lng);
    });
    if (coords.length === 0) {
        addCoordinateInput();
    }
}

// Función para calcular la distancia Haversine entre dos puntos (lat1, lon1) y (lat2, lon2)
// Retorna la distancia en kilómetros
function haversineDistance(lat1, lon1, lat2, lon2) {
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = 
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    const distance = EARTH_RADIUS_KM * c;
    return distance;
}

// Función para dibujar marcadores y la polilínea en el mapa
async function drawRoute() {
    // Limpiar marcadores y polilínea existentes
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];
    if (polyline) {
        map.removeLayer(polyline);
        polyline = null;
    }

    const coords = getCoordinatesFromInputs();
    if (coords.length === 0) {
        showMessage("No hay coordenadas para trazar.", true);
        return;
    }

    let latlngs = [];
    for (let i = 0; i < coords.length; i++) {
        const currentCoord = coords[i];
        const latlng = [currentCoord.lat, currentCoord.lng];
        latlngs.push(latlng);

        // Crear icono de marcador numerado y de color distinto
        const markerIcon = L.divIcon({
            className: 'custom-div-icon',
            html: `<div class="marker-pin"></div><span class="marker-number">${i + 1}</span>`,
            iconSize: [30, 42], // Tamaño del icono
            iconAnchor: [15, 42] // Punto de anclaje del icono
        });

        // Calcular información para el popup (si no es el último punto)
        let popupContent = `<b>Punto ${i + 1}:</b><br>Lat: ${currentCoord.lat.toFixed(6)}, Lng: ${currentCoord.lng.toFixed(6)}`;

        if (i < coords.length - 1) {
            const nextCoord = coords[i + 1];
            const segmentDistanceKm = haversineDistance(
                currentCoord.lat, currentCoord.lng,
                nextCoord.lat, nextCoord.lng
            );

            // Calcular tiempo aproximado
            const segmentTimeHours = segmentDistanceKm / MAN_TGM_AVG_SPEED_KMH;
            const segmentTimeMinutes = (segmentTimeHours * 60).toFixed(0);

            // Calcular consumo de combustible
            const segmentFuelLiters = (segmentDistanceKm / 100) * MAN_TGM_FUEL_CONSUMPTION_L_PER_100KM;

            popupContent += `<br><br><b>Al Siguiente Punto (${i + 2}):</b>
                             <br>Distancia: ${segmentDistanceKm.toFixed(2)} km
                             <br>Tiempo Aprox: ${segmentTimeMinutes} minutos
                             <br>Consumo Combustible: ${segmentFuelLiters.toFixed(2)} Litros`;
        } else {
            // Mensaje para el último punto
            popupContent += `<br><br>Este es el último punto de la ruta.`;
        }

        // Agregar marcador al mapa con el icono y el popup
        const marker = L.marker(latlng, { icon: markerIcon }).addTo(map)
            .bindPopup(popupContent);
        markers.push(marker);
    }

    if (latlngs.length > 1) {
        polyline = L.polyline(latlngs, { color: 'blue', weight: 4, opacity: 0.7 }).addTo(map);
        map.fitBounds(polyline.getBounds()); // Adjust map view to the route
    } else if (latlngs.length === 1) {
        map.setView(latlngs[0], 13); // Center on the single point if only one
    }

    // When drawing a route, update coordinates on the backend (e.g., when inputs change)
    try {
        const response = await fetch('/api/coordinates/batch/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(coords)
        });
        const result = await response.json();
        if (!response.ok) {
            throw new Error(result.detail || 'Error al actualizar coordenadas en el backend.');
        }
        showMessage(result.message);
    } catch (error) {
        console.error('Error al actualizar coordenadas en el backend:', error);
        showMessage(`Error: ${error.message}`, true);
    }
}

// --- EVENT LISTENERS PARA LOS BOTONES ---

document.getElementById('add-point-btn').addEventListener('click', () => {
    addCoordinateInput();
});

document.getElementById('draw-route-btn').addEventListener('click', () => {
    drawRoute();
});

document.getElementById('optimize-route-btn').addEventListener('click', async () => {
    showMessage("Optimizando ruta con algoritmo 2-opt...");
    try {
        const response = await fetch('/api/route/optimize/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        const result = await response.json();
        if (!response.ok) {
            throw new Error(result.detail || 'Error al optimizar la ruta.');
        }
        showMessage(result.message);
        const getCoordsResponse = await fetch('/api/coordinates/');
        const optimizedCoords = await getCoordsResponse.json();
        updateInputsWithCoordinates(optimizedCoords);
        drawRoute();
    } catch (error) {
        console.error('Error al optimizar la ruta:', error);
        showMessage(`Error: ${error.message}`, true);
    }
});

document.getElementById('save-route-btn').addEventListener('click', async () => {
    showMessage("La ruta ya está guardada en la base de datos.");
});

document.getElementById('load-route-btn').addEventListener('click', async () => {
    showMessage("Cargando ruta de la base de datos...");
    try {
        const response = await fetch('/api/data/load/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        const result = await response.json();
        if (!response.ok) {
            throw new Error(result.detail || 'Error al cargar la ruta.');
        }
        showMessage(result.message);
        const getCoordsResponse = await fetch('/api/coordinates/');
        const loadedCoords = await getCoordsResponse.json();
        updateInputsWithCoordinates(loadedCoords);
        drawRoute();
    } catch (error) {
        console.error('Error al cargar la ruta:', error);
        showMessage(`Error: ${error.message}`, true);
    }
});

document.getElementById('clear-map-btn').addEventListener('click', async () => {
    // Clear the map
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];
    if (polyline) {
        map.removeLayer(polyline);
        polyline = null;
    }
    // Clear inputs in the UI
    coordinateInputsDiv.innerHTML = '';
    addCoordinateInput();
    addCoordinateInput();

    // Clear coordinates in the backend (DB)
    try {
        const response = await fetch('/api/coordinates/', {
            method: 'DELETE'
        });
        const result = await response.json();
        if (!response.ok) {
            throw new Error(result.detail || 'Error al limpiar coordenadas en el backend.');
        }
        showMessage(result.message);
    } catch (error) {
        console.error('Error al limpiar coordenadas en el backend:', error);
        showMessage(`Error: ${error.message}`, true);
    }
});

// Initial coordinate loading on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
    fetch('/api/coordinates/')
        .then(response => response.json())
        .then(coords => {
            if (coords && coords.length > 0) {
                updateInputsWithCoordinates(coords);
                drawRoute();
            } else {
                addCoordinateInput();
                addCoordinateInput();
            }
        })
        .catch(error => {
            console.error('Error loading initial coordinates:', error);
            showMessage('Error al cargar coordenadas iniciales.', true);
            addCoordinateInput();
            addCoordinateInput();
        });
});
