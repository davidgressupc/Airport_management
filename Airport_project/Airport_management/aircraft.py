import matplotlib.pyplot as plt
import os
from math import radians, cos, sin, asin, sqrt
from airport import IsSchengenAirport, LoadAirports


class Aircraft:
    def __init__(self, aircraft_id, airline, origin, arrival_time):
        self.aircraft_id = aircraft_id
        self.airline = airline
        self.origin = origin
        self.arrival_time = arrival_time


# ===== LOAD ARRIVALS =====
def LoadArrivals(filename):
    """Carga vuelos del archivo"""
    aircrafts = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            i = 1  # Saltar encabezado
            while i < len(lines):
                line = lines[i].strip()
                if line:
                    parts = line.split()
                    if len(parts) >= 4:
                        try:
                            aircraft_id = parts[0]
                            origin = parts[1]
                            arrival_time = parts[2]
                            airline = parts[3]

                            # Validar formato de hora
                            if ':' in arrival_time or len(arrival_time) == 4:
                                aircraft = Aircraft(aircraft_id, airline, origin, arrival_time)
                                aircrafts.append(aircraft)
                        except:
                            pass
                i += 1
    except FileNotFoundError:
        print(f"Error: Archivo '{filename}' no encontrado")
        return []

    return aircrafts


