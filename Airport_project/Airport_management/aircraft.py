import matplotlib.pyplot as plt
import os
from math import radians, cos, sin, asin, sqrt
from airport import IsSchengenAirport, LoadAirports


class Aircraft:
    def __init__(self, aircraft_id="", airline="", origin="", arrival_time="",
                 destination="", departure_time=""):
        self.aircraft_id = aircraft_id
        self.airline = airline
        self.origin = origin  # ICAO code of arrival airport
        self.arrival_time = arrival_time  # Format hh:mm
        self.destination = destination  # ICAO code of departure airport (V4)
        self.departure_time = departure_time  # Format hh:mm (V4)


# ===== UTILITY FUNCTION: CONVERT TIME TO MINUTES =====
def TimeToMinutes(time_str):
    """Convierte tiempo en formato hh:mm a minutos desde medianoche"""
    try:
        parts = time_str.split(':')
        hours = int(parts[0])
        minutes = int(parts[1])
        return hours * 60 + minutes
    except:
        return -1


# ===== LOAD ARRIVALS =====
def LoadArrivals(filename):
    """Carga vuelos del archivo de llegadas"""
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
                                aircraft = Aircraft(
                                    aircraft_id=aircraft_id,
                                    airline=airline,
                                    origin=origin,
                                    arrival_time=arrival_time
                                )
                                aircrafts.append(aircraft)
                        except:
                            pass
                i += 1
    except FileNotFoundError:
        print(f"Error: Archivo '{filename}' no encontrado")
        return []

    return aircrafts


# ===== LOAD DEPARTURES (V4) =====
def LoadDepartures(filename):
    """Carga vuelos de salida desde un archivo (V4)"""
    departures = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            i = 1  # Saltar encabezado si existe
            while i < len(lines):
                line = lines[i].strip()
                if line:
                    parts = line.split()
                    if len(parts) >= 4:
                        try:
                            aircraft_id = parts[0]
                            destination = parts[1]
                            departure_time = parts[2]
                            airline = parts[3]

                            aircraft = Aircraft(
                                aircraft_id=aircraft_id,
                                airline=airline,
                                destination=destination,
                                departure_time=departure_time
                            )
                            departures.append(aircraft)
                        except:
                            pass
                i += 1
    except FileNotFoundError:
        print(f"Error: Archivo '{filename}' no encontrado")
        return []

    return departures


# ===== MERGE MOVEMENTS (V4) =====
def MergeMovements(arrivals, departures):
    """Fusiona llegadas y salidas del mismo avión si los tiempos son compatibles (V4)"""
    if not arrivals or not departures:
        return [], -1

    merged = []
    used_departures = set()

    # Copiar todas las llegadas e intentar fusionar
    i = 0
    while i < len(arrivals):
        arrival = arrivals[i]
        merged_aircraft = Aircraft(
            aircraft_id=arrival.aircraft_id,
            airline=arrival.airline,
            origin=arrival.origin,
            arrival_time=arrival.arrival_time
        )

        # Buscar salida correspondiente
        j = 0
        while j < len(departures):
            departure = departures[j]
            if departure.aircraft_id == arrival.aircraft_id and j not in used_departures:
                # Verificar compatibilidad de tiempos
                arr_time = TimeToMinutes(arrival.arrival_time)
                dep_time = TimeToMinutes(departure.departure_time)

                if arr_time >= 0 and dep_time >= 0 and arr_time < dep_time:
                    # Fusionar datos
                    merged_aircraft.destination = departure.destination
                    merged_aircraft.departure_time = departure.departure_time
                    used_departures.add(j)
                    break
            j += 1

        merged.append(merged_aircraft)
        i += 1

    # Agregar salidas que no tuvieron llegada (aviones nocturnos)
    j = 0
    while j < len(departures):
        if j not in used_departures:
            merged.append(departures[j])
        j += 1

    return merged, 0


# ===== NIGHT AIRCRAFT (V4) =====
def NightAircraft(aircrafts):
    """Retorna lista de aviones que solo tienen información de salida (aviones nocturnos) (V4)"""
    if not aircrafts:
        return [], -1

    night_aircrafts = []
    i = 0
    while i < len(aircrafts):
        aircraft = aircrafts[i]
        # Aircraft es nocturno si no tiene arrival_time pero sí tiene departure_time
        if not aircraft.arrival_time and aircraft.departure_time:
            night_aircrafts.append(aircraft)
        i += 1

    return night_aircrafts, 0


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
        if aircraft.arrival_time:
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
        if aircraft.origin:
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
        if aircraft.origin:
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
        if aircraft.origin:
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
            f.write("AIRCRAFT\tORIGIN\tARRIVAL\tDESTINATION\tDEPARTURE\tAIRLINE\n")
            i = 0
            while i < len(aircrafts):
                aircraft = aircrafts[i]
                origin = aircraft.origin if aircraft.origin else "-"
                arrival = aircraft.arrival_time if aircraft.arrival_time else "-"
                destination = aircraft.destination if aircraft.destination else "-"
                departure = aircraft.departure_time if aircraft.departure_time else "-"

                f.write(
                    f"{aircraft.aircraft_id}\t{origin}\t{arrival}\t{destination}\t{departure}\t{aircraft.airline}\n")
                i += 1
        return len(aircrafts)
    except:
        return -1


# ===== TEST SECTION =====
if __name__ == "__main__":
    print("=== TEST AIRCRAFT.PY (V4) ===\n")

    print("Test 1: Cargar vuelos de llegada")
    arrivals = LoadArrivals("Arrivals_file.txt")
    print(f"✓ {len(arrivals)} vuelos de llegada cargados\n")

    print("Test 2: Cargar vuelos de salida (V4)")
    departures = LoadDepartures("Departures_file.txt")
    print(f"✓ {len(departures)} vuelos de salida cargados\n")

    print("Test 3: Fusionar movimientos (V4)")
    merged, status = MergeMovements(arrivals, departures)
    print(f"✓ {len(merged)} vuelos fusionados\n")

    print("Test 4: Identificar aviones nocturnos (V4)")
    night_aircrafts, status = NightAircraft(merged)
    print(f"✓ {len(night_aircrafts)} aviones nocturnos detectados\n")

    if len(merged) > 0:
        print("Test 5: Mostrar primeros 3 vuelos fusionados")
        i = 0
        while i < min(3, len(merged)):
            ac = merged[i]
            origin = ac.origin if ac.origin else "-"
            dest = ac.destination if ac.destination else "-"
            arr_time = ac.arrival_time if ac.arrival_time else "-"
            dep_time = ac.departure_time if ac.departure_time else "-"
            print(f"  {ac.aircraft_id} | {ac.airline} | {origin} -> {dest} | Llega: {arr_time} | Sale: {dep_time}")
            i += 1
        print()