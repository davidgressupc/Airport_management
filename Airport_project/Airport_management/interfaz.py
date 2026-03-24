import tkinter as tk
from tkinter import messagebox, filedialog
from airport import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ===== VARIABLES GLOBALES =====
airports = []


# ===== FUNCIONES PARA BOTONES (USANDO SOLO airport.py) =====

def load_airports_from_file():
    """Cargar aeroports desde fichero - USA: LoadAirports()"""
    global airports
    filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if filename:
        airports = LoadAirports(filename)
        messagebox.showinfo("Éxito", f"✓ Carregats {len(airports)} aeroports")
    else:
        messagebox.showerror("Error", "No file selected")


def add_airport_manual():
    """Añadir un aeroport manualmente - USA: Airport(), SetSchengen(), AddAirport()"""
    global airports
    code_entry = entry_code.get()
    try:
        lat = float(entry_lat.get())
        lon = float(entry_lon.get())

        if not code_entry:
            messagebox.showerror("Error", "Codi ICAO requerido")
            return

        new_airport = Airport(code_entry, lat, lon)
        SetSchengen(new_airport)

        if len(code_entry)!=4:
            messagebox.showerror("Error", "Format incorrecte, ")
            return

        if AddAirport(airports, new_airport):
            messagebox.showinfo("Éxito", f"✓ Aeroport {code_entry} afegit")
            entry_code.delete(0, tk.END)
            entry_lat.delete(0, tk.END)
            entry_lon.delete(0, tk.END)
        else:
            messagebox.showwarning("Aviso", f"L'aeroport {code_entry} ja existeix")
    except ValueError:
        messagebox.showerror("Error", "Latitud i Longitud han de ser nombres")


def delete_airport_action():
    """Eliminar un aeroport - USA: RemoveAirport()"""
    global airports
    code = entry_search.get()
    if not code:
        messagebox.showerror("Error", "Introdueix codi ICAO")
        return

    if RemoveAirport(airports, code) == 0:
        messagebox.showinfo("Éxito", f"✓ Aeroport {code} eliminat")
        entry_search.delete(0, tk.END)
    else:
        messagebox.showerror("Error", f"Aeroport {code} no trobat")


def show_airport_data():
    """Mostrar dades de un aeroport - USA: PrintAirport()"""
    global airports
    code = entry_search.get()
    if not code:
        messagebox.showerror("Error", "Introdueix codi ICAO")
        return

    for a in airports:
        if a.icao_code.upper() == code.upper():
            info = f"Codi: {a.icao_code}\nLatitud: {a.latitude:.4f}\nLongitud: {a.longitude:.4f}\nSchengen: {'Sí' if a.schengen else 'No'}"
            messagebox.showinfo("Dades de l'aeroport", info)
            return

    messagebox.showerror("Error", f"Aeroport {code} no trobat")


def show_plot_schengen():
    """Mostrar gràfica Schengen vs No-Schengen - USA: PlotAirports()"""
    global airports
    if not airports:
        messagebox.showerror("Error", "No hi ha aeroports carregats")
        return

    fig = PlotAirports(airports)
    fig.show()

    if fig is None:
        return

    # Mostrar en interfaz
    for widget in picture_frame.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=picture_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


def show_google_earth_map():
    """Generar mapa KML para Google Earth - USA: MapAirports()"""
    global airports
    if not airports:
        messagebox.showerror("Error", "No hi ha aeroports carregats")
        return

    MapAirports(airports)
    messagebox.showinfo("Éxito", "✓ Mapa guardat: airports_map.kml\n(Obrir amb Google Earth Pro)")


def save_schengen_airports():
    """Guardar aeroports Schengen en fichero - USA: SaveSchengenAirports()"""
    global airports
    if not airports:
        messagebox.showerror("Error", "No hi ha aeroports carregats")
        return

    result = SaveSchengenAirports(airports, "schengen_airports.txt")
    if result > 0:
        messagebox.showinfo("Éxito", f"✓ {result} aeroports Schengen guardats en 'schengen_airports.txt'")
    else:
        messagebox.showerror("Error", "No hi ha aeroports Schengen")


