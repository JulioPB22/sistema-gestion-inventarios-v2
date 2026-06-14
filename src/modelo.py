"""
modelo.py
=========

Define la clase :class:`Producto`, la unidad básica de información del sistema
de gestión de inventarios. Aplica principios de Programación Orientada a
Objetos (POO): encapsulamiento, validación de estado en el constructor y
serialización hacia/desde estructuras de datos nativas de Python.

Autor: Proyecto de certificación Python (nivel intermedio).
"""

from __future__ import annotations

from dataclasses import dataclass, field


class ProductoInvalidoError(ValueError):
    """Se lanza cuando los datos de un producto no cumplen las reglas de negocio."""


@dataclass
class Producto:
    """Representa un producto de la tienda de abarrotes.

    Atributos
    ---------
    nombre : str
        Nombre del producto. Actúa como identificador lógico (no se permiten
        duplicados dentro del inventario).
    precio : float
        Precio de venta unitario en pesos mexicanos (MXN). Debe ser > 0.
    stock : int
        Número de unidades disponibles. Debe ser >= 0.
    categoria : str
        Categoría comercial del producto (p. ej. "Abarrotes", "Bebidas").

    Notas
    -----
    Se usa ``@dataclass`` para reducir código repetitivo (``__init__``,
    ``__repr__`` y ``__eq__`` se generan automáticamente). La validación de
    las reglas de negocio se realiza en ``__post_init__``.
    """

    nombre: str
    precio: float
    stock: int
    categoria: str = field(default="General")

    def __post_init__(self) -> None:
        # Normalizamos el nombre (sin espacios sobrantes) para evitar duplicados
        # del tipo "Leche" vs "  leche ".
        self.nombre = str(self.nombre).strip()
        self.categoria = str(self.categoria).strip().title() or "General"

        if not self.nombre:
            raise ProductoInvalidoError("El nombre del producto no puede estar vacío.")
        if not isinstance(self.precio, (int, float)) or self.precio <= 0:
            raise ProductoInvalidoError(
                f"El precio de '{self.nombre}' debe ser un número mayor a 0 (recibido: {self.precio})."
            )
        if not isinstance(self.stock, int) or self.stock < 0:
            raise ProductoInvalidoError(
                f"El stock de '{self.nombre}' debe ser un entero mayor o igual a 0 (recibido: {self.stock})."
            )

    # ------------------------------------------------------------------ #
    # Clave de identidad: usada por el inventario para evitar duplicados. #
    # ------------------------------------------------------------------ #
    @property
    def clave(self) -> str:
        """Identificador normalizado en minúsculas (clave para sets/dicts)."""
        return self.nombre.lower()

    @property
    def valor_inventario(self) -> float:
        """Valor monetario total de las unidades en existencia (precio * stock)."""
        return round(self.precio * self.stock, 2)

    # ------------------------------------------------------------------ #
    # Serialización: necesaria para la persistencia en archivos JSON.    #
    # ------------------------------------------------------------------ #
    def a_dict(self) -> dict:
        """Convierte el producto en un diccionario (para guardar en JSON)."""
        return {
            "nombre": self.nombre,
            "precio": self.precio,
            "stock": self.stock,
            "categoria": self.categoria,
        }

    @classmethod
    def desde_dict(cls, datos: dict) -> "Producto":
        """Reconstruye un :class:`Producto` a partir de un diccionario."""
        return cls(
            nombre=datos["nombre"],
            precio=float(datos["precio"]),
            stock=int(datos["stock"]),
            categoria=datos.get("categoria", "General"),
        )

    def __str__(self) -> str:
        return (
            f"{self.nombre:<22} | ${self.precio:>8.2f} | "
            f"{self.stock:>4} u | {self.categoria}"
        )
