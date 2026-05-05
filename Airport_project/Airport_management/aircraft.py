import matplotlib.pyplot as plt
import os
from airport import Airport, IsSchengenAirport
import math


class Aircraft:
    def __init__(self, aircraft_id, airline, origin, arrival_time):
        self.aircraft_id = aircraft_id
        self.airline = airline
        self.origin = origin
        self.arrival_time = arrival_time
        self.origin_lat = 0.0
        self.origin_lon = 0.0


# ===== HAVERSINE DISTANCE FUNCTION =====
def HaversineDistance(lat1, lon1, lat2, lon2):
    """Calcula la distancia en km entre dos puntos usando la fórmula de Haversine"""
    R = 6371  # Radio de la Tierra en km

    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad

    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance


def ParseTime(time_str):
    """Convierte una cadena de tiempo (hh:mm o h:mm) a minutos desde medianoche"""
    try:
        parts = time_str.split(':')
        if len(parts) != 2:
            return -1
        hours = int(parts[0])
        minutes = int(parts[1])
        if hours < 0 or hours > 23 or minutes < 0 or minutes > 59:
            return -1
        return hours * 60 + minutes
    except:
        return -1


# ===== LOAD ARRIVALS =====
def LoadArrivals(filename):
    """Carga los vuelos de llegada desde un archivo"""
    aircrafts = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines[1:]:  # Saltar la cabecera
                parts = line.strip().split()
                if len(parts) >= 4:
                    aircraft_id = parts[0]
                    origin = parts[1]
                    arrival_time_str = parts[2]
                    airline = parts[3]

                    # Validar tiempo
                    time_minutes = ParseTime(arrival_time_str)
                    if time_minutes < 0:
                        continue

                    # Crear Aircraft
                    aircraft = Aircraft(aircraft_id, airline, origin, arrival_time_str)
                    aircrafts.append(aircraft)
    except FileNotFoundError:
        print(f"Error: Fichero '{filename}' no encontrado")
        return []

    return aircrafts


# ===== PLOT ARRIVALS =====
def PlotArrivals(aircrafts):
    """Muestra un gráfico de frecuencia de llegadas por hora"""
    if not aircrafts:
        print("Error: No hay vuelos para mostrar")
        return None, None

    # Contar llegadas por hora
    hourly_count = [0] * 24

    for aircraft in aircrafts:
        time_minutes = ParseTime(aircraft.arrival_time)
        if time_minutes >= 0:
            hour = time_minutes // 60
            if 0 <= hour < 24:
                hourly_count[hour] += 1

    # Crear gráfica
    fig, ax = plt.subplots(figsize=(12, 6))
    hours = list(range(24))
    ax.bar(hours, hourly_count, color='#3498db', edgecolor='black', linewidth=1.5)
    ax.set_xlabel('Hora del día', fontsize=12)
    ax.set_ylabel('Número de vuelos', fontsize=12)
    ax.set_title('Frecuencia de llegadas por hora a LEBL', fontsize=14, fontweight='bold')
    ax.set_xticks(hours)
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    fig.tight_layout()
    return fig, ax


# ===== SAVE FLIGHTS =====
def SaveFlights(aircrafts, filename):
    """Guarda la información de vuelos en un archivo"""
    if not aircrafts:
        return -1

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("AIRCRAFT ORIGIN ARRIVAL AIRLINE\n")
            for aircraft in aircrafts:
                aircraft_id = aircraft.aircraft_id if aircraft.aircraft_id else "-"
                origin = aircraft.origin if aircraft.origin else "-"
                arrival = aircraft.arrival_time if aircraft.arrival_time else "-"
                airline = aircraft.airline if aircraft.airline else "-"
                f.write(f"{aircraft_id} {origin} {arrival} {airline}\n")
        return len(aircrafts)
    except:
        return -1


# ===== PLOT AIRLINES =====
def PlotAirlines(aircrafts):
    """Muestra un gráfico de barras con vuelos por aerolínea"""
    if not aircrafts:
        print("Error: No hay vuelos para mostrar")
        return None, None

    # Contar vuelos por aerolínea
    airline_count = {}
    for aircraft in aircrafts:
        if aircraft.airline:
            airline_count[aircraft.airline] = airline_count.get(aircraft.airline, 0) + 1

    # Crear gráfica
    fig, ax = plt.subplots(figsize=(12, 6))
    airlines = list(airline_count.keys())
    counts = list(airline_count.values())

    ax.bar(airlines, counts, color='#2ecc71', edgecolor='black', linewidth=1.5)
    ax.set_xlabel('Aerolínea', fontsize=12)
    ax.set_ylabel('Número de vuelos', fontsize=12)
    ax.set_title('Vuelos por aerolínea que llegan a LEBL', fontsize=14, fontweight='bold')
    ax.tick_params(axis='x', rotation=45)
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    fig.tight_layout()
    return fig, ax


