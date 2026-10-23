# Documentación del proyecto: Cafetería Magnolia

## 1. Descripción general

Este proyecto es una aplicación de escritorio desarrollada en Python con Tkinter para gestionar el personal de una cafetería. La lógica se divide en tres capas principales:

- Lógica del dominio: operaciones de empleados y validaciones.
- Persistencia: almacenamiento en JSON.
- Presentación: interfaz gráfica con formularios, tablas, filtros y reportes.

La aplicación permite:

- dar de alta empleados,
- modificar sus datos,
- dar de baja lógica con motivo,
- reactivar empleados,
- eliminar definitivamente registros (modo de prueba controlado por configuración),
- buscar y filtrar por rol, sucursal, nombre/DNI y estado,
- visualizar reportes resumidos,
- exportar la información a CSV.

El proyecto está pensado como una práctica orientada a mantener un código modular y fácil de entender, donde cada módulo tiene una responsabilidad clara.

---

## 2. Estructura del proyecto

```text
cafeteria/
├── README.md
├── DOCUMENTACION_PROYECTO.md
├── src/
│   ├── main.py
│   ├── gui.py
│   ├── assets/
│   │   └── magnolia.png
│   ├── empleados/
│   │   ├── __init__.py
│   │   ├── almacen.py
│   │   └── empleados.py
│   └── reportes/
│       ├── __init__.py
│       └── reportes.py
└── datos/
    └── empleados.json   (se crea automáticamente si no existe)
```

### Explicación de cada archivo

#### `src/main.py`
Es el punto de entrada de la aplicación.

Su flujo es:

1. intenta cargar los datos desde el archivo JSON,
2. si el archivo está corrupto, muestra un error y termina la ejecución,
3. si todo está bien, crea la instancia de `App` y lanza el loop principal de Tkinter.

Es el único lugar que inicia la aplicación y no contiene lógica de negocio.

#### `src/assets/magnolia.png`
Logo e imagen institucional de la cafetería. Es cargado dinámicamente por la interfaz gráfica (`gui.py`) para decorar la barra lateral izquierda y establecer el ícono representativo de la ventana principal de la aplicación.

#### `src/gui.py`
Contiene toda la interfaz gráfica de la aplicación.

Aquí se definen:

- estilos visuales (paleta café/crema basada en tonos espresso, mudo, acento y crema),
- componentes reutilizables (`boton`, `entrada`, `tarjeta`, `tabla`, etc.),
- carga y escalado del logo institucional,
- gráficos con `Canvas` (barras horizontales y barras mensuales comparativas),
- formulario modal para crear o modificar empleados con selección de sucursal y casillas para roles combinables,
- vista de empleados (con filtros por texto, rol, sucursal y estado, y acciones CRUD),
- vista de reportes (indicadores KPI, gráficos y tablas de antigüedad y motivos de baja),
- barra lateral de navegación con botones interactivos,
- ventana principal `App`.

La UI usa Tkinter y organiza la experiencia en dos vistas principales:

- Empleados: CRUD del personal.
- Reportes: resumen, gráficos y exportación.

#### `src/empleados/empleados.py`
Es el módulo central de la lógica del negocio.

Aquí se implementan todas las reglas de validación y las operaciones sobre la estructura de datos. Es un módulo “puro”: no toca archivos ni interfaz gráfica. Trabaja sobre una lista de diccionarios.

Incluye:

- constantes `ROLES`, `ROLES_COMBINABLES`, `TURNOS`, `SUCURSALES` y `PERMITIR_ELIMINAR`,
- normalización de texto para búsquedas sin tildes,
- búsqueda por ID,
- validación de nombre, DNI, roles combinables, turno y sucursal,
- alta, modificación, baja lógica, reactivación y eliminación física opcional,
- búsqueda y filtros avanzados.

#### `src/empleados/almacen.py`
Es la capa de persistencia.

Se encarga de:

- cargar los empleados desde `datos/empleados.json`,
- migrar automáticamente esquemas anteriores mediante `_migrar` (convirtiendo `rol` individual a lista `roles` y asignando sucursal por defecto),
- guardar la lista en formato JSON,
- crear respaldo (`.bak`) y escritura atómica temporal (`.tmp` con `os.replace`) para evitar corrupción,
- avisar si el archivo está dañado guardando una copia `.danado`.

