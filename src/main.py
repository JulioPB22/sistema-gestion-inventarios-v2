"""
main.py
=======

Punto de entrada del **Sistema de Gestión de Inventarios** para una tienda de
abarrotes. Ofrece un menú interactivo de consola que integra:

* Alta y visualización de productos.
* Reabastecimiento, venta/descuento y eliminación.
* Control de duplicados y reporte de bajo stock.
* Persistencia automática en JSON.
* Carga de la base de muestra con limpieza vía pandas y generación de gráficas.

Ejecución:
    python src/main.py
"""

from __future__ import annotations

import sys

# En Windows la consola suele usar cp1252; forzamos UTF-8 para mostrar
# correctamente acentos y símbolos (✔, ⚠, $, etc.).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import analisis
from inventario import Inventario
from modelo import ProductoInvalidoError

RUTA_JSON = "datos/inventario.json"


def _pausar() -> None:
    input("\nPresiona ENTER para continuar...")


def _leer_float(mensaje: str) -> float:
    while True:
        try:
            return float(input(mensaje).replace(",", "."))
        except ValueError:
            print("  ⚠ Ingresa un número válido (ej. 24.50).")


def _leer_int(mensaje: str) -> int:
    while True:
        try:
            return int(input(mensaje))
        except ValueError:
            print("  ⚠ Ingresa un número entero válido (ej. 10).")


# --------------------------------------------------------------------- #
# Opciones del menú                                                     #
# --------------------------------------------------------------------- #
def opcion_mostrar(inv: Inventario) -> None:
    print("\n" + inv.mostrar_inventario())


def opcion_agregar(inv: Inventario) -> None:
    nombre = input("Nombre del producto: ").strip()
    if inv.existe(nombre):
        print(f"  ⚠ '{nombre}' ya existe. Usa la opción de reabastecer.")
        return
    precio = _leer_float("Precio (MXN): ")
    stock = _leer_int("Stock inicial (unidades): ")
    categoria = input("Categoría (ENTER = General): ").strip() or "General"
    try:
        inv.crear_producto(nombre, precio, stock, categoria)
        inv.guardar()
        print(f"  ✔ Producto '{nombre}' agregado y guardado.")
    except ProductoInvalidoError as e:
        print(f"  ⚠ {e}")


def opcion_reabastecer(inv: Inventario) -> None:
    nombre = input("Producto a reabastecer: ").strip()
    cantidad = _leer_int("Unidades a agregar: ")
    try:
        p = inv.reabastecer(nombre, cantidad)
        inv.guardar()
        print(f"  ✔ '{p.nombre}' ahora tiene {p.stock} unidades.")
    except (KeyError, ValueError) as e:
        print(f"  ⚠ {e}")


def opcion_vender(inv: Inventario) -> None:
    nombre = input("Producto vendido: ").strip()
    cantidad = _leer_int("Unidades vendidas: ")
    try:
        p = inv.descontar(nombre, cantidad)
        inv.guardar()
        print(f"  ✔ Venta registrada. '{p.nombre}' queda con {p.stock} unidades.")
    except (KeyError, ValueError) as e:
        print(f"  ⚠ {e}")


def opcion_eliminar(inv: Inventario) -> None:
    nombre = input("Producto a eliminar: ").strip()
    confirm = input(f"¿Seguro que deseas eliminar '{nombre}'? (s/n): ").lower()
    if confirm != "s":
        print("  Operación cancelada.")
        return
    try:
        p = inv.eliminar(nombre)
        inv.guardar()
        print(f"  ✔ '{p.nombre}' eliminado del inventario.")
    except KeyError as e:
        print(f"  ⚠ {e}")


def opcion_bajo_stock(inv: Inventario) -> None:
    bajos = inv.productos_bajo_stock()
    if not bajos:
        print("  ✔ No hay productos con bajo stock. ¡Todo en orden!")
        return
    print(f"\n⚠ Productos con bajo stock (<= {inv.umbral_bajo_stock} unidades):")
    print("-" * 64)
    for p in bajos:
        print(f"  {p}")


def opcion_cargar_muestra(inv: Inventario) -> None:
    print("\nCargando base de datos de muestra y aplicando limpieza (pandas)...")
    try:
        df = analisis.cargar_datos()
    except FileNotFoundError:
        print("  ⚠ No se encontró 'datos/inventario_muestra.csv'.")
        return
    analisis.explorar(df)
    limpio = analisis.limpiar(df)
    productos = analisis.a_productos(limpio)
    agregados = inv.cargar_desde_iterable(productos)
    inv.guardar()
    print(f"\n  ✔ {agregados} productos nuevos cargados desde la muestra y guardados.")


def opcion_graficas(inv: Inventario) -> None:
    import pandas as pd
    if len(inv) == 0:
        print("  ⚠ El inventario está vacío. Agrega o carga productos primero.")
        return
    df = pd.DataFrame([p.a_dict() for p in inv.listar()])
    rutas = analisis.generar_todas_las_graficas(df, inv.umbral_bajo_stock)
    print("\n  ✔ Gráficas generadas en la carpeta 'graficas/':")
    for r in rutas:
        print(f"     - {r}")


MENU = """
============================================================
   SISTEMA DE GESTIÓN DE INVENTARIOS - Tienda de Abarrotes
============================================================
  1. Mostrar inventario
  2. Agregar producto
  3. Reabastecer producto
  4. Registrar venta (descontar stock)
  5. Eliminar producto
  6. Ver productos con bajo stock
  7. Cargar base de datos de muestra (EDA + limpieza)
  8. Generar gráficas estadísticas
  0. Salir
============================================================"""


def main() -> None:
    inv = Inventario(ruta_archivo=RUTA_JSON)
    print(f"Inventario cargado: {len(inv)} producto(s) en existencia.")

    acciones = {
        "1": opcion_mostrar,
        "2": opcion_agregar,
        "3": opcion_reabastecer,
        "4": opcion_vender,
        "5": opcion_eliminar,
        "6": opcion_bajo_stock,
        "7": opcion_cargar_muestra,
        "8": opcion_graficas,
    }

    while True:
        print(MENU)
        opcion = input("Elige una opción: ").strip()
        if opcion == "0":
            inv.guardar()
            print("Inventario guardado. ¡Hasta pronto!")
            break
        accion = acciones.get(opcion)
        if accion is None:
            print("  ⚠ Opción no válida.")
            continue
        accion(inv)
        _pausar()


if __name__ == "__main__":
    main()
