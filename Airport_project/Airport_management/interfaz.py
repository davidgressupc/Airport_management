import tkinter as tk
from tkinter import messagebox, filedialog
from airport import *
from aircraft import *
from LEBL import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ===== VARIABLES GLOBALES =====
airports = []
aircrafts = []
bcn = None  # BarcelonaAP


# ===== FUNCIONES PARA AEROPORTS =====

def load_airports_from_file():
    global airports
    filename = "airports_file.txt"
    airports = LoadAirports(filename)

    if airports:
        messagebox.showinfo("Éxito", f"{len(airports)} aeroports carregats")
    else:
        messagebox.showerror("Error", f"No s'ha trobat el fitxer: {filename}")


def add_airport_manual():
    """Añadir un aeroport manualmente"""
    global airports
    code_entry = entry_code.get()
    try:
        lat = float(entry_lat.get())
        lon = float(entry_lon.get())

        if not code_entry:
            messagebox.showerror("Error", "Codi ICAO requerit")
            return

        new_airport = Airport(code_entry, lat, lon)
        SetSchengen(new_airport)

        if len(code_entry) != 4:
            messagebox.showerror("Error", "Format incorrecte, necessita 4 caràcters")
            return

        if AddAirport(airports, new_airport):
            messagebox.showinfo("Éxit", f"Aeroport {code_entry} afegit")
            entry_code.delete(0, tk.END)
            entry_lat.delete(0, tk.END)
            entry_lon.delete(0, tk.END)
            show_plot_schengen()

        else:
            messagebox.showwarning("Avis", f"L'aeroport {code_entry} ja existeix")
    except ValueError:
        messagebox.showerror("Error", "Latitud i Longitud han de ser nombres")


def delete_airport_action():
    """Eliminar un aeroport"""
    global airports
    code = entry_search.get()
    if not code:
        messagebox.showerror("Error", "Introdueix codi ICAO")
        return

    if RemoveAirport(airports, code) == 0:
        messagebox.showinfo("Éxit", f"Aeroport {code} eliminat")
        entry_search.delete(0, tk.END)
        show_plot_schengen()
    else:
        messagebox.showerror("Error", f"Aeroport {code} no trobat")


def show_airport_data():
    """Mostrar dades de un aeroport"""
    global airports
    code = entry_search.get()
    if not code:
        messagebox.showerror("Error", "Introdueix codi ICAO")
        return

    i = 0
    while i < len(airports):
        a = airports[i]
        if a.icao_code.upper() == code.upper():
            info = f"Codi: {a.icao_code}\nLatitud: {a.latitude:.4f}\nLongitud: {a.longitude:.4f}\nSchengen: {'Sí' if a.schengen else 'No'}"
            messagebox.showinfo("Dades de l'aeroport", info)
            return
        i += 1

    messagebox.showerror("Error", f"Aeroport {code} no trobat")


def show_plot_schengen():
    """Mostrar gràfica Schengen vs No-Schengen"""
    global airports
    if not airports:
        messagebox.showerror("Error", "No hi ha aeroports carregats")
        return

    fig, ax = PlotAirports(airports)

    if fig is None:
        return

    for widget in picture_frame.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=picture_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


def show_google_earth_map():
    global airports
    if not airports:
        messagebox.showerror("Error", "No hi ha aeroports carregats")
        return

    filepath = MapAirports(airports)

    if filepath is None:
        messagebox.showerror("Error", "No s'ha pogut generar el mapa")
        return

    import os
    import subprocess
    try:
        os.startfile(filepath)
    except AttributeError:
        subprocess.Popen(['open', filepath])
    except:
        pass

    messagebox.showinfo("Éxito", f"Mapa obert:\n{filepath}")


def save_schengen_airports():
    """Guardar aeroports Schengen en fichero"""
    global airports
    if not airports:
        messagebox.showerror("Error", "No hi ha aeroports carregats")
        return

    result = SaveSchengenAirports(airports, "schengen_airports.txt")
    if result > 0:
        messagebox.showinfo("Éxito", f"✓ {result} aeroports Schengen guardats en 'schengen_airports.txt'")
    else:
        messagebox.showerror("Error", "No hi ha aeroports Schengen")


# ===== FUNCIONES PARA VUELOS =====

