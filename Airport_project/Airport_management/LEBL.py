import matplotlib.pyplot as plt
import matplotlib.patches as patches
import copy
from airport import IsSchengenAirport
from aircraft import Aircraft

# ===== CLASES =====

class Gate:
    def __init__(self, name):
        self.name = name
        self.occupied = False
        self.aircraft_id = None


class BoardingArea:
    def __init__(self, name):
        self.name = name
        self.area_type = None  # "Schengen" o "non-Schengen"
        self.gates = []


class Terminal:
    def __init__(self, name):
        self.name = name
        self.boarding_areas = []
        self.airlines = []


class BarcelonaAP:
    def __init__(self, code):
        self.code = code
        self.terminals = []


# ===== FUNCIONES AUXILIARES =====

def TimeToMinutes(time_str):
    """Convierte un string de hora HH:MM a minutos totales desde las 00:00"""
    if not time_str or ':' not in time_str:
        return 0
    parts = time_str.split(':')
    return int(parts[0]) * 60 + int(parts[1])


# ===== SET GATES =====

def SetGates(area, init_gate, end_gate, prefix):
    """Asigna gates a un boarding area"""
    if end_gate < init_gate:
        return -1

    area.gates = []
    i = init_gate
    while i <= end_gate:
        gate_name = f"{prefix}G{i}" ##########3
        gate = Gate(gate_name)
        area.gates.append(gate)
        i += 1

    return len(area.gates)


# ===== LOAD AIRLINES =====

def LoadAirlines(terminal, t_name):
    """Carga aerolíneas de un archivo"""
    filename = f"{t_name}_Airlines.txt"
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            terminal.airlines = []
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if line:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        airline_code = parts[1].strip()
                        terminal.airlines.append(airline_code)
                    elif len(parts) == 1:
                        terminal.airlines.append(parts[0].strip())
                i += 1

        return len(terminal.airlines)
    except FileNotFoundError:
        print(f"Archivo {filename} no encontrado")
        return -1
    except Exception as e:
        print(f"Error cargando aerolíneas: {e}")
        return -1


# ===== LOAD AIRPORT STRUCTURE =====

