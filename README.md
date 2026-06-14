# 🛒 Sistema de Gestión de Inventarios — Tienda de Abarrotes

Sistema de gestión de inventario para una pequeña tienda de abarrotes,
desarrollado en **Python** como proyecto final de una certificación de nivel
intermedio. Demuestra el uso de **Programación Orientada a Objetos (POO)**,
**estructuras de datos avanzadas** (diccionarios, conjuntos, listas),
**manipulación y análisis de datos con pandas**, **visualización con matplotlib**
y **persistencia en archivos JSON**.

---

## 📋 Características

| Punto clave | Funcionalidad |
|-------------|---------------|
| **1. Productos** | Crear productos (nombre, precio, stock, categoría) y mostrar inventario |
| **2. Operaciones** | Reabastecer, registrar ventas (descontar) y eliminar productos |
| **3. Control de datos** | Prevención de duplicados (dict + set) y reporte de bajo stock |
| **4. Persistencia** | Guardado y carga automática desde `datos/inventario.json` |
| **Extra: Datos** | Análisis Exploratorio (EDA) y limpieza de datos con **pandas** |
| **Extra: Gráficas** | Visualización estadística con **matplotlib** |

---

## 📁 Estructura del proyecto

```
.
├── src/
│   ├── modelo.py        # Clase Producto (POO + validación + serialización)
│   ├── inventario.py    # Clase Inventario (CRUD, control de datos, persistencia)
│   ├── analisis.py      # EDA, limpieza con pandas y gráficas con matplotlib
│   └── main.py          # Menú interactivo de consola (punto de entrada)
├── datos/
│   ├── inventario_muestra.csv  # Base de datos de muestra (con datos "sucios")
│   └── inventario.json         # Inventario persistente (se genera/actualiza solo)
├── graficas/            # Imágenes generadas por matplotlib
├── docs/                # Informe del proyecto (Word)
├── requirements.txt
└── README.md
```

---

## 🚀 Instalación y ejecución

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/JulioPB22/sistema-gestion-inventarios-v2.git
   cd sistema-gestion-inventarios-v2
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar el programa**
   ```bash
   python src/main.py
   ```

Para ejecutar solo el análisis de datos (EDA + limpieza + gráficas):
```bash
python src/analisis.py
```

---

## 🖥️ Uso

Al iniciar, el programa carga automáticamente el inventario guardado y muestra
un menú:

```
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
============================================================
```

Cada operación que modifica el inventario **guarda automáticamente** los cambios
en `datos/inventario.json`, garantizando la persistencia entre sesiones.

---

## 🧰 Tecnologías y conceptos aplicados

- **POO**: clases `Producto` e `Inventario`, encapsulamiento, `@dataclass`,
  `@property`, métodos de clase y validación de estado.
- **Estructuras de datos**: `dict` (acceso O(1)), `set` (control de duplicados),
  `list` (resultados ordenados).
- **pandas**: lectura de CSV, EDA (`describe`, `isna`, `duplicated`), limpieza
  (conversión de tipos, imputación, filtrado y deduplicación).
- **matplotlib**: gráficas de barras, pastel e histograma.
- **Persistencia**: serialización a JSON con manejo de errores.
- **Buenas prácticas**: *docstrings*, *type hints*, manejo de excepciones y
  separación de responsabilidades por módulo.

---

## 📄 Licencia

Proyecto educativo desarrollado con fines de certificación. Uso libre con
atribución.