def load_arrivals_from_file():
    global aircrafts
    filename = filedialog.askopenfilename(
        title="Selecciona archivo de vuelos",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )

    if filename:
        aircrafts = LoadArrivals(filename)
        if aircrafts:
            messagebox.showinfo("Éxito", f"{len(aircrafts)} vuelos cargados")
        else:
            messagebox.showerror("Error", "No se pudieron cargar vuelos del archivo")


def plot_arrivals_action():
    """Mostrar gráfica de llegadas por hora"""
    global aircrafts
    if not aircrafts:
        messagebox.showerror("Error", "No hay vuelos cargados")
        return

    fig, ax = PlotArrivals(aircrafts)
    if fig is None:
        return

    for widget in picture_frame.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=picture_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


def plot_airlines_action():
    """Mostrar gráfica de vuelos por aerolínea"""
    global aircrafts
    if not aircrafts:
        messagebox.showerror("Error", "No hay vuelos cargados")
        return

    fig, ax = PlotAirlines(aircrafts)
    if fig is None:
        return

    for widget in picture_frame.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=picture_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


def plot_flights_type_action():
    """Mostrar gráfica Schengen vs No-Schengen"""
    global aircrafts
    if not aircrafts:
        messagebox.showerror("Error", "No hay vuelos cargados")
        return

    fig, ax = PlotFlightsType(aircrafts, airports)
    if fig is None:
        return

    for widget in picture_frame.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=picture_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


def map_flights_action():
    """Mostrar mapa de trayectorias de vuelos"""
    global aircrafts, airports
    if not aircrafts:
        messagebox.showerror("Error", "No hay vuelos cargados")
        return

    if not airports:
        messagebox.showerror("Error", "No hay aeroports cargados")
        return

    filepath = MapFlights(aircrafts, airports)
    if filepath is None:
        messagebox.showerror("Error", "No se pudo generar el mapa")
        return

    import os
    import subprocess
    try:
        os.startfile(filepath)
    except AttributeError:
        subprocess.Popen(['open', filepath])
    except:
        pass

    messagebox.showinfo("Éxito", f"Mapa abierto:\n{filepath}")




def long_distance_action():

    global aircrafts, airports
    if not aircrafts:
        messagebox.showerror("Error", "No hay vuelos cargados")
        return

    if not airports:
        messagebox.showerror("Error", "No hay aeroports cargados")
        return

    long_distance_flights = LongDistanceArrivals(aircrafts, airports)

    if not long_distance_flights:
        messagebox.showinfo("Info", "No hay vuelos de larga distancia (>2000 km)")
        return

    filepath = MapFlights(long_distance_flights, airports)
    if filepath is None:
        messagebox.showerror("Error", "No se pudo generar el mapa")
        return

    import os
    import subprocess
    try:
        os.startfile(filepath)
    except AttributeError:
        subprocess.Popen(['open', filepath])
    except:
        pass

    messagebox.showinfo("Éxito",
                        f"Mapa guardado:\n{filepath}\n({len(long_distance_flights)} vuelos de larga distancia)")

#/////////////////////////////////////////EXAMEN:
def non_schengen_action():

    """Mostrar solo vuelos NO Schengen en Google Earth"""

    global aircrafts, airports

    if not aircrafts or not airports:
        messagebox.showerror("Error", "Faltan datos")
        return

    non_schengen = []

    i = 0
    while i < len(aircrafts):

        j = 0
        found = False

        while j < len(airports) and not found:

            airport = airports[j]

            if airport.icao_code.upper() == aircrafts[i].origin.upper():

                if airport.schengen == False:
                    non_schengen.append(aircrafts[i])

                found = True

            j += 1

        i += 1

    if len(non_schengen) == 0:
        messagebox.showinfo("Info", "No hay vuelos NO Schengen")
        return

    filepath = MapFlights(non_schengen, airports)

    import os
    import subprocess

    try:
        os.startfile(filepath)

    except AttributeError:
        subprocess.Popen(['open', filepath])

    messagebox.showinfo(
        "Éxito",
        f"{len(non_schengen)} vuelos NO Schengen mostrados"
    )
