"""
Modulo 2: Reportes (solo lectura).
Lee la lista de empleados y calcula resumenes. Nunca modifica los datos.
"""

import csv
from datetime import date


def resumen(empleados):
    activos = sum(1 for e in empleados if e["activo"])
    return {"total": len(empleados), "activos": activos, "inactivos": len(empleados) - activos}


def contar_por(empleados, campo):
    """Cuenta empleados ACTIVOS agrupados por 'roles' (o 'rol') o por 'turno'.
    Con 'roles', quien tiene dos roles se cuenta en cada uno (la suma puede superar
    a la cantidad de activos)."""
    conteo = {}
    for e in empleados:
        if e["activo"]:
            if campo in ("rol", "roles"):
                valores = e.get("roles") or ([e["rol"]] if "rol" in e else [])
            else:
                val = e.get(campo, [])
                valores = val if isinstance(val, list) else [val]
            for valor in valores:
                conteo[valor] = conteo.get(valor, 0) + 1
    return conteo


def altas_bajas_por_mes(empleados):
    """Devuelve {'2026-10': {'altas': 2, 'bajas': 1}, ...} ordenado por mes."""
    meses = {}
    for e in empleados:
        meses.setdefault(e["fecha_ingreso"][:7], {"altas": 0, "bajas": 0})["altas"] += 1
        if e["fecha_baja"]:
            meses.setdefault(e["fecha_baja"][:7], {"altas": 0, "bajas": 0})["bajas"] += 1
    return dict(sorted(meses.items()))


def antiguedad(empleados, hoy=None):
    """Lista (nombre, meses de antiguedad) de los activos, del mas antiguo al mas nuevo."""
    hoy = hoy or date.today()
    lista = []
    for e in empleados:
        if e["activo"]:
            ing = date.fromisoformat(e["fecha_ingreso"])
            meses = (hoy.year - ing.year) * 12 + hoy.month - ing.month
            if hoy.day < ing.day:
                meses -= 1
            lista.append((e["nombre"], max(meses, 0)))
    return sorted(lista, key=lambda x: x[1], reverse=True)


def motivos_de_baja(empleados):
    """Lista (nombre, fecha de baja, motivo) de los empleados inactivos."""
    return [(e["nombre"], e["fecha_baja"], e["motivo_baja"])
            for e in empleados if not e["activo"]]


def exportar_csv(empleados, ruta):
    """Exporta todos los empleados a CSV (se abre bien en Excel)."""
    columnas = ["id", "nombre", "dni", "roles", "turno", "sucursal", "contacto",
                "fecha_ingreso", "activo", "fecha_baja", "motivo_baja"]
    with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
        escritor = csv.DictWriter(f, fieldnames=columnas, delimiter=";", extrasaction="ignore")
        escritor.writeheader()
        for e in empleados:
            fila = dict(e)
            roles = e.get("roles")
            if isinstance(roles, list):
                fila["roles"] = " / ".join(roles)
            elif roles:
                fila["roles"] = str(roles)
            elif "rol" in e:
                fila["roles"] = e["rol"]
            escritor.writerow(fila)
