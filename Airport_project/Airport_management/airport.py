import matplotlib.pyplot as plt
import os


class Airport:
    def __init__(self, icao_code, latitude, longitude):
        self.icao_code = icao_code
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.schengen = False


# ===== STEP 1 =====
def IsSchengenAirport(code):
    """Comprova si un aeroport és Schengen per el codi ICAO"""
    if not code or len(code) < 2:
        return False
    schengen_prefixes = {
        'LO', 'EB', 'LK', 'LC', 'EK', 'EE', 'EF', 'LF', 'ED', 'LG',
        'EH', 'LH', 'BI', 'LI', 'EV', 'EY', 'EL', 'LM', 'EN', 'EP',
        'LP', 'LZ', 'LJ', 'LE', 'ES', 'LS'}
    return code[:2].upper() in schengen_prefixes #TODO: Canviar per un while


def SetSchengen(airport):
    """Estableix si l'aeroport és Schengen"""
    airport.schengen = IsSchengenAirport(airport.icao_code)


def PrintAirport(airport):
    """Mostra les dades de l'aeroport"""
    print(
        f"Codi: {airport.icao_code} | Lat: {airport.latitude:.4f} | Lon: {airport.longitude:.4f} | Schengen: {airport.schengen}")


# ===== STEP 3 =====
def ParseCoordinate(coord_str):
    """Converteix DMS (DDMMSS) a decimal"""
    direction = coord_str[0]
    seconds = float(coord_str[-2:])
    minutes = float(coord_str[-4:-2])
    degrees = float(coord_str[1:-4])

    decimal = degrees + minutes / 60 + seconds / 3600
    if direction in ['S', 'W']:#TODO: remove in
        decimal = -decimal
    return decimal


def LoadAirports(airports_file):
    """Carrega aeroports del fitxer"""
    airports = []
    try:
        with open(airports_file, 'r') as f:
            lines = f.readlines()
            for line in lines[1:]:
                parts = line.strip().split()
                if len(parts) == 3:
                    lat = ParseCoordinate(parts[1])
                    lng = ParseCoordinate(parts[2])
                    ap = Airport(parts[0], lat, lng)
                    SetSchengen(ap)
                    airports.append(ap)
    except FileNotFoundError:
        print(f"Error: Fitxer '{airports_file}' no trobat")
        return []
    return airports


def SaveSchengenAirports(airports, filename):
    """Guarda només els aeroports Schengen"""
    if not airports:
        return -1

    schengen = [a for a in airports if a.schengen]###################

    if not schengen:
        return -1

    with open(filename, 'w') as f:
        f.write("CODE LAT LON\n")
        for a in schengen:
            f.write(f"{a.icao_code} {a.latitude} {a.longitude}\n")

    return len(schengen)


def AddAirport(airports, airport):
    """Afegeix un aeroport a la llista"""
    for a in airports:
        if a.icao_code.upper() == airport.icao_code.upper():
            return False
    airports.append(airport)
    return True


def RemoveAirport(airports, code):
    """Elimina un aeroport per codi"""
    for i, a in enumerate(airports):   ##########WHILEE
        if a.icao_code.upper() == code.upper():
            del airports[i]
            return 0
    return -1


# ===== STEP 5 - GRÀFICS FÀCILS =====
def PlotAirports(airports):
    """Mostra una gràfica de barres Schengen vs No-Schengen"""
    if not airports:
        print(" No hi ha aeroports per mostrar")
        return

    # Comptem
    schengen_count = sum(1 for a in airports if a.schengen)
    non_schengen_count = len(airports) - schengen_count

    # Creem la gràfica
    fig1 = plt.figure(figsize=(8, 6))
    fig1 = plt.bar(['Schengen', 'No Schengen'], [schengen_count, non_schengen_count],
            color=['#2ecc71', '#e74c3c'], width=0.5, edgecolor='black', linewidth=2)
    fig1.ylabel('Nombre d\'aeroports', fontsize=12)
    fig1.title('Aeroports Schengen vs No Schengen', fontsize=14, fontweight='bold')
    fig1.grid(axis='y', alpha=0.3, linestyle='--')

    # Afegim etiquetes a les barres
    for i, v in enumerate([schengen_count, non_schengen_count]):
        plt.text(i, v + 1, str(v), ha='center', fontweight='bold', fontsize=11)

    fig1.tight_layout()
    return fig1


def MapAirports(airports):
    """Crea un mapa KML per Google Earth (aeroports colorejats)"""
    if not airports:
        print(" No hi ha aeroports per mostrar")
        return

    try:
        import simplekml
    except ImportError:
        print(" simplekml no instal·lat. Executa: pip install simplekml")
        return

    kml = simplekml.Kml()

    # Afegim cada aeroport
    for airport in airports:
        # Aeroports Schengen = VERD
        if airport.schengen:
            point = kml.newpoint(
                name=airport.icao_code,
                description=f"Schengen: SI\nLat: {airport.latitude}\nLon: {airport.longitude}",
                coords=[(airport.longitude, airport.latitude)]
            )
            point.style.iconstyle.color = simplekml.Color.green
        # No Schengen = VERMELL
        else:
            point = kml.newpoint(
                name=airport.icao_code,
                description=f"Schengen: NO\nLat: {airport.latitude}\nLon: {airport.longitude}",
                coords=[(airport.longitude, airport.latitude)]
            )
            point.style.iconstyle.color = simplekml.Color.red

    kml.save("airports_map.kml")
    print("Mapa guardat: 'airports_map.kml' (Obrir amb Google Earth)")