# ===== CREAR INTERFAZ GRÁFICA =====

root = tk.Tk()
root.geometry("1280x720")
root.title("Airport Management System - UPC Group 9")

# Configurar grid
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=10)
root.rowconfigure(0, weight=2)
root.rowconfigure(1, weight=2)
root.rowconfigure(2, weight=1)

# ===== PANEL IZQUIERDO - BOTONES =====

# 1. Frame para Cargar/Guardar
file_frame = tk.LabelFrame(root, text="📁 Ficheros", font=("Arial", 11, "bold"))
file_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
file_frame.columnconfigure(0, weight=1)

buttonload = tk.Button(file_frame, text="Cargar Aeroports", command=load_airports_from_file,
                       bg="#3498db", fg="white", font=("Arial", 10, "bold"), height=2)
buttonload.pack(fill="both", expand=True, padx=5, pady=5)

buttonsave = tk.Button(file_frame, text="Guardar Schengen", command=save_schengen_airports,
                       bg="#27ae60", fg="white", font=("Arial", 10, "bold"), height=2)
buttonsave.pack(fill="both", expand=True, padx=5, pady=5)

# 2. Frame para Gráficos
graph_frame = tk.LabelFrame(root, text="📊 Gráficos", font=("Arial", 11, "bold"))
graph_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
graph_frame.columnconfigure(0, weight=1)

button_plot = tk.Button(graph_frame, text="Mostrar Gráfica", command=show_plot_schengen,
                        bg="#e74c3c", fg="white", font=("Arial", 10, "bold"), height=2)
button_plot.pack(fill="both", expand=True, padx=5, pady=5)

button_map = tk.Button(graph_frame, text="Mapa Google Earth", command=show_google_earth_map,
                       bg="#f39c12", fg="white", font=("Arial", 10, "bold"), height=2)
button_map.pack(fill="both", expand=True, padx=5, pady=5)

# 3. Frame para Añadir Aeroport
add_frame = tk.LabelFrame(root, text="➕ Añadir Aeroport", font=("Arial", 11, "bold"))
add_frame.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
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

button_add = tk.Button(add_frame, text="Afegir", command=add_airport_manual,
                       bg="#27ae60", fg="white", font=("Arial", 10, "bold"))
button_add.pack(fill="x", padx=5, pady=5)

# ===== PANEL DERECHO - BÚSQUEDA Y VISUALIZACIÓN =====

# Frame para búsqueda/eliminar
search_frame = tk.LabelFrame(root, text="🔍 Buscar/Eliminar", font=("Arial", 11, "bold"))
search_frame.grid(row=0, column=1, rowspan=1, padx=5, pady=5, sticky="nsew")
search_frame.columnconfigure(0, weight=1)
search_frame.columnconfigure(1, weight=1)

tk.Label(search_frame, text="Codi ICAO:", font=("Arial", 9)).grid(row=0, column=0, columnspan=2,
                                                                  sticky="w", padx=5, pady=2)
entry_search = tk.Entry(search_frame, font=("Arial", 10))
entry_search.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

button_show = tk.Button(search_frame, text="Ver Dades", command=show_airport_data,
                        bg="#3498db", fg="white", font=("Arial", 9, "bold"))
button_show.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

button_delete = tk.Button(search_frame, text="Eliminar", command=delete_airport_action,
                          bg="#e74c3c", fg="white", font=("Arial", 9, "bold"))
button_delete.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

# Frame para mostrar gráficos/mapas
picture_frame = tk.LabelFrame(root, text=" Visualización", font=("Arial", 11, "bold"))
picture_frame.grid(row=1, column=1, rowspan=2, padx=5, pady=5, sticky="nsew")
picture_frame.rowconfigure(0, weight=1)
picture_frame.columnconfigure(0, weight=1)

# Label inicial
initial_label = tk.Label(picture_frame, text="Selecciona una opción para visualizar",
                         font=("Arial", 12), fg="#7f8c8d")
initial_label.pack(expand=True)

# ===== EJECUTAR =====
root.mainloop()