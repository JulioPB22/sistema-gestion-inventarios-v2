"""
analisis.py
===========

Módulo de **Análisis Exploratorio de Datos (EDA)**, **limpieza/preprocesamiento**
con ``pandas`` y **visualización estadística** con ``matplotlib``.

Demuestra buenas prácticas de manejo de datos sobre una base de muestra
(``datos/inventario_muestra.csv``) que contiene errores típicos de captura
manual en una tienda:

* Espacios sobrantes y mayúsculas/minúsculas inconsistentes.
* Filas duplicadas ("Leche Lala 1L" repetida; "Coca-Cola" con distinto formato).
* Valores faltantes en la columna ``stock``.
* Valores no numéricos ("abc") y negativos (stock = -3).
* Nombres vacíos.

Funciones principales
---------------------
* :func:`cargar_datos`         -> lee el CSV en un DataFrame.
* :func:`explorar`             -> imprime el diagnóstico exploratorio.
* :func:`limpiar`              -> devuelve un DataFrame limpio y validado.
* :func:`a_productos`          -> convierte el DataFrame limpio en objetos Producto.
* :func:`graficar_*`           -> genera gráficas con matplotlib.
"""

from __future__ import annotations

import os

import matplotlib

# Backend no interactivo: permite guardar imágenes sin abrir ventanas (útil en
# servidores o al ejecutar de forma automatizada).
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from modelo import Producto  # noqa: E402

RUTA_CSV = "datos/inventario_muestra.csv"
CARPETA_GRAFICAS = "graficas"


# ===================================================================== #
# 1. CARGA Y EXPLORACIÓN                                                #
# ===================================================================== #
def cargar_datos(ruta: str = RUTA_CSV) -> pd.DataFrame:
    """Lee la base de datos de muestra en un ``DataFrame`` de pandas."""
    return pd.read_csv(ruta)


def explorar(df: pd.DataFrame) -> None:
    """Imprime un diagnóstico exploratorio del DataFrame (EDA).

    Muestra dimensiones, tipos de dato, primeras filas, estadísticos
    descriptivos, valores faltantes y duplicados. No modifica los datos.
    """
    print("=" * 60)
    print("ANÁLISIS EXPLORATORIO DE DATOS (EDA)")
    print("=" * 60)
    print(f"\n• Dimensiones (filas, columnas): {df.shape}")
    print(f"\n• Tipos de dato por columna:\n{df.dtypes}")
    print(f"\n• Primeras 5 filas:\n{df.head()}")
    print(f"\n• Valores faltantes por columna:\n{df.isna().sum()}")

    # Duplicados detectados al normalizar el nombre (minúsculas + sin espacios).
    nombres_norm = df["nombre"].astype(str).str.strip().str.lower()
    n_dups = int(nombres_norm.duplicated().sum())
    print(f"\n• Filas duplicadas por nombre (normalizado): {n_dups}")

    # describe() solo tiene sentido en columnas numéricas; forzamos numérico.
    precio_num = pd.to_numeric(df["precio"], errors="coerce")
    print(f"\n• Estadísticos de 'precio':\n{precio_num.describe()}")
    print("=" * 60)


# ===================================================================== #
# 2. LIMPIEZA Y PREPROCESAMIENTO                                        #
# ===================================================================== #
def limpiar(df: pd.DataFrame, umbral_bajo_stock: int = 5) -> pd.DataFrame:
    """Aplica el pipeline de limpieza y devuelve un DataFrame válido.

    Pasos
    -----
    1. Normaliza textos (``strip`` y formato de mayúsculas).
    2. Convierte ``precio`` y ``stock`` a numéricos (no válidos -> NaN).
    3. Imputa el ``stock`` faltante con 0 (regla de negocio: si no se capturó,
       se asume agotado hasta verificar físicamente).
    4. Descarta filas inválidas: nombre vacío, precio <= 0 o nulo, stock < 0.
    5. Elimina duplicados conservando la primera aparición.
    """
    df = df.copy()

    # --- 1. Normalización de texto ---
    df["nombre"] = df["nombre"].astype(str).str.strip()
    df["categoria"] = (
        df["categoria"].astype(str).str.strip().str.title().replace("Nan", "General")
    )
    df["nombre_norm"] = df["nombre"].str.lower()

    # --- 2. Conversión de tipos (valores no numéricos -> NaN) ---
    df["precio"] = pd.to_numeric(df["precio"], errors="coerce")
    df["stock"] = pd.to_numeric(df["stock"], errors="coerce")

    # --- 3. Imputación del stock faltante ---
    df["stock"] = df["stock"].fillna(0)

    # --- 4. Filtrado de filas inválidas ---
    antes = len(df)
    df = df[df["nombre_norm"] != ""]          # nombre no vacío
    df = df[df["nombre_norm"] != "nan"]
    df = df[df["precio"].notna() & (df["precio"] > 0)]  # precio válido
    df = df[df["stock"] >= 0]                  # stock no negativo
    df["stock"] = df["stock"].astype(int)

    # --- 5. Eliminación de duplicados (primera aparición) ---
    df = df.drop_duplicates(subset="nombre_norm", keep="first")
    despues = len(df)

    print(f"\nLimpieza: {antes} filas originales -> {despues} filas válidas "
          f"({antes - despues} descartadas/duplicadas).")

    return df.drop(columns="nombre_norm").reset_index(drop=True)