def LoadAirportStructure(filename):
    """Carga la estructura del aeropuerto desde un archivo"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if len(lines) < 1:
            print("Archivo vacío")
            return None

        first_line = lines[0].strip().split()
        code = first_line[0]
        num_terminals = int(first_line[1])

        bcn = BarcelonaAP(code)

        line_idx = 1
        t = 0
        while t < num_terminals and line_idx < len(lines):
            terminal_line = lines[line_idx].strip().split()
            terminal_name = terminal_line[1]
            num_areas = int(terminal_line[2])

            terminal = Terminal(terminal_name)
            LoadAirlines(terminal, terminal_name)

            line_idx += 1
            a = 0
            while a < num_areas and line_idx < len(lines):
                area_line = lines[line_idx].strip()
                area_parts = area_line.split()

                area_name = area_parts[1]
                area_type = area_parts[2]
                init_gate = int(area_parts[4])
                end_gate = int(area_parts[6])

                prefix = f"{terminal_name}{area_name}"
                area = BoardingArea(area_name)
                area.area_type = area_type
                SetGates(area, init_gate, end_gate, prefix)

                terminal.boarding_areas.append(area)

                line_idx += 1
                a += 1

            bcn.terminals.append(terminal)
            t += 1

        return bcn

    except FileNotFoundError:
        print(f"Error: Archivo '{filename}' no encontrado")
        return None
    except ValueError as e:
        print(f"Error de valor: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


# ===== IS AIRLINE IN TERMINAL =====

def IsAirlineInTerminal(terminal, name):
    """Verifica si una aerolínea está en el terminal"""
    if not name or len(name) == 0:
        return False

    if not terminal.airlines:
        return False

    i = 0
    while i < len(terminal.airlines):
        if terminal.airlines[i] == name:
            return True
        i += 1

    return False


# ===== SEARCH TERMINAL =====

def SearchTerminal(bcn, airline_code):
    """Busca en qué terminal está una aerolínea"""
    if not airline_code or len(airline_code) == 0:
        return ""

    i = 0
    while i < len(bcn.terminals):
        terminal = bcn.terminals[i]
        if IsAirlineInTerminal(terminal, airline_code):
            return terminal.name
        i += 1

    return ""


# ===== ASSIGN GATE =====

def AssignGate(bcn, aircraft):
    """Asigna un gate a un vuelo basado en aerolínea y origen Schengen/no-Schengen"""

    if not aircraft.airline or len(aircraft.airline) == 0:
        return -1

    terminal_name = SearchTerminal(bcn, aircraft.airline)
    if not terminal_name:
        return -1

    terminal = None
    i = 0
    while i < len(bcn.terminals):
        if bcn.terminals[i].name == terminal_name:
            terminal = bcn.terminals[i]
            break
        i += 1

    if not terminal:
        return -1

    is_schengen = IsSchengenAirport(aircraft.origin) if aircraft.origin else True
    required_type = "Schengen" if is_schengen else "non-Schengen"

    i = 0
    while i < len(terminal.boarding_areas):
        area = terminal.boarding_areas[i]

        if area.area_type == required_type:
            j = 0
            while j < len(area.gates):
                gate = area.gates[j]
                if not gate.occupied:
                    gate.occupied = True
                    gate.aircraft_id = aircraft.aircraft_id
                    return 0
                j += 1

        i += 1

    return -1


# ===== GATE OCCUPANCY =====

def GateOccupancy(bcn):
    """Retorna lista con estado de gates"""
    occupancy_list = []

    i = 0
    while i < len(bcn.terminals):
        terminal = bcn.terminals[i]

        j = 0
        while j < len(terminal.boarding_areas):
            area = terminal.boarding_areas[j]

            k = 0
            while k < len(area.gates):
                gate = area.gates[k]
                status = "Libre" if not gate.occupied else "Ocupado"
                aircraft_id = gate.aircraft_id if gate.occupied else "-"

                occupancy_list.append({
                    'terminal': terminal.name,
                    'area': area.name,
                    'gate': gate.name,
                    'status': status,
                    'aircraft': aircraft_id
                })

                k += 1

            j += 1

        i += 1

    return occupancy_list


# ===== FREE GATE (V4) =====

def FreeGate(bcn, aircraft_id):
    """Libera el gate ocupado por un avión (V4)"""
    if not aircraft_id:
        return -1

    i = 0
    while i < len(bcn.terminals):
        terminal = bcn.terminals[i]

        j = 0
        while j < len(terminal.boarding_areas):
            area = terminal.boarding_areas[j]

            k = 0
            while k < len(area.gates):
                gate = area.gates[k]
                if gate.occupied and gate.aircraft_id == aircraft_id:
                    gate.occupied = False
                    gate.aircraft_id = None
                    return 0
                k += 1

            j += 1

        i += 1

    return -1


# ===== ASSIGN NIGHT GATES (V4) =====

def AssignNightGates(bcn, aircrafts):
    """Asigna gates a aviones nocturnos (solo salida) (V4)"""
    if not aircrafts:
        return -1

    assigned = 0
    i = 0
    while i < len(aircrafts):
        aircraft = aircrafts[i]

        if not aircraft.arrival_time and aircraft.departure_time:
            result = AssignGate(bcn, aircraft)
            if result == 0:
                assigned += 1

        i += 1

    return assigned


# ===== ASSIGN GATES AT TIME (V4) =====

def AssignGatesAtTime(bcn, aircrafts, time_hour):
    """Asigna gates dinámicamente en un periodo horario (V4)"""

    try:
        hour = int(time_hour.split(':')[0]) if ':' in time_hour else int(time_hour)
    except:
        return -1

    i = 0
    while i < len(aircrafts):
        aircraft = aircrafts[i]
        if aircraft.departure_time:
            dep_time = TimeToMinutes(aircraft.departure_time)
            hour_start = hour * 60

            if dep_time >= hour_start and dep_time < hour_start + 60:
                FreeGate(bcn, aircraft.aircraft_id)

        i += 1

    unassigned = 0
    i = 0
    while i < len(aircrafts):
        aircraft = aircrafts[i]
        if aircraft.arrival_time:
            arr_time = TimeToMinutes(aircraft.arrival_time)
            hour_start = hour * 60

            if arr_time >= hour_start and arr_time < hour_start + 60:
                result = AssignGate(bcn, aircraft)
                if result != 0:
                    unassigned += 1

        i += 1

    return unassigned


# ===== PLOT GATES =====

def PlotGates(bcn):
    """Visualiza los gates del aeropuerto"""
    if not bcn or not bcn.terminals:
        print("Error: No hay estructura de aeropuerto")
        return None, None

    fig, axes = plt.subplots(1, len(bcn.terminals), figsize=(18, 10), facecolor="#ffffff")

    if len(bcn.terminals) == 1:
        axes = [axes]

    t = 0
    while t < len(bcn.terminals):
        terminal = bcn.terminals[t]
        ax = axes[t]

        total_height = len(terminal.boarding_areas) * 3.5

        ax.set_title(f"Terminal {terminal.name}", fontsize=14, fontweight='bold')
        ax.set_xlim(-1.5, 11)
        ax.set_ylim(0, total_height)
        ax.axis('off')

        y_pos = total_height - 1

        a = 0
        while a < len(terminal.boarding_areas):
            area = terminal.boarding_areas[a]

            ax.text(-1.2, y_pos, f"{area.name} ({area.area_type})",
                    fontsize=11, fontweight='bold', color='white')
            y_pos -= 0.7

            x_pos = 0
            max_x = 10
            g = 0

            while g < len(area.gates):
                gate = area.gates[g]

                if gate.occupied:
                    color = '#e74c3c'
                else:
                    color = '#2ecc71'

                rect = patches.Rectangle((x_pos, y_pos - 0.45), 0.9, 0.4,
                                         linewidth=1.5, edgecolor='#34495e',
                                         facecolor=color, alpha=0.8)
                ax.add_patch(rect)

                gate_number = gate.name.split('G')[1] if 'G' in gate.name else str(g + 1)
                label = gate_number if not gate.occupied else gate.aircraft_id[:3]

                ax.text(x_pos + 0.45, y_pos - 0.25, label, ha='center', va='center',
                        fontsize=8, fontweight='bold', color='white')

                x_pos += 1.0

                if x_pos > max_x:
                    x_pos = 0
                    y_pos -= 0.6

                g += 1

            y_pos -= 1.2
            a += 1

        t += 1

    plt.tight_layout()
    return fig, axes


# ===== PLOT DAY OCCUPANCY (V4) =====

def PlotDayOccupancy(bcn, aircrafts):
    """Gráfica de ocupación de gates por hora del día (V4)"""

    if not bcn or not aircrafts:
        print("Error: No hay datos para la gráfica")
        return None, None

    hours_data = []

    h = 0
    while h < 24:
        bcn_copy = copy.deepcopy(bcn)

        unassigned = AssignGatesAtTime(bcn_copy, aircrafts, f"{h}:00")

        occupancy = GateOccupancy(bcn_copy)
        occupied_count = 0
        i = 0
        while i < len(occupancy):
            if occupancy[i]['status'] == 'Ocupado':
                occupied_count += 1
            i += 1

        hours_data.append({
            'hour': h,
            'occupied': occupied_count,
            'unassigned': unassigned
        })

        h += 1

    fig, ax = plt.subplots(figsize=(14, 6))

    hours_list = []
    occupied_list = []
    unassigned_list = []

    i = 0
    while i < len(hours_data):
        hours_list.append(f"{hours_data[i]['hour']}:00")
        occupied_list.append(hours_data[i]['occupied'])
        unassigned_list.append(hours_data[i]['unassigned'])
        i += 1

    x = list(range(len(hours_list)))
    width = 0.35

    ax.bar([xi - width / 2 for xi in x], occupied_list, width, label='Gates Ocupados',
           color='#e74c3c', edgecolor='black', linewidth=1.5)
    ax.bar([xi + width / 2 for xi in x], unassigned_list, width, label='Vuelos sin Gate',
           color='#f39c12', edgecolor='black', linewidth=1.5)

    ax.set_xlabel('Hora del día', fontsize=12, fontweight='bold')
    ax.set_ylabel('Número', fontsize=12, fontweight='bold')
    ax.set_title('Ocupación de Gates por Hora (LEBL)', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(hours_list)
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3)

    plt.xticks(rotation=45)
    fig.tight_layout()

    return fig, ax


# =====================================================================
# ===== NUEVAS FUNCIONES COMPLEMENTARIAS (VERSIÓN 4) =====
# =====================================================================
def LoadDepartures(filename):
    """Carga los vuelos de salida desde el archivo de texto (V4) - Corregido para 4 columnas"""
    departures_list = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line:
                parts = line.split()

                if len(parts) == 4:
                    vuelo = Aircraft(parts[0], parts[3], None, parts[1])
                    vuelo.departure_time = parts[2]
                    vuelo.arrival_time = None
                    departures_list.append(vuelo)
            i += 1
        return departures_list
    except Exception as e:
        print(f"Error al leer: {e}")
        return []

def MergeMovements(aircrafts, departures):
    """Fusiona las listas de llegadas (aircrafts) y salidas (departures) V4"""
    merged_aircrafts = []

    i = 0
    while i < len(aircrafts):
        merged_aircrafts.append(aircrafts[i])
        i += 1

    j = 0
    while j < len(departures):
        merged_aircrafts.append(departures[j])
        j += 1

    status = 0
    return merged_aircrafts, status


def NightAircraft(merged_aircrafts):
    """Filtra y extrae los aviones que operan en horario nocturno (23:00 a 06:00) V4"""
    night_aircrafts = []

    i = 0
    while i < len(merged_aircrafts):
        ac = merged_aircrafts[i]
        is_night = False

        if hasattr(ac, 'aircraft_id') and ac.aircraft_id == "AIRCRAFT":
            i += 1
            continue

        if hasattr(ac, 'arrival_time') and ac.arrival_time:
            hour = int(ac.arrival_time.split(':')[0])
            if hour >= 23 or hour < 6:
                is_night = True

        if hasattr(ac, 'departure_time') and ac.departure_time:
            hour = int(ac.departure_time.split(':')[0])
            if hour >= 23 or hour < 6:
                is_night = True

        if is_night:
            night_aircrafts.append(ac)

        i += 1

    status = 0
    return night_aircrafts, status