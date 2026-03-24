from airport import *

# ===== TEST STEP 1 =====
print("=== TEST STEP 1: Crear aeroport ===")
ap1 = Airport("LEBL", 41.297445, 2.0832941)
SetSchengen(ap1)
PrintAirport(ap1)
print()

# ===== TEST STEP 3 =====
print("=== TEST STEP 3: Cargar aeroports ===")
airports = LoadAirports("airports_file")
print(f"✓ Carregats {len(airports)} aeroports\n")

if len(airports) > 0:
    print("Primeros 3 aeroports:")
    for a in airports[:3]:
        PrintAirport(a)
    print()
else:
    print(" No se cargaron aeroports. Comprueba que airports_file existe.\n")

# ===== TEST STEP 4 =====
print("=== TEST STEP 4: Añadir/Eliminar aeroports ===")
if len(airports) > 0:
    new_ap = Airport("LEMD", 40.4667, -3.567)
    SetSchengen(new_ap)
    result = AddAirport(airports, new_ap)
    print(f"✓ Aeroport LEMD añadido: {result}")

    result2 = RemoveAirport(airports, "LEMD")
    print(f"✓ Aeroport LEMD eliminado: {result2 == 0}")

    result3 = SaveSchengenAirports(airports, "schengen_airports.txt")
    print(f"✓ Aeroports Schengen guardados: {result3} aeroports\n")

# ===== TEST STEP 5 GRÁFICOS =====
if len(airports) > 0:
    print("=== TEST STEP 5: Gráficos ===")
    print(" Abriendo gráfica...")
    PlotAirports(airports)

    print("Creando mapa KML...")
    MapAirports(airports)
else:
    print("No se pueden mostrar gráficos sin aeroports cargados")