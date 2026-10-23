"""Persistencia de empleados en un archivo JSON."""

import json
import os
import shutil
try:
    from .empleados import SUCURSALES
except ImportError:
    from empleados import SUCURSALES

# Carpeta "datos" en la raiz del proyecto (se crea sola)
RUTA = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), "datos", "empleados.json")


def _migrar(empleados):
    """Datos viejos: el campo 'rol' (texto) pasa a ser la lista 'roles' y mantiene 'rol'."""
    for e in empleados:
        if "roles" not in e:
            e["roles"] = [e["rol"]] if "rol" in e else []
        if "rol" not in e and e.get("roles"):
            e["rol"] = e["roles"][0]
        if "sucursal" not in e:
            e["sucursal"] = SUCURSALES[0]
    return empleados


def cargar(ruta=RUTA):
    """Devuelve la lista de empleados. Si el archivo no existe, devuelve []."""
    if not os.path.exists(ruta):
        return []
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return _migrar(json.load(f))
    except json.JSONDecodeError:
        # No devolvemos [] en silencio: el siguiente guardado borraria todo.
        copia = ruta + ".danado"
        shutil.copy2(ruta, copia)
        raise ValueError(f"El archivo de datos esta danado. Se guardo una copia en: {copia}")


def guardar(empleados, ruta=RUTA):
    """Guarda la lista de forma segura: copia de respaldo + escritura en archivo temporal."""
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    if os.path.exists(ruta):
        shutil.copy2(ruta, ruta + ".bak")
    temporal = ruta + ".tmp"
    with open(temporal, "w", encoding="utf-8") as f:
        json.dump(empleados, f, indent=2, ensure_ascii=False)
    os.replace(temporal, ruta)  # reemplazo atomico: nunca queda un archivo a medio escribir
