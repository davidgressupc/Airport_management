import matplotlib.pyplot as plt
import matplotlib.patches as patches
from aircraft import Aircraft
from airport import IsSchengenAirport


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


# ===== SET GATES =====
def SetGates(area, init_gate, end_gate, prefix):
    """Asigna gates a un boarding area"""
    if end_gate < init_gate:
        return -1

    area.gates = []
    i = init_gate
    while i <= end_gate:
        gate_name = f"{prefix}G{i}"
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

        # Primera línea: "LEBL 2 terminals"
        first_line = lines[0].strip().split()
        code = first_line[0]
        num_terminals = int(first_line[1])

        bcn = BarcelonaAP(code)

        line_idx = 1
        t = 0
        while t < num_terminals and line_idx < len(lines):
            # Línea de terminal: "Terminal T1 5 boarding areas"
            terminal_line = lines[line_idx].strip().split()
            terminal_name = terminal_line[1]  # T1 o T2
            num_areas = int(terminal_line[2])

            terminal = Terminal(terminal_name)

            # Cargar aerolíneas
            LoadAirlines(terminal, terminal_name)

            line_idx += 1
            a = 0
            while a < num_areas and line_idx < len(lines):
                # Línea de boarding area: "Area A Schengen Gates 1 - 11"
                area_line = lines[line_idx].strip()
                area_parts = area_line.split()

                area_name = area_parts[1]  # A, B, C, M, R, etc.
                area_type = area_parts[2]  # Schengen o non-Schengen
                # area_parts[3] es "Gates"
                init_gate = int(area_parts[4])
                # area_parts[5] es "-"
                end_gate = int(area_parts[6])

                # Crear prefix (ej: T1A, T2M)
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
    """Verifica si una aerolínea está en la terminal"""
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
    """Asigna un gate a un vuelo"""
    # Buscar terminal de la aerolínea
    terminal_name = SearchTerminal(bcn, aircraft.airline)
    if not terminal_name:
        return -1

    # Buscar terminal
    terminal = None
    i = 0
    while i < len(bcn.terminals):
        if bcn.terminals[i].name == terminal_name:
            terminal = bcn.terminals[i]
            break
        i += 1

    if not terminal:
        return -1

    # Determinar tipo de boarding area (Schengen o no)
    is_schengen = IsSchengenAirport(aircraft.origin)
    required_type = "Schengen" if is_schengen else "non-Schengen"

    # Buscar gate libre
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


# ===== PLOT GATES =====
def PlotGates(bcn):
    """Visualiza los gates del aeropuerto"""
    if not bcn or not bcn.terminals:
        print("Error: No hay estructura de aeropuerto")
        return None, None

    fig, axes = plt.subplots(1, len(bcn.terminals), figsize=(15, 6))

    if len(bcn.terminals) == 1:
        axes = [axes]

    t = 0
    while t < len(bcn.terminals):
        terminal = bcn.terminals[t]
        ax = axes[t]

        ax.set_title(f"Terminal {terminal.name}", fontsize=14, fontweight='bold')
        ax.set_xlim(-0.5, 10)
        ax.set_ylim(-0.5, len(terminal.boarding_areas) * 3)
        ax.axis('off')

        y_pos = len(terminal.boarding_areas) * 3 - 1

        a = 0
        while a < len(terminal.boarding_areas):
            area = terminal.boarding_areas[a]

            # Título del área
            ax.text(-0.3, y_pos, f"{area.name} ({area.area_type})",
                    fontsize=10, fontweight='bold')
            y_pos -= 0.7

            # Gates
            x_pos = 0
            g = 0
            while g < len(area.gates):
                gate = area.gates[g]

                # Color según ocupación
                color = '#e74c3c' if gate.occupied else '#2ecc71'

                rect = patches.Rectangle((x_pos, y_pos - 0.5), 0.8, 0.4,
                                         linewidth=1, edgecolor='black',
                                         facecolor=color, alpha=0.7)
                ax.add_patch(rect)

                # Etiqueta
                label = f"G{g + 1}" if not gate.occupied else gate.aircraft_id[:3]
                ax.text(x_pos + 0.4, y_pos - 0.3, label, ha='center', va='center',
                        fontsize=8, fontweight='bold', color='white')

                x_pos += 1
                if x_pos > 9:
                    x_pos = 0
                    y_pos -= 0.7

                g += 1

            y_pos -= 1.5
            a += 1

        t += 1

    plt.tight_layout()
    return fig, axes


# ===== TEST SECTION =====
if __name__ == "__main__":
    print("=== TEST LEBL.PY ===\n")

    print("Test 1: Cargar estructura del aeropuerto")
    bcn = LoadAirportStructure("Terminals.txt")

    if bcn:
        print(f"✓ Aeropuerto {bcn.code} cargado")
        print(f"✓ Terminales: {len(bcn.terminals)}\n")

        i = 0
        while i < len(bcn.terminals):
            terminal = bcn.terminals[i]
            print(f"Terminal {terminal.name}:")
            print(f"  Aerolíneas: {len(terminal.airlines)}")
            print(f"  Boarding Areas: {len(terminal.boarding_areas)}")

            j = 0
            while j < len(terminal.boarding_areas):
                area = terminal.boarding_areas[j]
                print(f"    - {area.name} ({area.area_type}): {len(area.gates)} gates")
                j += 1

            i += 1

        print("\nTest 2: Asignar gates a vuelos")
        test_flight1 = Aircraft("ECMKV", "VLG", "LYBE", "00:04")
        test_flight2 = Aircraft("EIDPG", "RYR", "LEPA", "04:57")

        result1 = AssignGate(bcn, test_flight1)
        result2 = AssignGate(bcn, test_flight2)

        print(f"✓ Vuelo ECMKV asignado: {'OK' if result1 == 0 else 'ERROR'}")
        print(f"✓ Vuelo EIDPG asignado: {'OK' if result2 == 0 else 'ERROR'}\n")

        print("Test 3: Estado de gates")
        occupancy = GateOccupancy(bcn)
        print(f"✓ Total de gates: {len(occupancy)}")

        occupied = 0
        free = 0
        i = 0
        while i < len(occupancy):
            if occupancy[i]['status'] == 'Ocupado':
                occupied += 1
            else:
                free += 1
            i += 1

        print(f"✓ Gates libres: {free}")
        print(f"✓ Gates ocupados: {occupied}\n")

        print("Test 4: Visualizar gates")
        fig, axes = PlotGates(bcn)
        if fig:
            print("✓ Gráfica generada correctamente")
            plt.show()
    else:
        print("✗ Error al cargar el aeropuerto")


