import tkinter as tk
from tkinter import messagebox, filedialog
from airport import *
import os
import subprocess
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import copy
import numpy as np
import urllib.request
import json

airports = []
aircrafts = []
departures = []
merged_aircrafts = []
night_aircrafts = []
bcn = None


def load_airports_from_file():
    global airports
    filename = "airports_file.txt"
    airports = LoadAirports(filename)
    if airports:
        messagebox.showinfo("Èxit", f"{len(airports)} aeroports carregats correctament.")
    else:
        messagebox.showerror("Error", f"No s'ha trobat el fitxer: {filename}")


def add_airport_manual():
    global airports
    code_entry = entry_code.get().strip().upper()
    try:
        lat = float(entry_lat.get())
        lon = float(entry_lon.get())
        if not code_entry:
            messagebox.showerror("Error", "El codi ICAO és requerit.")
            return
        if len(code_entry) != 4:
            messagebox.showerror("Error", "Format incorrecte. El codi ICAO necessita exactament 4 caràcters.")
            return
        new_airport = Airport(code_entry, lat, lon)
        SetSchengen(new_airport)
        if AddAirport(airports, new_airport):
            messagebox.showinfo("Èxit", f"Aeroport {code_entry} afegit correctament.")
            entry_code.delete(0, tk.END)
            entry_lat.delete(0, tk.END)
            entry_lon.delete(0, tk.END)
            show_plot_schengen()
        else:
            messagebox.showwarning("Avís", f"L'aeroport {code_entry} ja existeix al sistema.")
    except ValueError:
        messagebox.showerror("Error", "La latitud i la longitud han de ser valors numèrics.")


def delete_airport_action():
    global airports
    code = entry_search.get().strip().upper()
    if not code:
        messagebox.showerror("Error", "Introdueix un codi ICAO vàlid.")
        return
    if RemoveAirport(airports, code) == 0:
        messagebox.showinfo("Èxit", f"Aeroport {code} eliminat correctament.")
        entry_search.delete(0, tk.END)
        show_plot_schengen()
    else:
        messagebox.showerror("Error", f"L'aeroport {code} no s'ha trobat.")


def show_airport_data():
    global airports
    code = entry_search.get().strip().upper()
    if not code:
        messagebox.showerror("Error", "Introdueix un codi ICAO.")
        return
    i = 0
    while i < len(airports):
        a = airports[i]
        if a.icao_code.upper() == code:
            info = f"Codi: {a.icao_code}\nLatitud: {a.latitude:.4f}\nLongitud: {a.longitude:.4f}\nSchengen: {'Sí' if a.schengen else 'No'}"
            messagebox.showinfo("Dades de l'aeroport", info)
            return
        i += 1
    messagebox.showerror("Error", f"L'aeroport {code} no s'ha trobat.")


