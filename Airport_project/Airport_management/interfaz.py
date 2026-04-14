import tkinter as tk
from tkinter import messagebox, filedialog
from airport import *
from aircraft import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ===== VARIABLES GLOBALES =====
airports = []
aircrafts = []


# ===== FUNCIONES PARA CARGAR AEROPORTS =====

def load_airports_from_file():
    global airports
    filename = "airports_file.txt"
    airports = LoadAirports(filename)

    if airports:
        messagebox.showinfo("Éxito", f"{len(airports)} aeroports carregats")
    else:
        messagebox.showerror("Error", f"No s'ha trobat el fitxer: {filename}")


# ===== FUNCIONES PARA CARGAR VUELOS =====

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


# ===== FUNCIONES PARA GRÁFICOS DE VUELOS =====

def plot_arrivals_action():
    """Mostrar gráfica de llegadas por hora"""
    global aircrafts
    if not aircrafts:
        messagebox.showerror("Error", "No hay vuelos cargados")
        return

    fig, ax = PlotArrivals(aircrafts)
    if fig is None:
        return

    # Mostrar en interfaz
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

    # Mostrar en interfaz
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

    # Mostrar en interfaz
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
        # Para Linux/Mac
        subprocess.Popen(['open', filepath])
    except:
        messagebox.showinfo("Éxito", f"Mapa guardado en:\n{filepath}\nÁbrelo con Google Earth")

    messagebox.showinfo("Éxito", f"Mapa abierto:\n{filepath}")


def long_distance_action():
    """Mostrar mapa de vuelos de larga distancia"""
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


# ===== CREAR INTERFAZ GRÁFICA =====

root = tk.Tk()
root.geometry("1920x1080")
root.title("Airport Management System v2.0 - UPC Group 9")

# Configurar grid
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=10)
root.rowconfigure(0, weight=2)
root.rowconfigure(1, weight=2)
root.rowconfigure(2, weight=1)

# ===== PANEL IZQUIERDO - BOTONES =====

# 1. Frame para Cargar Aeroports
file_frame = tk.LabelFrame(root, text="📁 Aeroports", font=("Arial", 11, "bold"))
file_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
file_frame.columnconfigure(0, weight=1)

buttonload = tk.Button(file_frame, text="Cargar Aeroports", command=load_airports_from_file,
                       bg="#3498db", fg="white", font=("Arial", 10, "bold"), height=2)
buttonload.pack(fill="both", expand=True, padx=5, pady=5)

# 2. Frame para Cargar/Guardar Vuelos
flights_frame = tk.LabelFrame(root, text="✈️ Vuelos", font=("Arial", 11, "bold"))
flights_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
flights_frame.columnconfigure(0, weight=1)

button_load_flights = tk.Button(flights_frame, text="Cargar Vuelos", command=load_arrivals_from_file,
                                bg="#9b59b6", fg="white", font=("Arial", 10, "bold"), height=2)
button_load_flights.pack(fill="both", expand=True, padx=5, pady=5)

button_save_flights = tk.Button(flights_frame, text="Guardar Vuelos", command=save_flights_action,
                                bg="#16a085", fg="white", font=("Arial", 10, "bold"), height=2)
button_save_flights.pack(fill="both", expand=True, padx=5, pady=5)

# 3. Frame para Gráficos de Vuelos
graph_flights_frame = tk.LabelFrame(root, text="📊 Gráficos", font=("Arial", 11, "bold"))
graph_flights_frame.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
graph_flights_frame.columnconfigure(0, weight=1)

button_plot_arrivals = tk.Button(graph_flights_frame, text="Llegadas/Hora", command=plot_arrivals_action,
                                 bg="#e67e22", fg="white", font=("Arial", 9, "bold"))
button_plot_arrivals.pack(fill="x", padx=5, pady=3)

button_plot_airlines = tk.Button(graph_flights_frame, text="Vuelos/Aerolínea", command=plot_airlines_action,
                                 bg="#c0392b", fg="white", font=("Arial", 9, "bold"))
button_plot_airlines.pack(fill="x", padx=5, pady=3)

button_plot_type = tk.Button(graph_flights_frame, text="Schengen vs No", command=plot_flights_type_action,
                             bg="#27ae60", fg="white", font=("Arial", 9, "bold"))
button_plot_type.pack(fill="x", padx=5, pady=3)

button_map = tk.Button(graph_flights_frame, text="Mapa Trayectorias", command=map_flights_action,
                       bg="#3498db", fg="white", font=("Arial", 9, "bold"))
button_map.pack(fill="x", padx=5, pady=3)

button_long_dist = tk.Button(graph_flights_frame, text="Larga Distancia >2000km", command=long_distance_action,
                             bg="#f39c12", fg="white", font=("Arial", 9, "bold"))
button_long_dist.pack(fill="x", padx=5, pady=3)

# ===== PANEL DERECHO - VISUALIZACIÓN =====

picture_frame = tk.LabelFrame(root, text="📈 Visualización", font=("Arial", 11, "bold"))
picture_frame.grid(row=0, column=1, rowspan=3, padx=5, pady=5, sticky="nsew")
picture_frame.rowconfigure(0, weight=1)
picture_frame.columnconfigure(0, weight=1)

initial_label = tk.Label(picture_frame, text="Selecciona una opción para visualizar",
                         font=("Arial", 12), fg="#7f8c8d")
initial_label.pack(expand=True)

# Abrir ventana
root.mainloop()