La estrategia es segura: si el archivo JSON falla al parsearse, se guarda una copia llamada `empleados.json.danado` y se lanza un `ValueError` para que la aplicación no continúe con datos potencialmente corruptos.

#### `src/reportes/reportes.py`
Este módulo contiene todas las consultas y cálculos de reportes.

Su propósito es ser de solo lectura: no cambia la información, solo la analiza.

Genera resultados como:

- total de empleados,
- activos e inactivos,
- conteo por rol (soporta tanto empleados con rol único como múltiples roles combinados),
- conteo por turno,
- altas y bajas por mes,
- antigüedad del personal activo,
- motivos de baja,
- exportación a CSV incluyendo información completa (roles y sucursal).

#### `src/empleados/__init__.py` y `src/reportes/__init__.py`
Son archivos de inicialización del paquete. No agregan lógica funcional compleja; sirven para identificar cada módulo como paquete Python.

---

## 3. Modelo de datos

Los empleados se almacenan como una lista de diccionarios. Cada empleado tiene esta estructura:

```python
{
    "id": 1,
    "nombre": "Ana García",
    "dni": "30123456",
    "rol": "mozo",
    "roles": ["mozo"],
    "turno": "mañana",
    "sucursal": "Magnolia Central",
    "contacto": "11 5555-1234",
    "fecha_ingreso": "2024-01-15",
    "activo": True,
    "fecha_baja": None,
    "motivo_baja": ""
}
```

### Campos relevantes

- `id`: identificador único del empleado (entero incremental).
- `nombre`: nombre y apellido (solo letras, espacios y puntuación habitual, sin números).
- `dni`: documento de identidad, validado con longitud de 7 u 8 dígitos numéricos.
- `rol`: rol principal (mantenido por compatibilidad con consultas individuales).
- `roles`: lista de roles asignados. Opciones: `mozo`, `cocinero`, `encargado`. Permite asignación múltiple para roles combinables (`mozo` y `encargado`).
- `turno`: turno laboral, uno de `mañana`, `tarde`, `ambos`.
- `sucursal`: sucursal asignada (`Magnolia Central`, `Magnolia Bar`, `Magnolia Cpo. Santo`).
- `contacto`: dato de contacto o teléfono (opcional).
- `fecha_ingreso`: fecha de alta en formato ISO (`YYYY-MM-DD`).
- `activo`: booleano que indica si el empleado se encuentra activo (`True`) o inactivo (`False`).
- `fecha_baja`: fecha en la que fue dado de baja (`None` si está activo).
- `motivo_baja`: texto explicativo de la baja lógica.

La baja no elimina registros por defecto; simplemente marca al empleado como inactivo y conserva el historial.

---

## 4. Lógica de negocio del módulo `empleados.py`

### 4.1 Validaciones

La función `_validar(empleados, nombre, dni, roles, turno, sucursal=None, id_actual=None)` verifica lo siguiente:

- que el nombre no esté vacío y no contenga números ni símbolos no permitidos,
- que el DNI contenga solo números y tenga 7 u 8 caracteres,
- que el DNI no esté duplicado con otro empleado existente (salvo el propio empleado si se está modificando),
- que se haya seleccionado al menos un rol y que todos pertenezcan a `ROLES`,
- que la combinación de roles sea válida: únicamente los roles en `ROLES_COMBINABLES` (`mozo` y `encargado`) pueden coexistir en un mismo empleado (el cocinero es un rol exclusivo),
- que el turno pertenezca a `TURNOS` (`mañana`, `tarde`, `ambos`),
- que la sucursal sea válida de acuerdo a `SUCURSALES` (`Magnolia Central`, `Magnolia Bar`, `Magnolia Cpo. Santo`).

Si algo falla, lanza un `ValueError` con un mensaje descriptivo para el usuario.

### 4.2 Alta de empleados

La función `alta(empleados, nombre, dni, roles, turno, sucursal=None, contacto="", fecha_ingreso=None)`:

1. normaliza espacios en blanco del nombre, DNI y contacto,
2. admite `roles` tanto en formato de lista como string individual (convirtiéndolo a lista),
3. asigna la sucursal por defecto si no se especifica,
4. llama a `_validar(...)`,
5. genera un nuevo ID como `max(id) + 1`,
6. crea el registro con todos sus campos (incluyendo `roles`, `rol`, `sucursal` y estado activo),
7. agrega el registro a la lista y lo devuelve.

