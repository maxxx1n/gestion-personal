# Gestion de personal - Cafeteria

Practicas Profesionalizantes II - Analisis de Sistemas y Desarrollo de Software

Dos modulos funcionales en Python (solo libreria estandar + Tkinter):

- **Empleados** (ABM): alta, modificacion, baja logica con motivo, reactivacion, busqueda y filtros.
- **Reportes** (solo lectura): totales, personal por rol y turno, altas/bajas por mes,
  antiguedad, motivos de baja y exportacion a CSV.

## Estructura
```
src/
  empleados/
    empleados.py   logica del modulo (reglas y validaciones)
    almacen.py     guardado en JSON (seguro)
  reportes/
    reportes.py    logica de reportes
  gui.py           interfaz grafica (barra lateral, tarjetas y graficos)
  main.py          punto de entrada
datos/             se crea solo; contiene empleados.json
```

## Ejecutar
```
cd src
python main.py
```
Los roles y turnos se editan en `src/empleados/empleados.py` (listas `ROLES` y `TURNOS`).

## Eliminacion definitiva (solo para pruebas)
El boton "Eliminar definitivamente" borra un empleado para siempre (pide confirmacion).
Se controla con `PERMITIR_ELIMINAR` en `src/empleados/empleados.py`:
ponerlo en `False` oculta el boton y bloquea la funcion. La baja normal sigue siendo logica.
