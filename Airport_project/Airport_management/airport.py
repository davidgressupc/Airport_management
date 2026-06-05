import matplotlib.pyplot as plt
import os

class Airport:
    def __init__(self, icao_code, latitude, longitude):
        self.icao_code = icao_code
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.schengen = False


#comprobar si un aeroport és shengen pel file
def IsSchengenAirport(code):
    if not code or len(code) < 2:
        return False
    schengen_prefixes = {
        'LO', 'EB', 'LK', 'LC', 'EK', 'EE', 'EF', 'LF', 'ED', 'LG',
        'EH', 'LH', 'BI', 'LI', 'EV', 'EY', 'EL', 'LM', 'EN', 'EP',
        'LP', 'LZ', 'LJ', 'LE', 'ES', 'LS'}
    return code[:2].upper() in schengen_prefixes


#estbleix un aeroport com a shengen
def SetSchengen(airport):
    airport.schengen = IsSchengenAirport(airport.icao_code)

#busca dades aeroport
def PrintAirport(airport):
    print(
        f"Codi: {airport.icao_code} | Lat: {airport.latitude:.4f} | Lon: {airport.longitude:.4f} | Schengen: {airport.schengen}")


#converteix coordenades de minuts a decimal
def ParseCoordinate(coord_str):
    direction = coord_str[0]
    seconds = float(coord_str[-2:])
    minutes = float(coord_str[-4:-2])
    degrees = float(coord_str[1:-4])

    decimal = degrees + minutes / 60 + seconds / 3600
    if direction == 'S' or direction == 'W':
        decimal = -decimal
    return decimal

#carregar aeroports del fitxer airports.txt
def LoadAirports(airports_file):
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
    if not airports:
        return -1

    schengen = [a for a in airports if a.schengen]

    if not schengen:
        return -1

    with open(filename, 'w') as f:
        f.write("CODE LAT LON\n")
        i = 0
        while i < len(schengen):
            a = schengen[i]
            f.write(f"{a.icao_code} {a.latitude} {a.longitude}\n")
            i += 1

    return len(schengen)

#per afegir un aeroport
def AddAirport(airports, airport):

    i = 0
    while i < len(airports):
        a = airports[i]
        if a.icao_code.upper() == airport.icao_code.upper():
            return False
        i += 1
    airports.append(airport)
    return True

#elimina aeroport de la llista
def RemoveAirport(airports, code):
    i = 0
    while i < len(airports):
        a = airports[i]
        if a.icao_code.upper() == code.upper():
            del airports[i]
            return 0
        i += 1
    return -1

#ploteja aeroports shengen vs no shengen
def PlotAirports(airports):
    if not airports:
        print(" No hi ha aeroports per mostrar")
        return None, None

    schengen_count = sum(1 for a in airports if a.schengen)
    non_schengen_count = len(airports) - schengen_count

    # Creem la gràfica
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(['Schengen', 'No Schengen'], [schengen_count, non_schengen_count],
            color=['#2ecc71', '#e74c3c'], width=0.5, edgecolor='black', linewidth=2)
    ax.set_ylabel('Nombre d\'aeroports', fontsize=12)
    ax.set_title('Aeroports Schengen vs No Schengen', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    i = 0
    counts = [schengen_count, non_schengen_count]
    while i < len(counts):
        v = counts[i]
        ax.text(i, v + 1, str(v), ha='center', fontweight='bold', fontsize=11)
        i += 1

    fig.tight_layout()
    return fig, ax

import simplekml
import os

#crear el mapa dels aeroports
def MapAirports(airports):

    if not airports:
        print("No hi ha aeroports per mostrar")
        return None

    kml = simplekml.Kml()

    i = 0
    while i < len(airports):
        airport = airports[i]

        point = kml.newpoint(
            name=airport.icao_code,
            description=(
                f"Schengen: {'SI' if airport.schengen else 'NO'}\n"
                f"Lat: {airport.latitude}\n"
                f"Lon: {airport.longitude}"
            ),
            coords=[(airport.longitude, airport.latitude)]
        )

        if airport.schengen:
            point.style.iconstyle.color = simplekml.Color.green
        else:
            point.style.iconstyle.color = simplekml.Color.red

        i += 1

    base_dir = os.path.dirname(__file__)
    filepath = os.path.join(base_dir, "airports_map.kml")

    kml.save(filepath)

    print(f"Mapa guardat: {filepath} (Obrir amb Google Earth)")

    return filepath