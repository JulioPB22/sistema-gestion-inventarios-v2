"""
inventario.py
=============

* **Productos**: alta de productos y consulta del inventario.
* **Operaciones**: reabastecer (sumar stock) y eliminar productos.
* **Control de datos**: prevención de duplicados (mediante un diccionario
  indexado por clave normalizada y un ``set`` de claves) y detección de
  productos con bajo stock.
* **Persistencia**: guardado y carga automática desde un archivo JSON.

Estructuras de datos empleadas
------------------------------
* ``dict``  -> acceso O(1) a cada producto por su clave normalizada.
* ``set``   -> verificación O(1) de existencia para evitar duplicados.
* ``list``  -> resultados ordenados para mostrar o graficar.
"""

from __future__ import annotations

import json
import os
from typing import Iterable

from modelo import Producto, ProductoInvalidoError


class Inventario:
    """Gestiona una colección de :class:`Producto` con persistencia en JSON.

    Parámetros
    ----------
    ruta_archivo : str
        Ruta del archivo JSON donde se guarda/carga el inventario.
    umbral_bajo_stock : int
        Nivel a partir del cual (inclusive) un producto se considera con
        "bajo stock". Por defecto 5 unidades.
    """

    def __init__(self, ruta_archivo: str = "datos/inventario.json",
                 umbral_bajo_stock: int = 5) -> None:
        self.ruta_archivo = ruta_archivo
        self.umbral_bajo_stock = umbral_bajo_stock
        # Diccionario clave_normalizada -> Producto (evita duplicados y da O(1)).
        self._productos: dict[str, Producto] = {}
        # Conjunto de claves; espejo del dict, usado para validaciones rápidas.
        self._claves: set[str] = set()
        # Carga automática al iniciar (punto clave 4: "Cargar automáticamente").
        self.cargar()

    # ===================================================================== #
    # 1. PRODUCTOS                                                          #
    # ===================================================================== #
    def agregar_producto(self, producto: Producto) -> None:
        """Da de alta un producto nuevo.

        Lanza ``ProductoInvalidoError`` si ya existe un producto con el mismo
        nombre (control de duplicados, punto clave 3).
        """
        if producto.clave in self._claves:
            raise ProductoInvalidoError(
                f"El producto '{producto.nombre}' ya existe. "
                f"Usa 'reabastecer' para aumentar su stock."
            )
        self._productos[producto.clave] = producto
        self._claves.add(producto.clave)

    def crear_producto(self, nombre: str, precio: float, stock: int,
                       categoria: str = "General") -> Producto:
        """Atajo: crea un :class:`Producto` y lo agrega al inventario."""
        producto = Producto(nombre=nombre, precio=precio, stock=stock,
                            categoria=categoria)
        self.agregar_producto(producto)
        return producto

    def obtener(self, nombre: str) -> Producto | None:
        """Devuelve el producto por nombre (sin distinguir mayúsculas) o None."""
        return self._productos.get(nombre.strip().lower())

    def listar(self) -> list[Producto]:
        """Lista de productos ordenada alfabéticamente por nombre."""
        return sorted(self._productos.values(), key=lambda p: p.nombre.lower())

    def mostrar_inventario(self) -> str:
        """Devuelve una tabla en texto con todo el inventario."""
        if not self._productos:
            return "(El inventario está vacío)"
        encabezado = (
            f"{'PRODUCTO':<22} | {'PRECIO':>9} | {'STOCK':>6} | CATEGORÍA\n"
            + "-" * 64
        )
        filas = [str(p) for p in self.listar()]
        total = self.valor_total_inventario()
        pie = "-" * 64 + f"\nValor total del inventario: ${total:,.2f} MXN"
        return "\n".join([encabezado, *filas, pie])

    # ===================================================================== #
    # 2. OPERACIONES                                                        #
    # ===================================================================== #
    def reabastecer(self, nombre: str, cantidad: int) -> Producto:
        """Suma ``cantidad`` unidades al stock de un producto existente."""
        if cantidad <= 0:
            raise ValueError("La cantidad a reabastecer debe ser mayor a 0.")
        producto = self.obtener(nombre)
        if producto is None:
            raise KeyError(f"No existe el producto '{nombre}'.")
        producto.stock += cantidad
        return producto

    def descontar(self, nombre: str, cantidad: int) -> Producto:
        """Resta ``cantidad`` unidades (p. ej. tras una venta)."""
        if cantidad <= 0:
            raise ValueError("La cantidad a descontar debe ser mayor a 0.")
        producto = self.obtener(nombre)
        if producto is None:
            raise KeyError(f"No existe el producto '{nombre}'.")
        if cantidad > producto.stock:
            raise ValueError(
                f"Stock insuficiente de '{producto.nombre}': "
                f"hay {producto.stock}, se intenta descontar {cantidad}."
            )
        producto.stock -= cantidad
        return producto

    def eliminar(self, nombre: str) -> Producto:
        """Elimina un producto del inventario y lo devuelve."""
        clave = nombre.strip().lower()
        if clave not in self._claves:
            raise KeyError(f"No existe el producto '{nombre}'.")
        producto = self._productos.pop(clave)
        self._claves.discard(clave)
        return producto

    # ===================================================================== #
    # 3. CONTROL DE DATOS                                                   #
    # ===================================================================== #
    def existe(self, nombre: str) -> bool:
        """True si ya hay un producto con ese nombre (control de duplicados)."""
        return nombre.strip().lower() in self._claves

    def productos_bajo_stock(self) -> list[Producto]:
        """Productos cuyo stock es <= umbral, ordenados de menor a mayor."""
        bajos = [p for p in self._productos.values()
                 if p.stock <= self.umbral_bajo_stock]
        return sorted(bajos, key=lambda p: p.stock)

    def categorias(self) -> set[str]:
        """Conjunto de categorías presentes (uso de set)."""
        return {p.categoria for p in self._productos.values()}

    def valor_total_inventario(self) -> float:
        """Suma del valor (precio * stock) de todos los productos."""
        return round(sum(p.valor_inventario for p in self._productos.values()), 2)

    # ===================================================================== #
    # 4. PERSISTENCIA                                                       #
    # ===================================================================== #
    def guardar(self) -> None:
        """Guarda el inventario completo en el archivo JSON."""
        carpeta = os.path.dirname(self.ruta_archivo)
        if carpeta:
            os.makedirs(carpeta, exist_ok=True)
        datos = [p.a_dict() for p in self.listar()]
        with open(self.ruta_archivo, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)

    def cargar(self) -> None:
        """Carga el inventario desde el archivo JSON si existe.

        Si el archivo no existe (primer arranque) o está corrupto, el
        inventario inicia vacío sin interrumpir el programa.
        """
        if not os.path.exists(self.ruta_archivo):
            return
        try:
            with open(self.ruta_archivo, "r", encoding="utf-8") as f:
                datos = json.load(f)
        except (json.JSONDecodeError, OSError):
            # Archivo dañado: se ignora y se continúa con inventario vacío.
            return
        for registro in datos:
            try:
                producto = Producto.desde_dict(registro)
                self._productos[producto.clave] = producto
                self._claves.add(producto.clave)
            except (ProductoInvalidoError, KeyError, ValueError):
                # Se omiten registros inválidos para no romper la carga.
                continue

    def cargar_desde_iterable(self, productos: Iterable[Producto]) -> int:
        """Carga productos ya limpios (p. ej. tras el preprocesamiento con
        pandas). Devuelve cuántos se agregaron (omite duplicados)."""
        agregados = 0
        for producto in productos:
            if not self.existe(producto.nombre):
                self.agregar_producto(producto)
                agregados += 1
        return agregados

    # ----------------------------------------------------------------- #
    def __len__(self) -> int:
        return len(self._productos)

    def __contains__(self, nombre: str) -> bool:
        return self.existe(nombre)