### 4.3 Modificación

`modificar(empleados, id_empleado, nombre, dni, roles, turno, sucursal=None, contacto="")`:

1. busca al empleado por su ID (lanza `ValueError` si no existe),
2. limpia espacios y valida los nuevos datos contra los demás empleados,
3. actualiza nombre, DNI, roles ordenados, rol principal, turno, sucursal y contacto,
4. no altera el historial de fechas de ingreso/baja ni el estado de actividad.

### 4.4 Baja lógica

`baja(empleados, id_empleado, motivo, fecha=None)`:

No borra el registro de la lista. Solo se ejecuta si el empleado está actualmente activo, requiere obligatoriamente un motivo y actualiza:

- `activo = False`,
- `fecha_baja = fecha` (o la fecha del día en formato ISO),
- `motivo_baja = motivo.strip()`.

### 4.5 Reactivación

`reactivar(empleados, id_empleado)`:

Invierte la baja lógica para un empleado inactivo:

- `activo = True`,
- `fecha_baja = None`,
- `motivo_baja = ""`.

### 4.6 Búsqueda y filtros

`buscar(empleados, texto="", rol=None, estado="activos", sucursal=None)`:

Filtra empleados combinando:

- texto: busca coincidencias parciales en el nombre (normalizando tildes mediante `_sin_tildes`) o coincidencia en el DNI,
- rol opcional: filtra si el empleado posee dicho rol,
- sucursal opcional: filtra por la sucursal asignada,
- estado: filtra por `'activos'`, `'inactivos'` o `'todos'`.

### 4.7 Eliminación definitiva (Modo de pruebas)

`eliminar(empleados, id_empleado)`:

Elimina permanentemente el registro de la lista de empleados (borrado físico sin historial).
- Está condicionada por la constante `PERMITIR_ELIMINAR = True`. Si está en `False`, arroja un error impidiendo el borrado.
- En la interfaz gráfica se controla mostrando u ocultando el botón "Eliminar definitivamente" y solicitando confirmación de seguridad antes de proceder.

---

## 5. Lógica de persistencia

La persistencia usa JSON como formato de almacenamiento simple, portable y legible.

El archivo se almacena en:

```text
../datos/empleados.json
```

El módulo `almacen.py` gestiona:

- **Carga de datos (`cargar`)**: si el archivo no existe devuelve `[]`. Si existe, lo lee y ejecuta `_migrar(...)`. Si el JSON está dañado, crea una copia de seguridad `empleados.json.danado` y lanza un `ValueError` preventivo para no perder datos.
- **Migración de esquema (`_migrar`)**: garantiza retrocompatibilidad en caso de datos con esquemas previos, transformando el campo `rol` individual en lista `roles` y asignando la sucursal predeterminada.
- **Escritura segura (`guardar`)**:
  1. genera una copia de respaldo `.bak` si el archivo previo existe,
  2. escribe el nuevo contenido en un archivo temporal `.tmp`,
  3. realiza un reemplazo atómico mediante `os.replace(...)` para evitar archivos truncados o corruptos si ocurre un corte imprevisto.

---

## 6. Lógica de reportes

El módulo `reportes.py` es una capa analítica de solo lectura que procesa la colección de empleados sin mutarla.

### Funciones principales

#### `resumen(empleados)`
Devuelve un diccionario con:
- `total`: total de empleados registrados,
- `activos`: cantidad de empleados activos,
- `inactivos`: cantidad de empleados inactivos.

#### `contar_por(empleados, campo)`
Cuenta empleados activos agrupados por:
- `'roles'` (o `'rol'`): cuenta cada rol presente (si un empleado posee dos roles combinados, suma a cada uno),
- `'turno'`: agrupa por turno laboral.

#### `altas_bajas_por_mes(empleados)`
Agrupa cronológicamente altas y bajas por mes en un diccionario ordenado (`{'YYYY-MM': {'altas': X, 'bajas': Y}}`). Se utiliza directamente para renderizar el gráfico comparativo mensual.

#### `antiguedad(empleados, hoy=None)`
Calcula la antigüedad en meses de cada empleado activo calculando la diferencia exacta con la fecha actual, y devuelve una lista de tuplas `(nombre, meses)` ordenada de mayor a menor antigüedad.