#//////////////////////////////////////////////////////////////////////
def save_flights_action():
    """Guardar vuelos en archivo"""
    global aircrafts
    if not aircrafts:
        messagebox.showerror("Error", "No hay vuelos para guardar")
        return

    filename = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )

    if filename:
        result = SaveFlights(aircrafts, filename)
        if result > 0:
            messagebox.showinfo("Éxito", f"✓ {result} vuelos guardados en '{filename}'")
        else:
            messagebox.showerror("Error", "No se pudieron guardar los vuelos")


# ===== NUEVAS FUNCIONES PARA GATES (VERSIÓN 3) =====

def load_airport_structure():
    """Carga la estructura del aeropuerto (terminales y gates)"""
    global bcn
    filename = filedialog.askopenfilename(
        title="Selecciona archivo de estructura del aeropuerto",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if filename:
        bcn = LoadAirportStructure(filename)
        if bcn:
            # Contar gates totales
            total_gates = 0
            i = 0
            while i < len(bcn.terminals):
                j = 0
                while j < len(bcn.terminals[i].boarding_areas):
                    k = 0
                    while k < len(bcn.terminals[i].boarding_areas[j].gates):
                        total_gates += 1
                        k += 1
                    j += 1
                i += 1

            messagebox.showinfo("Éxito", f"Aeropuerto {bcn.code} cargado\nTotal de gates: {total_gates}")
        else:
            messagebox.showerror("Error", "No se pudo cargar la estructura")


def assign_gates_to_flights():
    """Asigna gates a los vuelos cargados"""
    global bcn, aircrafts
    if not bcn:
        messagebox.showerror("Error", "No hay estructura del aeropuerto cargada")
        return
    if not aircrafts:
        messagebox.showerror("Error", "No hay vuelos cargados")
        return

    assigned = 0
    failed = 0

    i = 0
    while i < len(aircrafts):
        result = AssignGate(bcn, aircrafts[i])
        if result == 0:
            assigned += 1
        else:
            failed += 1
        i += 1

    messagebox.showinfo("Asignación", f"✓ {assigned} vuelos asignados\n✗ {failed} sin gate disponible")


def show_gate_occupancy():
    """Muestra el estado de los gates"""
    global bcn
    if not bcn:
        messagebox.showerror("Error", "No hay estructura del aeropuerto cargada")
        return

    occupancy = GateOccupancy(bcn)

    # Contar gates
    free_gates = 0
    occupied_gates = 0

    i = 0
    while i < len(occupancy):
        if occupancy[i]['status'] == 'Libre':
            free_gates += 1
        else:
            occupied_gates += 1
        i += 1

    messagebox.showinfo("Estado de Gates",
                        f"Gates libres: {free_gates}\n"
                        f"Gates ocupados: {occupied_gates}\n"
                        f"Total: {len(occupancy)}")


def plot_gates_action():
    """Visualiza los gates"""
    global bcn
    if not bcn:
        messagebox.showerror("Error", "No hay estructura del aeropuerto cargada")
        return

    fig, axes = PlotGates(bcn)
    if fig is None:
        return

    for widget in picture_frame.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=picture_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


# ===== CREAR INTERFAZ GRÁFICA =====

root = tk.Tk()
root.geometry("1920x1080")
root.title("Airport Management System v3.0 - UPC Group 9")

# Configurar grid
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=10)
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
root.rowconfigure(2, weight=1)
root.rowconfigure(3, weight=1)
root.rowconfigure(4, weight=2)

# ===== PANEL IZQUIERDO - BOTONES (SCROLLABLE) =====

canvas_left = tk.Canvas(root, bg="#ecf0f1")
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas_left.yview)
scrollable_frame = tk.Frame(canvas_left, bg="#ecf0f1")

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas_left.configure(scrollregion=canvas_left.bbox("all"))
)

canvas_left.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas_left.configure(yscrollcommand=scrollbar.set)

canvas_left.grid(row=0, column=0, rowspan=5, padx=5, pady=5, sticky="nsew")
scrollbar.grid(row=0, column=0, rowspan=5, padx=(0, 5), pady=5, sticky="nse")

# 1. Frame para Cargar Aeroports
file_frame = tk.LabelFrame(scrollable_frame, text="📁 Aeroports", font=("Arial", 11, "bold"))
file_frame.pack(fill="x", padx=5, pady=5)
file_frame.columnconfigure(0, weight=1)

buttonload = tk.Button(file_frame, text="Cargar Aeroports", command=load_airports_from_file,
                       bg="#3498db", fg="white", font=("Arial", 10, "bold"), height=2)