# ===== PLOT ARRIVALS =====
def PlotArrivals(aircrafts):
    """Gráfica de llegadas por hora"""
    if not aircrafts:
        print("Error: No hay vuelos para mostrar")
        return None, None

    # Contar llegadas por hora
    hours = {}
    i = 0
    while i < len(aircrafts):
        aircraft = aircrafts[i]
        time_parts = aircraft.arrival_time.split(':')
        try:
            hour = int(time_parts[0])
            if hour not in hours:
                hours[hour] = 0
            hours[hour] += 1
        except:
            pass
        i += 1

    # Crear gráfica
    fig, ax = plt.subplots(figsize=(12, 6))

    hours_list = []
    counts = []
    h = 0
    while h < 24:
        hours_list.append(f"{h}:00")
        counts.append(hours.get(h, 0))
        h += 1

    ax.bar(hours_list, counts, color='#3498db', edgecolor='black', linewidth=1.5)
    ax.set_xlabel('Hora del día', fontsize=12)
    ax.set_ylabel('Número de llegadas', fontsize=12)
    ax.set_title('Llegadas de Vuelos por Hora (LEBL)', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    plt.xticks(rotation=45)
    fig.tight_layout()

    return fig, ax


# ===== PLOT AIRLINES =====
def PlotAirlines(aircrafts):
    """Gráfica de vuelos por aerolínea"""
    if not aircrafts:
        print("Error: No hay vuelos para mostrar")
        return None, None

    # Contar vuelos por aerolínea
    airlines = {}
    i = 0
    while i < len(aircrafts):
        aircraft = aircrafts[i]
        airline = aircraft.airline
        if airline not in airlines:
            airlines[airline] = 0
        airlines[airline] += 1
        i += 1

    # Crear gráfica
    fig, ax = plt.subplots(figsize=(12, 6))

    airlines_list = []
    counts = []
    for airline, count in sorted(airlines.items()):
        airlines_list.append(airline)
        counts.append(count)

    ax.bar(airlines_list, counts, color='#e74c3c', edgecolor='black', linewidth=1.5)
    ax.set_xlabel('Aerolínea (Código ICAO)', fontsize=12)
    ax.set_ylabel('Número de vuelos', fontsize=12)
    ax.set_title('Vuelos por Aerolínea (LEBL)', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    plt.xticks(rotation=45)
    fig.tight_layout()

    return fig, ax


# ===== PLOT FLIGHTS TYPE =====
def PlotFlightsType(aircrafts, airports):
    """Gráfica Schengen vs No-Schengen"""
    if not aircrafts or not airports:
        print("Error: No hay datos para mostrar")
        return None, None

    schengen_count = 0
    non_schengen_count = 0

    i = 0
    while i < len(aircrafts):
        aircraft = aircrafts[i]
        if IsSchengenAirport(aircraft.origin):
            schengen_count += 1
        else:
            non_schengen_count += 1
        i += 1

    # Crear gráfica
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.bar(['Schengen', 'No-Schengen'], [schengen_count, non_schengen_count],
           color=['#27ae60', '#e74c3c'], edgecolor='black', linewidth=2)
    ax.set_ylabel('Número de vuelos', fontsize=12)
    ax.set_title('Vuelos Schengen vs No-Schengen (LEBL)', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    # Etiquetas
    ax.text(0, schengen_count + 1, str(schengen_count), ha='center', fontweight='bold', fontsize=12)
    ax.text(1, non_schengen_count + 1, str(non_schengen_count), ha='center', fontweight='bold', fontsize=12)

    fig.tight_layout()

    return fig, ax


# ===== HAVERSINE DISTANCE =====
def HaversineDistance(lat1, lon1, lat2, lon2):
    """Calcula distancia entre dos coordenadas en km"""
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371

    return c * r


# ===== LONG DISTANCE ARRIVALS =====
def LongDistanceArrivals(aircrafts, airports):
    """Retorna vuelos de larga distancia (>2000 km)"""
    long_distance = []

    # Coordenadas de LEBL
    lebl_lat = 41.2974
    lebl_lon = 2.0833

    i = 0
    while i < len(aircrafts):
        aircraft = aircrafts[i]

        # Buscar aeropuerto de origen
        j = 0
        found = False
        while j < len(airports):
            airport = airports[j]
            if airport.icao_code == aircraft.origin:
                distance = HaversineDistance(lebl_lat, lebl_lon,
                                             airport.latitude, airport.longitude)
                if distance > 2000:
                    long_distance.append(aircraft)
                found = True
                break
            j += 1

        i += 1

    return long_distance


# ===== MAP FLIGHTS =====
def MapFlights(aircrafts, airports):
    """Crea mapa KML con trayectorias de vuelos"""
    if not aircrafts or not airports:
        print("Error: No hay datos para generar mapa")
        return None

    try:
        import simplekml
    except ImportError:
        print("simplekml no instalado. Ejecuta: pip install simplekml")
        return None

    kml = simplekml.Kml()

    # Coordenadas de LEBL
    lebl_lat = 41.2974
    lebl_lon = 2.0833

    i = 0
    while i < len(aircrafts):
        aircraft = aircrafts[i]

        # Buscar aeropuerto de origen
        j = 0
        while j < len(airports):
            airport = airports[j]
            if airport.icao_code == aircraft.origin:
                # Determinar color (Schengen o no)
                is_schengen = IsSchengenAirport(aircraft.origin)
                color = simplekml.Color.green if is_schengen else simplekml.Color.red

                # Crear línea
                line = kml.newlinestring(
                    name=f"{aircraft.aircraft_id} ({aircraft.airline})",
                    description=f"De: {aircraft.origin}\nA: LEBL\nHora: {aircraft.arrival_time}",
                    coords=[(airport.longitude, airport.latitude), (lebl_lon, lebl_lat)]
                )
                line.style.linestyle.color = color
                line.style.linestyle.width = 2

                break
            j += 1

        i += 1

    # Guardar archivo
    base_dir = os.path.dirname(__file__)
    filepath = os.path.join(base_dir, "flights_map.kml")
    kml.save(filepath)

    print(f"Mapa guardado: {filepath}")
    return filepath


# ===== SAVE FLIGHTS =====
def SaveFlights(aircrafts, filename):
    """Guarda vuelos en archivo"""
    if not aircrafts:
        return -1

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("AIRCRAFT ORIGIN ARRIVAL AIRLINE\n")
            i = 0
            while i < len(aircrafts):
                aircraft = aircrafts[i]
                f.write(f"{aircraft.aircraft_id} {aircraft.origin} {aircraft.arrival_time} {aircraft.airline}\n")
                i += 1
        return len(aircrafts)
    except:
        return -1


# ===== TEST SECTION =====
if __name__ == "__main__":
    print("=== TEST AIRCRAFT.PY ===\n")

    print("Test 1: Cargar vuelos")
    aircrafts = LoadArrivals("Arrivals.txt")
    print(f"✓ {len(aircrafts)} vuelos cargados\n")

    if len(aircrafts) > 0:
        print("Test 2: Mostrar primeros 3 vuelos")
        i = 0
        while i < min(3, len(aircrafts)):
            ac = aircrafts[i]
            print(f"  {ac.aircraft_id} | {ac.airline} | {ac.origin} -> LEBL ({ac.arrival_time})")
            i += 1
        print()

        print("Test 3: Gráficas")
        fig1, ax1 = PlotArrivals(aircrafts)
        fig2, ax2 = PlotAirlines(aircrafts)
        print("✓ Gráficas generadas")

        print("\nTest 4: Guardar vuelos")
        result = SaveFlights(aircrafts, "test_flights.txt")
        print(f"✓ {result} vuelos guardados")