#### `motivos_de_baja(empleados)`
Devuelve una lista de tuplas `(nombre, fecha_baja, motivo_baja)` con el detalle de todos los empleados dados de baja.

#### `exportar_csv(empleados, ruta)`
Exporta la nómina completa a un archivo delimitado por punto y coma (`;`) y codificado en `utf-8-sig` (compatible con Microsoft Excel y hojas de cálculo), incluyendo columnas: `id`, `nombre`, `dni`, `roles`, `turno`, `sucursal`, `contacto`, `fecha_ingreso`, `activo`, `fecha_baja` y `motivo_baja`.

---

## 7. Flujo de la interfaz gráfica

### 7.1 Arranque

`main.py` intenta cargar los datos con `almacen.cargar()`. Si ocurre un error de corrupción muestra un mensaje de diálogo y detiene el proceso; si es exitoso, inicializa `App(datos)` y ejecuta el `mainloop()` de Tkinter.

### 7.2 Ventana principal

La clase `App(tk.Tk)` define:

- Barra lateral izquierda en tono espresso: muestra el logo de la cafetería (`magnolia.png`) o título estilizado, y botones de navegación rápida.
- Contenedor central con alternancia de vistas mediante `mostrar(clave)`.
- Persistencia centralizada con `app.guardar()`.

### 7.3 Vista `VistaEmpleados`

Esta vista proporciona la gestión integral del personal:

- Encabezado con título descriptivo y botón "+ Nuevo empleado".
- Barra de filtros en tarjeta blanca: búsqueda reactiva por texto (nombre/DNI), filtro por Rol, filtro por Sucursal y filtro por Estado (`activos`, `inactivos`, `todos`).
- Tabla principal con estilo personalizado y scrollbar vertical (resalta filas pares e inactivos).
- Pie con contador dinámico de resultados y botones de acción: "Modificar", "Dar de baja" (solicita motivo), "Reactivar" y "Eliminar definitivamente" (visible si `PERMITIR_ELIMINAR` está habilitado).

### 7.4 Formulario `FormEmpleado`

Ventana modal secundaria (`Toplevel`) para altas y modificaciones:

- Campos: Nombre y apellido, DNI, Contacto, Roles (casillas de verificación con ajuste automático para solo permitir combinaciones autorizadas), Turno y Sucursal.
- Al guardar valida los datos; ante cualquier error muestra un diálogo de advertencia sin cerrar la ventana ni perder lo ingresado.

### 7.5 Vista `VistaReportes`

Presenta un tablero de control analítico:

- Cuatro tarjetas KPI: Total, Activos, Inactivos y Antigüedad promedio.
- Tres paneles gráficos en Canvas: Personal por rol, Personal por turno y Gráfico de barras agrupadas de altas y bajas de los últimos 6 meses.
- Dos tablas de detalle con scroll: Antigüedad del personal activo (mostrando años y meses) y Registro histórico de motivos de baja.
- Botones de actualización manual y exportación directa a CSV.

---

## 8. Separación de responsabilidades

La aplicación tiene una arquitectura simple pero clara:

- `empleados.py`: reglas del negocio.
- `almacen.py`: almacenamiento persistente.
- `reportes.py`: análisis de datos.
- `gui.py`: interfaz, interacción, componentes visuales.
- `main.py`: arranque de la app.

Esto significa que:

- la lógica no depende de Tkinter,
- los reportes no escriben ni modifican datos,
- la UI no conoce cómo se guardan los empleados internamente,
- la aplicación es más fácil de mantener y ampliar.

---

## 9. Cómo se ejecuta

Desde la carpeta `src`, se lanza:

```bash
python main.py
```

El proyecto ya está preparado para funcionar sin instalar librerías adicionales, porque usa solo la librería estándar de Python y Tkinter.

---

## 10. Conclusión

Este proyecto sigue una estructura muy limpia para una app de gestión pequeña:

- lógica de empleado centralizada,
- archivo JSON como almacenamiento persistente,
- reportes calculados a partir de los mismos datos,
- interfaz gráfica para manejar todo sin tocar código.

La solución demuestra una buena separación de responsabilidades y una implementación práctica para administrar personal en un entorno de cafetería.