def show_plot_schengen():
    global airports
    if not airports:
        messagebox.showerror("Error", "No hi ha aeroports carregats al sistema.")
        return
    fig, ax = PlotAirports(airports)
    if fig is None:
        return
    for widget in picture_frame.winfo_children():
        widget.destroy()
    fig.patch.set_facecolor('#121212')
    ax.set_facecolor('#1e1e1e')
    ax.title.set_color('white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.tick_params(colors='white')
    canvas = FigureCanvasTkAgg(fig, master=picture_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


def show_google_earth_map():
    global airports
    if not airports:
        messagebox.showerror("Error", "No hi ha aeroports carregats.")
        return
    filepath = MapAirports(airports)
    if filepath is None:
        messagebox.showerror("Error", "No s'ha pogut generar el mapa de Google Earth.")
        return
    try:
        os.startfile(filepath)
    except AttributeError:
        subprocess.Popen(['open', filepath])
    except:
        pass
    messagebox.showinfo("Èxit", f"Mapa obert correctament a:\n{filepath}")


def save_schengen_airports():
    global airports
    if not airports:
        messagebox.showerror("Error", "No hi ha aeroports carregats.")
        return
    result = SaveSchengenAirports(airports, "schengen_airports.txt")
    if result > 0:
        messagebox.showinfo("Èxit", f"✓ {result} aeroports Schengen guardats a 'schengen_airports.txt'")
    else:
        messagebox.showerror("Error", "No s'ha trobat cap aeroport Schengen per guardar.")


# ===== FUNCIONS PER A VOLS =====

def load_arrivals_from_file():
    from aircraft import LoadArrivals
    global aircrafts
    filename = "Arrivals_file.txt"
    if filename:
        aircrafts = LoadArrivals(filename)
        if aircrafts:
            messagebox.showinfo("Èxit", f"{len(aircrafts)} vols d'arribada carregats correctament.")
        else:
            messagebox.showerror("Error", "No s'han pogut carregar els vols del fitxer.")


def plot_arrivals_action():
    from aircraft import PlotArrivals
    global aircrafts
    if not aircrafts:
        messagebox.showerror("Error", "No hi ha vols carregats.")
        return
    fig, ax = PlotArrivals(aircrafts)
    if fig is None:
        return
    for widget in picture_frame.winfo_children():
        widget.destroy()
    fig.patch.set_facecolor('#121212')
    ax.set_facecolor('#1e1e1e')
    ax.title.set_color('white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.tick_params(colors='white')
    canvas = FigureCanvasTkAgg(fig, master=picture_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


def plot_airlines_action():
    from aircraft import PlotAirlines
    global aircrafts
    if not aircrafts:
        messagebox.showerror("Error", "No hi ha vols carregats.")
        return
    fig, ax = PlotAirlines(aircrafts)
    if fig is None:
        return
    for widget in picture_frame.winfo_children():
        widget.destroy()
    fig.patch.set_facecolor('#121212')
    ax.set_facecolor('#1e1e1e')
    ax.title.set_color('white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.tick_params(colors='white')
    canvas = FigureCanvasTkAgg(fig, master=picture_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


def plot_flights_type_action():
    from aircraft import PlotFlightsType
    global aircrafts
    if not aircrafts:
        messagebox.showerror("Error", "No hi ha vols carregats.")
        return
    fig, ax = PlotFlightsType(aircrafts, airports)
    if fig is None:
        return
    for widget in picture_frame.winfo_children():
        widget.destroy()
    fig.patch.set_facecolor('#121212')
    ax.set_facecolor('#1e1e1e')
    ax.title.set_color('white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.tick_params(colors='white')
    canvas = FigureCanvasTkAgg(fig, master=picture_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


def map_flights_action():
    from aircraft import MapFlights
    global aircrafts, airports
    if not aircrafts:
        messagebox.showerror("Error", "No hi ha vols carregats.")
        return
    if not airports:
        messagebox.showerror("Error", "No hi ha aeroports carregats.")
        return
    filepath = MapFlights(aircrafts, airports)
    if filepath is None:
        messagebox.showerror("Error", "No s'ha pogut generar el mapa de trajectòries.")
        return
    try:
        os.startfile(filepath)
    except AttributeError:
        subprocess.Popen(['open', filepath])
    except:
        pass
    messagebox.showinfo("Èxit", f"Mapa de trajectòries obert:\n{filepath}")


def long_distance_action():
    from aircraft import LongDistanceArrivals, MapFlights
    global aircrafts, airports
    if not aircrafts:
        messagebox.showerror("Error", "No hi ha vols carregats.")
        return
    if not airports:
        messagebox.showerror("Error", "No hi ha aeroports carregats.")
        return
    long_distance_flights = LongDistanceArrivals(aircrafts, airports)
    if not long_distance_flights:
        messagebox.showinfo("Informació", "No s'han detectat vols de llarga distància (>2000 km).")
        return
    filepath = MapFlights(long_distance_flights, airports)
    if filepath is None:
        messagebox.showerror("Error", "No s'ha pogut generar el mapa.")
        return
    try:
        os.startfile(filepath)
    except AttributeError:
        subprocess.Popen(['open', filepath])
    except:
        pass
    messagebox.showinfo("Èxit",
                        f"Mapa guardat:\n{filepath}\n({len(long_distance_flights)} vols de llarga distància detectats)")


def non_schengen_action():
    from aircraft import MapFlights
    global aircrafts, airports
    if not aircrafts or not airports:
        messagebox.showerror("Error", "Falten dades de vols o aeroports per fer la cerca.")
        return
    non_schengen = []
    i = 0
    while i < len(aircrafts):
        j = 0
        found = False
        while j < len(airports) and not found:
            airport = airports[j]
            if airport.icao_code.upper() == aircrafts[i].origin.upper():
                if not airport.schengen:
                    non_schengen.append(aircrafts[i])
                found = True
            j += 1
        i += 1
    if len(non_schengen) == 0:
        messagebox.showinfo("Informació", "No hi ha vols NO Schengen.")
        return
    filepath = MapFlights(non_schengen, airports)
    try:
        os.startfile(filepath)
    except AttributeError:
        subprocess.Popen(['open', filepath])
    messagebox.showinfo("Èxit", f"{len(non_schengen)} vols NO Schengen mostrats al mapa.")


def save_flights_action():
    from aircraft import SaveFlights
    global aircrafts
    if not aircrafts:
        messagebox.showerror("Error", "No hi ha vols per guardar al fitxer.")
        return
    filename = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Fitxers de text", "*.txt"), ("Tots els fitxers", "*.*")]
    )
    if filename:
        result = SaveFlights(aircrafts, filename)
        if result > 0:
            messagebox.showinfo("Èxit", f"✓ {result} vols guardats correctament a '{filename}'")
        else:
            messagebox.showerror("Error", "No s'han pogut guardar els vols.")


# ===== FUNCIONS PER A GATES (V3) =====

def load_airport_structure():
    from LEBL import LoadAirportStructure
    global bcn
    filename = "Terminals.txt"
    if filename:
        bcn = LoadAirportStructure(filename)
        if bcn:
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
            info_text = f"✓ Aeroport {bcn.code} carregat correctament\n✓ Total de gates (portes): {total_gates}\n\n"
            info_text += "Aerolínies assignades per terminal:\n"
            i = 0
            while i < len(bcn.terminals):
                terminal = bcn.terminals[i]
                info_text += f"  • Terminal {terminal.name}: {len(terminal.airlines)} aerolínies\n"
                i += 1
            messagebox.showinfo("Èxit", info_text)
        else:
            messagebox.showerror("Error", "No s'ha pogut carregar l'estructura de l'aeroport.")


def assign_gates_to_flights():
    from LEBL import AssignGate
    global bcn, aircrafts
    if not bcn:
        messagebox.showerror("Error", "L'estructura de l'aeroport (LEBL) no està carregada.")
        return
    if not aircrafts:
        messagebox.showerror("Error", "No hi ha vols carregats al sistema.")
        return
    assigned = 0
    failed = 0
    failed_airlines = []
    i = 0
    while i < len(aircrafts):
        aircraft = aircrafts[i]
        result = AssignGate(bcn, aircraft)
        if result == 0:
            assigned += 1
        else:
            failed += 1
            if aircraft.airline not in failed_airlines:
                failed_airlines.append(aircraft.airline)
        i += 1
    message = f"✓ {assigned} vols assignats correctament a les portes\n✗ {failed} vols s'han quedat sense porta disponible"
    if failed_airlines:
        message += f"\n\nAerolínies sense terminal/porta compatible:"
        j = 0
        while j < len(failed_airlines):
            message += f"\n  - {failed_airlines[j]}"
            j += 1
    messagebox.showinfo("Asignació de Gates", message)


def show_gate_occupancy():
    from LEBL import GateOccupancy
    global bcn
    if not bcn:
        messagebox.showerror("Error", "L'estructura de l'aeroport no està carregada.")
        return
    occupancy = GateOccupancy(bcn)
    free_gates = 0
    occupied_gates = 0
    i = 0
    while i < len(occupancy):
        if occupancy[i]['status'] == 'Libre' or occupancy[i]['status'] == 'Lliure':
            free_gates += 1
        else:
            occupied_gates += 1
        i += 1
    info_text = f"📊 Estat de les Gates (Portes)\n\n"
    info_text += f"✓ Gates lliures: {free_gates}\n"
    info_text += f"✗ Gates ocupades: {occupied_gates}\n"
    info_text += f"Total: {len(occupancy)}"
    messagebox.showinfo("Estat de les Gates", info_text)


def plot_gates_action():
    from LEBL import PlotGates
    global bcn
    if not bcn:
        messagebox.showerror("Error", "L'estructura de l'aeroport no està carregada.")
        return
    try:
        fig, axes = PlotGates(bcn)
        if fig is None:
            messagebox.showerror("Error", "No s'ha pogut generar el gràfic de les portes.")
            return
        for widget in picture_frame.winfo_children():
            widget.destroy()
        fig.patch.set_facecolor(COLOR_FONDO)
        for ax in axes.ravel() if hasattr(axes, 'ravel') else [axes]:
            ax.set_facecolor('white')
            ax.title.set_color('white')
            ax.tick_params(colors='white')
        canvas = FigureCanvasTkAgg(fig, master=picture_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    except Exception as e:
        messagebox.showerror("Error", f"Error en visualitzar les gates: {str(e)}")


# ===== FUNCIONS PER A GATES (V4) =====

def load_departures_from_file():
    from LEBL import LoadDepartures
    global departures
    filename = "Departures_file.txt"
    departures = LoadDepartures(filename)
    if departures:
        messagebox.showinfo("Èxit", f"{len(departures)} vols de sortida (Departures) carregats.")
    else:
        messagebox.showerror("Error", f"No s'ha pogut carregar el fitxer: {filename}")


def merge_arrivals_departures():
    from LEBL import MergeMovements
    global aircrafts, departures, merged_aircrafts
    if not aircrafts:
        messagebox.showerror("Error", "No hi ha vols d'arribada carregats.")
        return
    if not departures:
        messagebox.showerror("Error", "No hi ha vols de sortida carregats.")
        return
    merged_aircrafts, status = MergeMovements(aircrafts, departures)
    if status == 0:
        messagebox.showinfo("Èxit", f"✓ {len(merged_aircrafts)} vols fusionats correctament (Arribades + Sortides).")
    else:
        messagebox.showerror("Error", "No s'han pogut fusionar els moviments de vols.")


def identify_night_aircraft():
    from LEBL import NightAircraft
    global merged_aircrafts, night_aircrafts
    if not merged_aircrafts:
        messagebox.showerror("Error", "Primer has de fusionar les arribades i sortides.")
        return
    night_aircrafts, status = NightAircraft(merged_aircrafts)
    if night_aircrafts:
        message = f"✓ {len(night_aircrafts)} avions nocturnes detectats:\n\n"
        i = 0
        while i < min(10, len(night_aircrafts)):
            ac = night_aircrafts[i]
            message += f"  • {ac.aircraft_id} → {ac.destination} ({ac.departure_time})\n"
            i += 1
        if len(night_aircrafts) > 10:
            message += f"\n  ... i {len(night_aircrafts) - 10} més."
        messagebox.showinfo("Avions Nocturnes", message)
    else:
        messagebox.showinfo("Informació", "No s'ha detectat cap avió nocturn.")


def assign_night_gates_action():
    from LEBL import AssignNightGates
    global bcn, night_aircrafts
    if not bcn:
        messagebox.showerror("Error", "L'estructura de l'aeroport no està carregada.")
        return
    if not night_aircrafts:
        messagebox.showerror("Error", "Primer has d'identificar els avions nocturnes.")
        return
    assigned = AssignNightGates(bcn, night_aircrafts)
    if assigned > 0:
        messagebox.showinfo("Èxit", f"✓ {assigned} avions nocturnes assignats de forma fixa a les gates.")
    else:
        messagebox.showwarning("Avís", "No s'ha pogut assignar cap avió nocturn.")


def assign_gates_by_hour_action():
    from LEBL import AssignGatesAtTime
    global bcn, merged_aircrafts
    if not bcn:
        messagebox.showerror("Error", "L'estructura de l'aeroport no està carregada.")
        return
    if not merged_aircrafts:
        messagebox.showerror("Error", "No hi ha vols fusionats disponibles.")
        return

    hour_window = tk.Toplevel(root)
    hour_window.title("Seleccionar Hora")
    hour_window.geometry("300x150")
    hour_window.resizable(False, False)
    hour_window.configure(bg="#121212")

    tk.Label(hour_window, text="Selecciona l'hora de simulació:", font=("Arial", 10), bg="#121212", fg="white").pack(
        pady=10)
    hour_var = tk.StringVar(value="12")
    hour_spinbox = tk.Spinbox(hour_window, from_=0, to=23, textvariable=hour_var, width=10, font=("Arial", 12))
    hour_spinbox.pack(pady=10)

    def assign_and_close():
        global bcn
        try:
            hour_int = int(hour_spinbox.get())
            hour_str = f"{hour_int}:00"
            bcn_reset = copy.deepcopy(bcn)
            h = 0
            while h <= hour_int:
                AssignGatesAtTime(bcn_reset, merged_aircrafts, f"{h}:00")
                h += 1
            bcn = bcn_reset
            messagebox.showinfo("Èxit", f"✓ Gates assignades correctament fins a les {hour_str}")
            hour_window.destroy()
            plot_gates_action()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(hour_window, text="Assignar", command=assign_and_close,
              bg="#1f4e79", fg="white", font=("Arial", 10, "bold"), width=15).pack(pady=10)


def plot_day_occupancy_action():
    from LEBL import PlotDayOccupancy
    global bcn, merged_aircrafts
    if not bcn:
        messagebox.showerror("Error", "L'estructura de l'aeroport no està carregada.")
        return
    if not merged_aircrafts:
        messagebox.showerror("Error", "No hi ha vols fusionats disponibles.")
        return
    try:
        fig, ax = PlotDayOccupancy(bcn, merged_aircrafts)
        if fig is None:
            messagebox.showerror("Error", "No s'ha pogut generar la gràfica d'ocupació.")
            return
        for widget in picture_frame.winfo_children():
            widget.destroy()
        fig.patch.set_facecolor('#121212')
        ax.set_facecolor('#1e1e1e')
        ax.title.set_color('white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.tick_params(colors='white')
        canvas = FigureCanvasTkAgg(fig, master=picture_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    except Exception as e:
        messagebox.showerror("Error", f"Error al generar la gràfica: {str(e)}")


# ===== GESTIÓ D'EMERGÈNCIES =====

def declare_emergency_flight_window():
    if not bcn:
        messagebox.showerror("Error", "L'estructura de l'aeroport no està carregada.")
        return
    if not aircrafts:
        messagebox.showerror("Error", "No hi ha vols d'arribada carregats al sistema.")
        return

    emergency_window = tk.Toplevel(root)
    emergency_window.title("Protocol d'Emergència")
    emergency_window.geometry("350x180")
    emergency_window.resizable(False, False)
    emergency_window.configure(bg="#962d2d")

    tk.Label(emergency_window, text="🚨 CONTROL D'EMERGÈNCIES LEBL 🚨", font=("Arial", 11, "bold"), bg="#962d2d",
             fg="white").pack(pady=10)
    tk.Label(emergency_window, text="Introdueix l'Identificador del Vol (Aircraft ID):", font=("Arial", 9),
             bg="#962d2d", fg="white").pack()

    id_var = tk.StringVar()
    entry_id = tk.Entry(emergency_window, textvariable=id_var, font=("Arial", 11), width=20, justify="center")
    entry_id.pack(pady=10)

    def trigger_emergency_routing():
        global bcn
        target_id = id_var.get().strip().upper()
        if not target_id:
            messagebox.showerror("Error", "L'ID introduït no és vàlid.")
            return

        flight_found = None
        i = 0
        while i < len(aircrafts):
            if aircrafts[i].aircraft_id.upper() == target_id:
                flight_found = aircrafts[i]
                break
            i += 1

        if not flight_found:
            messagebox.showerror("Error", f"No s'ha trobat cap vol amb l'ID: {target_id}")
            return

        assigned_gate = None
        t = 0
        while t < len(bcn.terminals) and not assigned_gate:
            term = bcn.terminals[t]
            a = 0
            while a < len(term.boarding_areas) and not assigned_gate:
                area = term.boarding_areas[a]
                g = 0
                while g < len(area.gates) and not assigned_gate:
                    gate = area.gates[g]

                    # COMPROVACIÓ AMB AIRCRAFT_ID SEGONS LA TEVA CLASSE GATE
                    if gate.aircraft_id is None or gate.aircraft_id == "":
                        assigned_gate = gate
                        flight_found.airline = "EMERGENCY"
                        flight_found.gate = gate.name
                        gate.aircraft_id = flight_found.aircraft_id
                    g += 1
                a += 1
            t += 1

        if assigned_gate:
            messagebox.showinfo("🚨 PRIORITAT MAYDAY 🚨",
                                f"El vol {target_id} s'ha ficat directament a la pista!\n\n"
                                f"• Estat: ASSIGNACIÓ MANUAL CRÍTICA\n"
                                f"• Forçat immediat a la porta: GATE {assigned_gate.name}\n"
                                f"• L'espai s'ha reservat de forma indefinida.")
            emergency_window.destroy()
            plot_gates_action()
        else:
            messagebox.showerror("🚨 ERROR CRÍTIC 🚨",
                                 "Col·lapse absolut! No queda cap porta física lliure a l'aeroport.")

    tk.Button(emergency_window, text="Autoritzar Aterratge Immediat", command=trigger_emergency_routing,
              bg="white", fg="#962d2d", font=("Arial", 10, "bold"), relief="flat").pack(pady=5)


# ===== CONSULTA EN TEMPS REAL METAR LEBL =====

def fetch_live_metar_lebl():
    url = "https://aviationweather.gov/api/data/metar?ids=LEBL&format=json"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())

        if data and len(data) > 0:
            metar_raw = data[0].get('rawOb', 'No disponible')
            temp = data[0].get('temp', 'N/A')
            viento_dir = data[0].get('wdir', 'N/A')
            viento_vel = data[0].get('wspd', 'N/A')
            elevacion = data[0].get('elev', 'N/A')

            metar_report = tk.Toplevel(root)
            metar_report.title("METAR en temps real - LEBL")
            metar_report.geometry("420x240")
            metar_report.resizable(False, False)
            metar_report.configure(bg="#1e272e")

            tk.Label(metar_report, text="✈️ TORRE DE CONTROL LEBL: METAR ACTUAL ✈️",
                     font=("Arial", 10, "bold"), bg="#1e272e", fg="#00d2d3").pack(pady=10)

            raw_text_box = tk.Text(metar_report, font=("Courier New", 10, "bold"), height=2, width=45, bg="#2f3640",
                                   fg="#4cd137", bd=0, padx=5, pady=5)
            raw_text_box.insert(tk.END, metar_raw)
            raw_text_box.config(state=tk.DISABLED)
            raw_text_box.pack(pady=5)

            decoded_info = f"📊 DADES DELS SENSORS EN DIRECTE:\n\n" \
                           f"• Temperatura a pista: {temp} °C\n" \
                           f"• Direcció del vent: {viento_dir}°\n" \
                           f"• Velocitat del vent: {viento_vel} nusos (kt)\n" \
                           f"• Elevació del camp: {elevacion} metres"

            tk.Label(metar_report, text=decoded_info, font=("Arial", 10), bg="#1e272e", fg="white",
                     justify="left").pack(pady=10)
        else:
            messagebox.showerror("Error", "No s'han rebut dades meteorològiques per a l'ICAO: LEBL")
    except Exception as e:
        messagebox.showerror("Error de Xarxa", f"No s'ha pogut connectar amb el servidor meteorològic:\n{str(e)}")


# =======================================================
# ===== CONFIGURACIÓ INTERFÍCIE I COLORS ================
# =======================================================

COLOR_FONDO = "#3498db"
COLOR_BOTON = "#ffffff"
COLOR_TEXTO = "#3498db"
COLOR_TITULO = "#ffffff"

root = tk.Tk()
root.state('zoomed')
root.title("Airport Management System v4.0 - UPC EETAC")
root.configure(bg=COLOR_FONDO)

root.columnconfigure(0, weight=0, minsize=270)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=0, minsize=270)
root.rowconfigure(0, weight=1)

# === COLUMNA 1 (ESQUERRA) ===
left_frame = tk.Frame(root, bg=COLOR_FONDO, width=260)
left_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsw")

file_frame = tk.LabelFrame(left_frame, text="📁 Fitxers d'Aeroports", font=("Arial", 11, "bold"), bg=COLOR_FONDO,
                           fg=COLOR_TITULO)
file_frame.pack(fill="x", padx=5, pady=5)
tk.Button(file_frame, text="Carregar Aeroports", command=load_airports_from_file, bg=COLOR_BOTON, fg=COLOR_TEXTO,
          font=("Arial", 10, "bold"), height=2, relief="flat").pack(fill="x", padx=5, pady=5)
tk.Button(file_frame, text="Guardar Aeroports Schengen", command=save_schengen_airports, bg=COLOR_BOTON, fg=COLOR_TEXTO,
          font=("Arial", 10, "bold"), height=2, relief="flat").pack(fill="x", padx=5, pady=5)

search_frame = tk.LabelFrame(left_frame, text="🔍 Cercar/Eliminar Aeroport", font=("Arial", 11, "bold"), bg=COLOR_FONDO,
                             fg=COLOR_TITULO)
search_frame.pack(fill="x", padx=5, pady=5)
tk.Label(search_frame, text="Codi ICAO:", font=("Arial", 9), bg=COLOR_FONDO, fg=COLOR_TITULO).pack(anchor="w", padx=5,
                                                                                                   pady=2)
entry_search = tk.Entry(search_frame, font=("Arial", 10), bg="#ccd8e3", fg="white", insertbackground="white")
entry_search.pack(fill="x", padx=5, pady=2)
tk.Button(search_frame, text="Veure Dades", command=show_airport_data, bg=COLOR_BOTON, fg=COLOR_TEXTO,
          font=("Arial", 9, "bold"), relief="flat").pack(fill="x", padx=5, pady=3)
tk.Button(search_frame, text="Eliminar Aeroport", command=delete_airport_action, bg=COLOR_BOTON, fg=COLOR_TEXTO,
          font=("Arial", 9, "bold"), relief="flat").pack(fill="x", padx=5, pady=3)

add_frame = tk.LabelFrame(left_frame, text="➕ Afegir Aeroport Manual", font=("Arial", 11, "bold"), bg=COLOR_FONDO,
                          fg=COLOR_TITULO)
add_frame.pack(fill="x", padx=5, pady=5)
tk.Label(add_frame, text="Codi ICAO:", font=("Arial", 9), bg=COLOR_FONDO, fg=COLOR_TITULO).pack(anchor="w", padx=5,
                                                                                                pady=2)
entry_code = tk.Entry(add_frame, font=("Arial", 10), bg="#ccd8e3", fg="white", insertbackground="white")
entry_code.pack(fill="x", padx=5, pady=2)
tk.Label(add_frame, text="Latitud:", font=("Arial", 9), bg=COLOR_FONDO, fg=COLOR_TITULO).pack(anchor="w", padx=5,
                                                                                              pady=2)
entry_lat = tk.Entry(add_frame, font=("Arial", 10), bg="#ccd8e3", fg="white", insertbackground="white")
entry_lat.pack(fill="x", padx=5, pady=2)
tk.Label(add_frame, text="Longitud:", font=("Arial", 9), bg=COLOR_FONDO, fg=COLOR_TITULO).pack(anchor="w", padx=5,
                                                                                               pady=2)
entry_lon = tk.Entry(add_frame, font=("Arial", 10), bg="#ccd8e3", fg="white", insertbackground="white")
entry_lon.pack(fill="x", padx=5, pady=2)
tk.Button(add_frame, text="Afegir Aeroport", command=add_airport_manual, bg=COLOR_BOTON, fg=COLOR_TEXTO,
          font=("Arial", 10, "bold"), relief="flat").pack(fill="x", padx=5, pady=5)

flights_frame = tk.LabelFrame(left_frame, text="✈️ Fitxers de Vols", font=("Arial", 11, "bold"), bg=COLOR_FONDO,
                              fg=COLOR_TITULO)
flights_frame.pack(fill="x", padx=5, pady=5)
tk.Button(flights_frame, text="Carregar Vols (Arribades)", command=load_arrivals_from_file, bg=COLOR_BOTON,
          fg=COLOR_TEXTO, font=("Arial", 10, "bold"), height=2, relief="flat").pack(fill="x", padx=5, pady=5)
tk.Button(flights_frame, text="Guardar Vols al Disc", command=save_flights_action, bg=COLOR_BOTON, fg=COLOR_TEXTO,
          font=("Arial", 10, "bold"), height=2, relief="flat").pack(fill="x", padx=5, pady=5)

logo_frame = tk.Frame(left_frame, bg=COLOR_FONDO)
logo_frame.pack(fill="x", padx=5, pady=(2, 5))
try:
    img_logo = tk.PhotoImage(file="logo_eetac.png")
    img_logo = img_logo.subsample(3, 3)
    label_img = tk.Label(logo_frame, image=img_logo, bg=COLOR_FONDO)
    label_img.image = img_logo
    label_img.pack(anchor="n", pady=0)
except Exception:
    tk.Label(logo_frame, text="UPC - EETAC", font=("Arial", 10, "bold"), fg="#7f8c8d", bg=COLOR_FONDO).pack(anchor="n",
                                                                                                            pady=0)

# === COLUMNA 2 (CENTRE) ===
center_frame = tk.Frame(root, bg=COLOR_FONDO)
center_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
center_frame.rowconfigure(0, weight=1)
center_frame.rowconfigure(1, weight=0)
center_frame.columnconfigure(0, weight=1)

picture_frame = tk.LabelFrame(center_frame, text="📈 Visualització Gràfica", font=("Arial", 11, "bold"), bg=COLOR_FONDO,
                              fg=COLOR_TITULO)
picture_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
picture_frame.rowconfigure(0, weight=1)
picture_frame.columnconfigure(0, weight=1)
tk.Label(picture_frame, text="Selecciona una opció lateral per visualitzar les dades", font=("Arial", 12),
         fg=COLOR_TITULO, bg=COLOR_FONDO).pack(expand=True)

extra_frame = tk.LabelFrame(center_frame, text="🚨 Protocol de Contingència & Meteorologia", font=("Arial", 11, "bold"),
                            bg=COLOR_FONDO, fg=COLOR_TITULO)
extra_frame.grid(row=1, column=0, sticky="ew")

extra_frame.columnconfigure(0, weight=1)
extra_frame.columnconfigure(1, weight=1)

btn_emergencia = tk.Button(extra_frame, text="🚨 Declarar Emergència (Forçar Pista)",
                           command=declare_emergency_flight_window, bg="#c0392b", fg="white",
                           font=("Arial", 10, "bold"), relief="flat")
btn_emergencia.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

btn_metar = tk.Button(extra_frame, text="🌤️ Actualitzar METAR LEBL (Temps Real)",
                      command=fetch_live_metar_lebl, bg="#1b3a4b", fg="white", font=("Arial", 10, "bold"),
                      relief="flat")
btn_metar.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

# === COLUMNA 3 (DRETA) ===
right_frame = tk.Frame(root, bg=COLOR_FONDO, width=260)
right_frame.grid(row=0, column=2, padx=5, pady=5, sticky="nse")

graph_flights_frame = tk.LabelFrame(right_frame, text="📊 Gràfics de Vols i AP", font=("Arial", 11, "bold"),
                                    bg=COLOR_FONDO, fg=COLOR_TITULO)
graph_flights_frame.pack(fill="x", padx=5, pady=5)
tk.Button(graph_flights_frame, text="Schengen vs No-Schengen (AP)", command=show_plot_schengen, bg=COLOR_BOTON,
          fg=COLOR_TEXTO, font=("Arial", 9, "bold"), relief="flat").pack(fill="x", padx=5, pady=3)
tk.Button(graph_flights_frame, text="Mapa Google Earth", command=show_google_earth_map, bg=COLOR_BOTON, fg=COLOR_TEXTO,
          font=("Arial", 9, "bold"), relief="flat").pack(fill="x", padx=5, pady=3)
tk.Button(graph_flights_frame, text="Arribades per Hora", command=plot_arrivals_action, bg=COLOR_BOTON, fg=COLOR_TEXTO,
          font=("Arial", 9, "bold"), relief="flat").pack(fill="x", padx=5, pady=3)
tk.Button(graph_flights_frame, text="Vols per Aerolínia", command=plot_airlines_action, bg=COLOR_BOTON, fg=COLOR_TEXTO,
          font=("Arial", 9, "bold"), relief="flat").pack(fill="x", padx=5, pady=3)
tk.Button(graph_flights_frame, text="Vols Schengen vs No-Schengen", command=plot_flights_type_action, bg=COLOR_BOTON,
          fg=COLOR_TEXTO, font=("Arial", 9, "bold"), relief="flat").pack(fill="x", padx=5, pady=3)
tk.Button(graph_flights_frame, text="Mapa de Trajectòries", command=map_flights_action, bg=COLOR_BOTON, fg=COLOR_TEXTO,
          font=("Arial", 9, "bold"), relief="flat").pack(fill="x", padx=5, pady=3)
tk.Button(graph_flights_frame, text="Llarga Distància (>2000km)", command=long_distance_action, bg=COLOR_BOTON,
          fg=COLOR_TEXTO, font=("Arial", 9, "bold"), relief="flat").pack(fill="x", padx=5, pady=3)
tk.Button(graph_flights_frame, text="Mapa Vols NO Schengen", command=non_schengen_action, bg=COLOR_BOTON,
          fg=COLOR_TEXTO, font=("Arial", 9, "bold"), relief="flat").pack(fill="x", padx=5, pady=3)

gates_frame = tk.LabelFrame(right_frame, text="🚪 Gestió de Gates V3", font=("Arial", 11, "bold"), bg=COLOR_FONDO,
                            fg=COLOR_TITULO)
gates_frame.pack(fill="x", padx=5, pady=5)
tk.Button(gates_frame, text="Carregar Estructura LEBL", command=load_airport_structure, bg=COLOR_BOTON, fg=COLOR_TEXTO,
          font=("Arial", 10, "bold"), relief="flat").pack(fill="x", padx=5, pady=3)
tk.Button(gates_frame, text="Assignar Gates a Vols", command=assign_gates_to_flights, bg=COLOR_BOTON, fg=COLOR_TEXTO,
          font=("Arial", 10, "bold"), relief="flat").pack(fill="x", padx=5, pady=3)
tk.Button(gates_frame, text="Veure Estat de les Gates", command=show_gate_occupancy, bg=COLOR_BOTON, fg=COLOR_TEXTO,
          font=("Arial", 10, "bold"), relief="flat").pack(fill="x", padx=5, pady=3)
tk.Button(gates_frame, text="Visualitzar Gates (Gràfic)", command=plot_gates_action, bg=COLOR_BOTON, fg=COLOR_TEXTO,
          font=("Arial", 10, "bold"), relief="flat").pack(fill="x", padx=5, pady=3)

gates_frame_v4 = tk.LabelFrame(right_frame, text="🚪 Gestió de Gates V4", font=("Arial", 11, "bold"), bg=COLOR_FONDO,
                               fg=COLOR_TITULO)
gates_frame_v4.pack(fill="x", padx=5, pady=5)
tk.Button(gates_frame_v4, text="Carregar Sortides (Departures)", command=load_departures_from_file, bg=COLOR_BOTON,
          fg=COLOR_TEXTO, font=("Arial", 10, "bold"), relief="flat").pack(fill="x", padx=5, pady=3)
tk.Button(gates_frame_v4, text="Fusionar Arribades + Sortides", command=merge_arrivals_departures, bg=COLOR_BOTON,
          fg=COLOR_TEXTO, font=("Arial", 10, "bold"), relief="flat").pack(fill="x", padx=5, pady=3)
tk.Button(gates_frame_v4, text="Identificar Avions Nocturnes", command=identify_night_aircraft, bg=COLOR_BOTON,
          fg=COLOR_TEXTO, font=("Arial", 10, "bold"), relief="flat").pack(fill="x", padx=5, pady=3)
tk.Button(gates_frame_v4, text="Assignar Gates Nocturnes", command=assign_night_gates_action, bg=COLOR_BOTON,
          fg=COLOR_TEXTO, font=("Arial", 10, "bold"), relief="flat").pack(fill="x", padx=5, pady=3)
tk.Button(gates_frame_v4, text="Assignar Gates per Hora", command=assign_gates_by_hour_action, bg=COLOR_BOTON,
          fg=COLOR_TEXTO, font=("Arial", 10, "bold"), relief="flat").pack(fill="x", padx=5, pady=3)
tk.Button(gates_frame_v4, text="Ocupació Diària (Gràfica)", command=plot_day_occupancy_action, bg=COLOR_BOTON,
          fg=COLOR_TEXTO, font=("Arial", 10, "bold"), relief="flat").pack(fill="x", padx=5, pady=3)

root.mainloop()