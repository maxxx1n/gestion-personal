"""
Modulo 1: Gestion de Empleados (ABM).
Logica pura: trabaja sobre una lista de diccionarios, sin archivos ni pantallas.
"""

import unicodedata
from datetime import date

ROLES = ["mozo", "cocinero", "encargado"]   # para agregar un rol, sumarlo aca
# Solo estos roles se pueden combinar (rotan segun el dia). El cocinero es fijo.
ROLES_COMBINABLES = ["mozo", "encargado"]
TURNOS = ["mañana", "tarde", "ambos"]
SUCURSALES = ["Magnolia Central", "Magnolia Bar", "Magnolia Cpo. Santo"]

# Eliminacion definitiva (borra el registro para siempre). Sirve para las pruebas.
# En produccion conviene ponerla en False: la baja normal es siempre logica.
PERMITIR_ELIMINAR = True


def _sin_tildes(texto):
    """Pasa a minusculas y saca tildes, para buscar sin distinguir."""
    normal = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in normal if unicodedata.category(c) != "Mn")


def buscar_por_id(empleados, id_empleado):
    for e in empleados:
        if e["id"] == id_empleado:
            return e
    return None


def _nombre_valido(nombre):
    """El nombre solo puede tener letras (con tildes o ñ), espacios, guion, apostrofe y punto."""
    return (all(c.isalpha() or c in " -'." for c in nombre)
            and any(c.isalpha() for c in nombre))


def _ordenar_roles(roles):
    """Saca repetidos y deja los roles en el orden de la lista ROLES."""
    return [r for r in ROLES if r in roles]


def _validar(empleados, nombre, dni, roles, turno, sucursal=None, id_actual=None):
    """Valida los datos. Lanza ValueError con un mensaje claro si algo esta mal."""
    if not nombre.strip():
        raise ValueError("El nombre no puede estar vacio.")
    if not _nombre_valido(nombre.strip()):
        raise ValueError("El nombre solo puede tener letras y espacios (sin numeros ni simbolos).")
    if not (dni.isdigit() and 7 <= len(dni) <= 8):
        raise ValueError("El DNI debe tener 7 u 8 numeros, sin puntos.")
    for e in empleados:
        if e["dni"] == dni and e["id"] != id_actual:
            raise ValueError(f"Ya existe un empleado con el DNI {dni} ({e['nombre']}).")
    if isinstance(roles, str):
        roles = [roles]
    if not roles:
        raise ValueError("Elegi al menos un rol.")
    for rol in roles:
        if rol not in ROLES:
            raise ValueError(f"Rol invalido. Opciones: {', '.join(ROLES)}.")
    elegidos = set(roles)
    if len(elegidos) > 1 and not elegidos <= set(ROLES_COMBINABLES):
        raise ValueError("Solo se pueden combinar los roles: "
                         f"{' y '.join(ROLES_COMBINABLES)}. El resto tiene un unico rol.")
    if turno not in TURNOS:
        raise ValueError(f"Turno invalido. Opciones: {', '.join(TURNOS)}.")
    if sucursal is not None and sucursal not in SUCURSALES:
        raise ValueError(f"Sucursal Invalida. Opciones: {', '.join(SUCURSALES)}.")


def alta(empleados, nombre, dni, roles, turno, sucursal=None, contacto="", fecha_ingreso=None):
    """Agrega un empleado nuevo y lo devuelve."""
    nombre, dni, contacto = " ".join(nombre.split()), dni.strip(), contacto.strip()
    if isinstance(roles, str):
        roles = [roles]
    sucursal = sucursal or SUCURSALES[0]
    _validar(empleados, nombre, dni, roles, turno, sucursal)
    lista_roles = _ordenar_roles(roles)
    nuevo = {
        "id": max((e["id"] for e in empleados), default=0) + 1,
        "nombre": nombre,
        "dni": dni,
        "rol": lista_roles[0] if lista_roles else "",
        "roles": lista_roles,
        "turno": turno,
        "sucursal": sucursal,
        "contacto": contacto,
        "fecha_ingreso": fecha_ingreso or date.today().isoformat(),
        "activo": True,
        "fecha_baja": None,
        "motivo_baja": "",
    }
    empleados.append(nuevo)
    return nuevo


def modificar(empleados, id_empleado, nombre, dni, roles, turno, sucursal=None, contacto=""):
    """Cambia los datos de un empleado existente."""
    emp = buscar_por_id(empleados, id_empleado)
    if emp is None:
        raise ValueError("El empleado no existe.")
    nombre, dni, contacto = " ".join(nombre.split()), dni.strip(), contacto.strip()
    if isinstance(roles, str):
        roles = [roles]
    sucursal = sucursal or emp.get("sucursal", SUCURSALES[0])
    _validar(empleados, nombre, dni, roles, turno, sucursal, id_actual=id_empleado)
    lista_roles = _ordenar_roles(roles)
    emp.update(
        nombre=nombre,
        dni=dni,
        rol=lista_roles[0] if lista_roles else "",
        roles=lista_roles,
        turno=turno,
        sucursal=sucursal,
        contacto=contacto
    )
    return emp


def baja(empleados, id_empleado, motivo, fecha=None):
    """Baja logica: el empleado queda inactivo pero su historial se conserva."""
    emp = buscar_por_id(empleados, id_empleado)
    if emp is None:
        raise ValueError("El empleado no existe.")
    if not emp["activo"]:
        raise ValueError("El empleado ya estaba dado de baja.")
    if not motivo.strip():
        raise ValueError("Indica el motivo de la baja.")
    emp.update(activo=False, fecha_baja=fecha or date.today().isoformat(),
               motivo_baja=motivo.strip())
    return emp


def eliminar(empleados, id_empleado):
    """Elimina definitivamente a un empleado (no queda historial). Devuelve el eliminado."""
    if not PERMITIR_ELIMINAR:
        raise ValueError("La eliminacion definitiva esta desactivada.")
    emp = buscar_por_id(empleados, id_empleado)
    if emp is None:
        raise ValueError("El empleado no existe.")
    empleados.remove(emp)
    return emp


def reactivar(empleados, id_empleado):
    emp = buscar_por_id(empleados, id_empleado)
    if emp is None:
        raise ValueError("El empleado no existe.")
    if emp["activo"]:
        raise ValueError("El empleado ya esta activo.")
    emp.update(activo=True, fecha_baja=None, motivo_baja="")
    return emp


def buscar(empleados, texto="", rol=None, estado="activos", sucursal=None):
    """Lista empleados filtrando por texto (nombre o DNI), rol y estado
    ('activos', 'inactivos' o 'todos')."""
    texto = _sin_tildes(texto.strip())
    resultado = []
    for e in empleados:
        if estado == "activos" and not e["activo"]:
            continue
        if estado == "inactivos" and e["activo"]:
            continue
        roles_emp = e.get("roles", [])
        if not roles_emp and "rol" in e:
            roles_emp = [e["rol"]]
        if rol and rol not in roles_emp:
            continue
        if sucursal and e.get("sucursal", e.get("Sucursal")) != sucursal:
            continue
        if texto and texto not in _sin_tildes(e["nombre"]) and texto not in e["dni"]:
            continue
        resultado.append(e)
    return resultado