buttonload.pack(fill="both", expand=True, padx=5, pady=5)

button_map_airports = tk.Button(file_frame, text="Mapa Google Earth", command=show_google_earth_map,
                                bg="#f39c12", fg="white", font=("Arial", 10, "bold"), height=2)
button_map_airports.pack(fill="both", expand=True, padx=5, pady=5)

buttonsave = tk.Button(file_frame, text="Guardar Aeroports Schengen", command=save_schengen_airports,
                       bg="#27ae60", fg="white", font=("Arial", 10, "bold"), height=2)
buttonsave.pack(fill="both", expand=True, padx=5, pady=5)

# 2. Frame para Gráficos de Aeroports
graph_frame = tk.LabelFrame(scrollable_frame, text="📊 Gráficos Aeroports", font=("Arial", 11, "bold"))
graph_frame.pack(fill="x", padx=5, pady=5)
graph_frame.columnconfigure(0, weight=1)

button_plot = tk.Button(graph_frame, text="Mostrar Schengen vs No-Schengen", command=show_plot_schengen,
                        bg="#e74c3c", fg="white", font=("Arial", 10, "bold"))
button_plot.pack(fill="x", padx=5, pady=5)

# 3. Frame para Búsqueda/Eliminar Aeroports
search_frame = tk.LabelFrame(scrollable_frame, text="🔍 Buscar/Eliminar Aeroport", font=("Arial", 11, "bold"))
search_frame.pack(fill="x", padx=5, pady=5)
search_frame.columnconfigure(0, weight=1)

tk.Label(search_frame, text="Codi ICAO:", font=("Arial", 9)).pack(anchor="w", padx=5, pady=2)
entry_search = tk.Entry(search_frame, font=("Arial", 10))
entry_search.pack(fill="x", padx=5, pady=2)

button_show = tk.Button(search_frame, text="Ver Dades", command=show_airport_data,
                        bg="#3498db", fg="white", font=("Arial", 9, "bold"))
button_show.pack(fill="x", padx=5, pady=3)

button_delete = tk.Button(search_frame, text="Eliminar Aeroport", command=delete_airport_action,
                          bg="#e74c3c", fg="white", font=("Arial", 9, "bold"))
button_delete.pack(fill="x", padx=5, pady=3)

# 4. Frame para Añadir Aeroport
add_frame = tk.LabelFrame(scrollable_frame, text="➕ Añadir Aeroport", font=("Arial", 11, "bold"))
add_frame.pack(fill="x", padx=5, pady=5)
add_frame.columnconfigure(0, weight=1)

tk.Label(add_frame, text="Codi ICAO:", font=("Arial", 9)).pack(anchor="w", padx=5, pady=2)
entry_code = tk.Entry(add_frame, font=("Arial", 10))
entry_code.pack(fill="x", padx=5, pady=2)

tk.Label(add_frame, text="Latitud:", font=("Arial", 9)).pack(anchor="w", padx=5, pady=2)
entry_lat = tk.Entry(add_frame, font=("Arial", 10))
entry_lat.pack(fill="x", padx=5, pady=2)

tk.Label(add_frame, text="Longitud:", font=("Arial", 9)).pack(anchor="w", padx=5, pady=2)
entry_lon = tk.Entry(add_frame, font=("Arial", 10))
entry_lon.pack(fill="x", padx=5, pady=2)

button_add = tk.Button(add_frame, text="Afegir Aeroport", command=add_airport_manual,
                       bg="#27ae60", fg="white", font=("Arial", 10, "bold"))
button_add.pack(fill="x", padx=5, pady=5)

# 5. Frame para Cargar Vuelos
flights_frame = tk.LabelFrame(scrollable_frame, text="✈️ Vuelos", font=("Arial", 11, "bold"))
flights_frame.pack(fill="x", padx=5, pady=5)
flights_frame.columnconfigure(0, weight=1)

button_load_flights = tk.Button(flights_frame, text="Cargar Vuelos", command=load_arrivals_from_file,
                                bg="#9b59b6", fg="white", font=("Arial", 10, "bold"), height=2)
button_load_flights.pack(fill="both", expand=True, padx=5, pady=5)