# ===== PLOT FLIGHTS TYPE (SCHENGEN vs NO-SCHENGEN) =====
def PlotFlightsType(aircrafts, airports):
    """Muestra un gráfico apilado de vuelos Schengen vs No-Schengen"""
    if not aircrafts:
        print("Error: No hay vuelos para mostrar")
        return None, None

    # Contar vuelos por tipo
    schengen_count = 0
    non_schengen_count = 0

    for aircraft in aircrafts:
        if IsSchengenAirport(aircraft.origin):
            schengen_count += 1
        else:
            non_schengen_count += 1

    # Crear gráfica
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(['Vuelos'], [schengen_count], label='Schengen', color='#2ecc71', edgecolor='black', linewidth=2)
    ax.bar(['Vuelos'], [non_schengen_count], bottom=[schengen_count], label='No-Schengen',
           color='#e74c3c', edgecolor='black', linewidth=2)

    ax.set_ylabel('Número de vuelos', fontsize=12)
    ax.set_title('Vuelos que llegan a LEBL: Schengen vs No-Schengen', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    # Añadir etiquetas
    ax.text(0, schengen_count / 2, str(schengen_count), ha='center', va='center',
            fontweight='bold', fontsize=12, color='white')
    ax.text(0, schengen_count + non_schengen_count / 2, str(non_schengen_count),
            ha='center', va='center', fontweight='bold', fontsize=12, color='white')

    fig.tight_layout()
    return fig, ax


# ===== MAP FLIGHTS (SIN SIMPLEKML) =====
def MapFlights(aircrafts, airports):
    """Crea un archivo KML con las trayectorias de vuelos (versión sin simplekml)"""
    if not aircrafts:
        print("No hay vuelos para mostrar")
        return None

    # Barcelona coordinates
    lebl_lat = 41.2974
    lebl_lon = 2.0833

    # Crear diccionario de aeropuertos
    airports_dict = {}
    for airport in airports:
        airports_dict[airport.icao_code] = airport

    kml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Flight Trajectories LEBL</name>
    <Style id="schengen">
      <LineStyle>
        <color>ff00ff00</color>
        <width>2</width>
      </LineStyle>
    </Style>
    <Style id="non_schengen">
      <LineStyle>
        <color>ff0000ff</color>
        <width>2</width>
      </LineStyle>
    </Style>
'''

    for aircraft in aircrafts:
        if aircraft.origin in airports_dict:
            origin_airport = airports_dict[aircraft.origin]

            # Determinar estilo
            style_id = "schengen" if origin_airport.schengen else "non_schengen"

            kml_content += f'''    <Placemark>
      <name>{aircraft.aircraft_id} ({aircraft.airline})</name>
      <description>Origin: {aircraft.origin} | Arrival: {aircraft.arrival_time}</description>
      <styleUrl>#{style_id}</styleUrl>
      <LineString>
        <coordinates>
          {origin_airport.longitude},{origin_airport.latitude},0
          {lebl_lon},{lebl_lat},0
        </coordinates>
      </LineString>
    </Placemark>
'''

    kml_content += '''  </Document>
</kml>'''

    # Guardar archivo
    base_dir = os.path.dirname(__file__)
    filepath = os.path.join(base_dir, "flights_map.kml")

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(kml_content)
        print(f"Mapa guardado: {filepath}")
        return filepath
    except Exception as e:
        print(f"Error al guardar mapa: {e}")
        return None


# ===== LONG DISTANCE ARRIVALS =====
def LongDistanceArrivals(aircrafts, airports):
    """Retorna una lista de vuelos que llegan desde más de 2000 km"""
    long_distance = []

    # Barcelona coordinates
    lebl_lat = 41.2974
    lebl_lon = 2.0833

    # Crear diccionario de aeropuertos
    airports_dict = {}
    for airport in airports:
        airports_dict[airport.icao_code] = airport

    for aircraft in aircrafts:
        if aircraft.origin in airports_dict:
            origin_airport = airports_dict[aircraft.origin]
            distance = HaversineDistance(origin_airport.latitude, origin_airport.longitude, lebl_lat, lebl_lon)
            if distance > 2000:
                long_distance.append(aircraft)

    return long_distance


# ===== TEST SECTION =====
if __name__ == "__main__":
    print("=== TEST AIRCRAFT.PY ===\n")

    # Test LoadArrivals
    print("Test 1: Cargar vuelos")
    aircrafts = LoadArrivals("Arrivals.txt")
    print(f"✓ Cargados {len(aircrafts)} vuelos\n")

    if len(aircrafts) > 0:
        print("Primeros 3 vuelos:")
        for i in range(min(3, len(aircrafts))):
            a = aircrafts[i]
            print(f"  {a.aircraft_id} -> {a.origin} ({a.airline}) Llegada: {a.arrival_time}")
        print()

        # Test PlotArrivals
        print("Test 2: Gráfica de frecuencia de llegadas")
        fig, ax = PlotArrivals(aircrafts)
        if fig:
            plt.show()
        print("✓ Gráfica mostrada\n")

        # Test SaveFlights
        print("Test 3: Guardar vuelos")
        result = SaveFlights(aircrafts, "flights_saved.txt")
        print(f"✓ {result} vuelos guardados\n")

        # Test PlotAirlines
        print("Test 4: Gráfica de aerolíneas")
        fig, ax = PlotAirlines(aircrafts)
        if fig:
            plt.show()
        print("✓ Gráfica mostrada\n")