def a_productos(df: pd.DataFrame) -> list[Producto]:
    """Convierte el DataFrame limpio en una lista de objetos :class:`Producto`."""
    productos: list[Producto] = []
    for _, fila in df.iterrows():
        productos.append(
            Producto(
                nombre=fila["nombre"],
                precio=float(fila["precio"]),
                stock=int(fila["stock"]),
                categoria=fila["categoria"],
            )
        )
    return productos


# ===================================================================== #
# 3. VISUALIZACIÓN ESTADÍSTICA (matplotlib)                            #
# ===================================================================== #
def _asegurar_carpeta(carpeta: str = CARPETA_GRAFICAS) -> str:
    os.makedirs(carpeta, exist_ok=True)
    return carpeta


def graficar_stock_por_producto(df: pd.DataFrame,
                                 umbral_bajo_stock: int = 5,
                                 carpeta: str = CARPETA_GRAFICAS) -> str:
    """Gráfica de barras del stock por producto, resaltando el bajo stock."""
    _asegurar_carpeta(carpeta)
    datos = df.sort_values("stock")
    colores = ["#d9534f" if s <= umbral_bajo_stock else "#5cb85c"
               for s in datos["stock"]]

    plt.figure(figsize=(10, 7))
    plt.barh(datos["nombre"], datos["stock"], color=colores)
    plt.axvline(umbral_bajo_stock, color="#333", linestyle="--",
                label=f"Umbral bajo stock ({umbral_bajo_stock})")
    plt.title("Existencias por producto (rojo = bajo stock)")
    plt.xlabel("Unidades en stock")
    plt.ylabel("Producto")
    plt.legend()
    plt.tight_layout()
    ruta = os.path.join(carpeta, "stock_por_producto.png")
    plt.savefig(ruta, dpi=120)
    plt.close()
    return ruta


def graficar_valor_por_categoria(df: pd.DataFrame,
                                 carpeta: str = CARPETA_GRAFICAS) -> str:
    """Gráfica de pastel del valor monetario del inventario por categoría."""
    _asegurar_carpeta(carpeta)
    df = df.copy()
    df["valor"] = df["precio"] * df["stock"]
    por_cat = df.groupby("categoria")["valor"].sum().sort_values(ascending=False)

    plt.figure(figsize=(8, 8))
    plt.pie(por_cat, labels=por_cat.index, autopct="%1.1f%%", startangle=90)
    plt.title("Distribución del valor del inventario por categoría")
    plt.tight_layout()
    ruta = os.path.join(carpeta, "valor_por_categoria.png")
    plt.savefig(ruta, dpi=120)
    plt.close()
    return ruta


def graficar_distribucion_precios(df: pd.DataFrame,
                                  carpeta: str = CARPETA_GRAFICAS) -> str:
    """Histograma de la distribución de precios de los productos."""
    _asegurar_carpeta(carpeta)
    plt.figure(figsize=(9, 6))
    plt.hist(df["precio"], bins=8, color="#0275d8", edgecolor="white")
    plt.title("Distribución de precios del inventario")
    plt.xlabel("Precio (MXN)")
    plt.ylabel("Número de productos")
    plt.tight_layout()
    ruta = os.path.join(carpeta, "distribucion_precios.png")
    plt.savefig(ruta, dpi=120)
    plt.close()
    return ruta


def generar_todas_las_graficas(df: pd.DataFrame,
                               umbral_bajo_stock: int = 5) -> list[str]:
    """Genera todas las gráficas y devuelve las rutas de los archivos."""
    return [
        graficar_stock_por_producto(df, umbral_bajo_stock),
        graficar_valor_por_categoria(df),
        graficar_distribucion_precios(df),
    ]


# ===================================================================== #
# Ejecución directa: demostración del flujo EDA -> limpieza -> gráficas #
# ===================================================================== #
if __name__ == "__main__":
    datos = cargar_datos()
    explorar(datos)
    limpio = limpiar(datos)
    print("\nDatos limpios:")
    print(limpio.to_string(index=False))
    rutas = generar_todas_las_graficas(limpio)
    print("\nGráficas generadas:")
    for r in rutas:
        print(f"  - {r}")