button_save_flights = tk.Button(flights_frame, text="Guardar Vuelos", command=save_flights_action,
                                bg="#16a085", fg="white", font=("Arial", 10, "bold"), height=2)
button_save_flights.pack(fill="both", expand=True, padx=5, pady=5)

# 6. Frame para Gráficos de Vuelos
graph_flights_frame = tk.LabelFrame(scrollable_frame, text="📊 Gráficos Vuelos", font=("Arial", 11, "bold"))
graph_flights_frame.pack(fill="x", padx=5, pady=5)
graph_flights_frame.columnconfigure(0, weight=1)

button_plot_arrivals = tk.Button(graph_flights_frame, text="Llegadas por Hora", command=plot_arrivals_action,
                                 bg="#e67e22", fg="white", font=("Arial", 9, "bold"))
button_plot_arrivals.pack(fill="x", padx=5, pady=3)

button_plot_airlines = tk.Button(graph_flights_frame, text="Vuelos por Aerolínea", command=plot_airlines_action,
                                 bg="#c0392b", fg="white", font=("Arial", 9, "bold"))
button_plot_airlines.pack(fill="x", padx=5, pady=3)

button_plot_type = tk.Button(graph_flights_frame, text="Vuelos Schengen vs No", command=plot_flights_type_action,
                             bg="#27ae60", fg="white", font=("Arial", 9, "bold"))
button_plot_type.pack(fill="x", padx=5, pady=3)

button_map = tk.Button(graph_flights_frame, text="Mapa Trayectorias", command=map_flights_action,
                       bg="#3498db", fg="white", font=("Arial", 9, "bold"))
button_map.pack(fill="x", padx=5, pady=3)

button_long_dist = tk.Button(graph_flights_frame, text="Larga Distancia >2000km", command=long_distance_action,
                             bg="#f39c12", fg="white", font=("Arial", 9, "bold"))
button_long_dist.pack(fill="x", padx=5, pady=3)
#EXÁMEN: ///////////////////////////////////////////7777777777777
button_non_schengen = tk.Button(
    graph_flights_frame,
    text="Mapa vuelos NO Schengen",
    command=non_schengen_action,
    bg="#8e44ad",
    fg="white",
    font=("Arial", 9, "bold")
)

button_non_schengen.pack(fill="x", padx=5, pady=3)
#///////////////////////////////////777
# 7. NUEVO - Gestión de Gates (VERSIÓN 3)
gates_frame = tk.LabelFrame(scrollable_frame, text="🚪 Gestión de Gates V3", font=("Arial", 11, "bold"))
gates_frame.pack(fill="x", padx=5, pady=5)
gates_frame.columnconfigure(0, weight=1)

button_load_structure = tk.Button(gates_frame, text="Cargar Estructura LEBL", command=load_airport_structure,
                                  bg="#8e44ad", fg="white", font=("Arial", 10, "bold"), height=2)
button_load_structure.pack(fill="both", expand=True, padx=5, pady=5)

button_assign_gates = tk.Button(gates_frame, text="Asignar Gates a Vuelos", command=assign_gates_to_flights,
                                bg="#d35400", fg="white", font=("Arial", 10, "bold"), height=2)
button_assign_gates.pack(fill="both", expand=True, padx=5, pady=5)

button_gate_status = tk.Button(gates_frame, text="Ver Estado de Gates", command=show_gate_occupancy,
                               bg="#2980b9", fg="white", font=("Arial", 10, "bold"))
button_gate_status.pack(fill="x", padx=5, pady=3)

button_plot_gates = tk.Button(gates_frame, text="Visualizar Gates", command=plot_gates_action,
                              bg="#16a085", fg="white", font=("Arial", 10, "bold"))
button_plot_gates.pack(fill="x", padx=5, pady=3)

# ===== PANEL DERECHO - VISUALIZACIÓN =====

picture_frame = tk.LabelFrame(root, text="📈 Visualización", font=("Arial", 11, "bold"))
picture_frame.grid(row=0, column=1, rowspan=5, padx=5, pady=5, sticky="nsew")
picture_frame.rowconfigure(0, weight=1)
picture_frame.columnconfigure(0, weight=1)

initial_label = tk.Label(picture_frame, text="Selecciona una opción para visualizar",
                         font=("Arial", 12), fg="#7f8c8d")
initial_label.pack(expand=True)

# Abrir ventana
root.mainloop()

