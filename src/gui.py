"""
Interfaz grafica (Tkinter) de los dos modulos: Empleados y Reportes.
Barra lateral de navegacion, tarjetas y graficos de barras dibujados con Canvas.
Solo usa la libreria estandar.
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog

from empleados import empleados as logica
from empleados import almacen
from reportes import reportes as rep

# ---------- Paleta (tonos cafe) y fuente ----------
ESPRESSO = "#3b2a20"
ESPRESSO_CLARO = "#523b2d"
ACENTO = "#c8783c"
ACENTO_OSC = "#a85f2a"
CREMA = "#f6efe7"
TARJETA = "#ffffff"
FILA_PAR = "#faf5ee"
BORDE = "#e4d8ca"
TEXTO = "#3b2a20"
MUDO = "#8c7b6e"
VERDE = "#4f9d69"
ROJO = "#c0504d"
MOCCA = "#7a5c47"
FUENTE = "Segoe UI"
# Logo de la cafeteria: archivo PNG o GIF en  src/assets/logo.png
RUTA_LOGO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "magnolia.png")
LOGO_SOBRE_CREMA = False   # True: apoya el logo sobre un fondo crema (si no se ve bien en oscuro)


# ---------- Piezas reutilizables ----------

def estilos(raiz):
    """Configura la apariencia de tablas, listas desplegables y barras de scroll."""
    e = ttk.Style(raiz)
    e.theme_use("clam")
    e.configure("Treeview", background=TARJETA, fieldbackground=TARJETA, foreground=TEXTO,
                rowheight=32, borderwidth=0, font=(FUENTE, 10))
    e.configure("Treeview.Heading", background=ESPRESSO, foreground="white", relief="flat",
                font=(FUENTE, 10, "bold"), padding=(8, 8))
    e.map("Treeview", background=[("selected", ACENTO)], foreground=[("selected", "white")])
    e.map("Treeview.Heading", background=[("active", ESPRESSO_CLARO)])
    e.configure("TCombobox", fieldbackground=CREMA, background=CREMA, foreground=TEXTO,
                arrowcolor=ESPRESSO, bordercolor=BORDE, lightcolor=CREMA, darkcolor=CREMA,
                padding=5)
    e.map("TCombobox", fieldbackground=[("readonly", CREMA)],
          selectbackground=[("readonly", CREMA)], selectforeground=[("readonly", TEXTO)])
    e.configure("Vertical.TScrollbar", background=BORDE, troughcolor=CREMA,
                bordercolor=CREMA, arrowcolor=ESPRESSO)
    raiz.option_add("*TCombobox*Listbox.font", (FUENTE, 10))
    raiz.option_add("*TCombobox*Listbox.selectBackground", ACENTO)

def cargar_logo(ancho_max=150):
    """Carga el logo y lo achica (si hace falta) para que entre en la barra lateral.
    Devuelve None si el archivo no existe, asi el programa funciona igual sin logo."""
    if not os.path.exists(RUTA_LOGO):
        return None
    try:
        imagen = tk.PhotoImage(file=RUTA_LOGO)
    except tk.TclError:   # formato no soportado (por ejemplo un JPG renombrado)
        return None
    if imagen.width() > ancho_max:
        imagen = imagen.subsample(-(-imagen.width() // ancho_max))   # reduce a enteros
    return imagen


def boton(master, texto, comando, color=ACENTO, hover=ACENTO_OSC, fg="white"):
    """Boton plano de color que cambia al pasar el mouse."""
    b = tk.Button(master, text=texto, command=comando, bg=color, fg=fg, activebackground=hover,
                  activeforeground=fg, relief="flat", bd=0, padx=16, pady=8, cursor="hand2",
                  highlightthickness=0,
                  font=(FUENTE, 10, "bold"))
    b.bind("<Enter>", lambda _: b.config(bg=hover))
    b.bind("<Leave>", lambda _: b.config(bg=color))
    return b


def entrada(master, variable, ancho=26):
    """Campo de texto plano que resalta su borde al enfocarlo."""
    return tk.Entry(master, textvariable=variable, width=ancho, relief="flat", bg=CREMA,
                    fg=TEXTO, font=(FUENTE, 11), highlightthickness=1,
                    highlightbackground=BORDE, highlightcolor=ACENTO, insertbackground=TEXTO)


def tarjeta(master):
    return tk.Frame(master, bg=TARJETA, highlightbackground=BORDE, highlightthickness=1)


def tarjeta_titulada(master, titulo):
    """Tarjeta con titulo. Devuelve (tarjeta, cabecera, cuerpo)."""
    t = tarjeta(master)
    cabecera = tk.Frame(t, bg=TARJETA)
    cabecera.pack(fill="x", padx=14, pady=(12, 4))
    tk.Label(cabecera, text=titulo, bg=TARJETA, fg=TEXTO,
             font=(FUENTE, 11, "bold")).pack(side="left")
    cuerpo = tk.Frame(t, bg=TARJETA)
    cuerpo.pack(fill="both", expand=True, padx=14, pady=(0, 12))
    return t, cabecera, cuerpo


def encabezado(master, titulo, subtitulo):
    """Titulo grande de cada seccion. Devuelve el marco, para sumarle botones a la derecha."""
    marco = tk.Frame(master, bg=CREMA)
    marco.pack(fill="x", padx=28, pady=(24, 14))
    textos = tk.Frame(marco, bg=CREMA)
    textos.pack(side="left")
    tk.Label(textos, text=titulo, bg=CREMA, fg=TEXTO, font=("Georgia", 22, "bold")).pack(anchor="w")
    tk.Label(textos, text=subtitulo, bg=CREMA, fg=MUDO, font=(FUENTE, 10)).pack(anchor="w")
    return marco


def tabla(master, columnas, alto=None):
    """Tabla con estilo. 'columnas' es una lista de (nombre, ancho, titulo)."""
    t = ttk.Treeview(master, columns=[c[0] for c in columnas], show="headings",
                     selectmode="browse", height=alto or 10)
    for nombre, ancho, titulo in columnas:
        t.heading(nombre, text=titulo, anchor="w")
        t.column(nombre, width=ancho, anchor="w")
    t.tag_configure("par", background=FILA_PAR)
    t.tag_configure("inactivo", foreground="#a99b8f")
    return t


def tabla_con_scroll(master, columnas, alto):
    """Tabla con estilo y barra de scroll vertical."""
    marco = tk.Frame(master, bg=TARJETA)
    t = tabla(marco, columnas, alto)
    scroll = ttk.Scrollbar(marco, orient="vertical", command=t.yview)
    t.configure(yscrollcommand=scroll.set)
    t.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")
    return marco, t


def texto_antiguedad(meses):
    anios, resto = divmod(meses, 12)
    if anios == 0:
        return f"{resto} mes" + ("" if resto == 1 else "es")
    return f"{anios} año" + ("" if anios == 1 else "s") + (f" y {resto} m" if resto else "")


# ---------- Graficos simples con Canvas ----------

class GraficoBarras(tk.Canvas):
    """Barras horizontales: una por categoria."""

    def __init__(self, master, color):
        super().__init__(master, bg=TARJETA, highlightthickness=0, height=100)
        self.color, self.datos = color, {}
        self.bind("<Configure>", lambda _: self._dibujar())

    def mostrar(self, datos):
        self.datos = datos
        self._dibujar()

    def _dibujar(self):
        self.delete("all")
        ancho = self.winfo_width()
        if not self.datos:
            self.create_text(ancho / 2, 50, text="Sin datos", fill=MUDO, font=(FUENTE, 10))
            return
        maximo = max(self.datos.values())
        x0, x1 = 90, max(ancho - 45, 100)
        for i, (nombre, valor) in enumerate(self.datos.items()):
            y = 10 + i * 34
            largo = (x1 - x0) * valor / maximo
            self.create_text(0, y + 10, text=nombre.capitalize(), anchor="w", fill=TEXTO,
                             font=(FUENTE, 10))
            self.create_rectangle(x0, y, x0 + largo, y + 20, fill=self.color, outline="")
            self.create_text(x0 + largo + 8, y + 10, text=str(valor), anchor="w", fill=TEXTO,
                             font=(FUENTE, 10, "bold"))


class GraficoMeses(tk.Canvas):
    """Barras verticales agrupadas: altas (verde) y bajas (rojo) de los ultimos 6 meses."""

    def __init__(self, master):
        super().__init__(master, bg=TARJETA, highlightthickness=0, height=100)
        self.datos = {}
        self.bind("<Configure>", lambda _: self._dibujar())

    def mostrar(self, datos):
        self.datos = datos
        self._dibujar()

    def _dibujar(self):
        self.delete("all")
        ancho, alto = self.winfo_width(), self.winfo_height()
        meses = list(self.datos.items())[-6:]
        if not meses:
            self.create_text(ancho / 2, alto / 2, text="Sin datos", fill=MUDO, font=(FUENTE, 10))
            return
        maximo = max(max(d["altas"], d["bajas"]) for _, d in meses) or 1
        base, tope = alto - 22, 18
        grupo = (ancho - 10) / len(meses)
        for i, (mes, d) in enumerate(meses):
            centro = 5 + i * grupo + grupo / 2
            for j, (clave, color) in enumerate((("altas", VERDE), ("bajas", ROJO))):
                altura = (base - tope) * d[clave] / maximo
                x = centro - 16 + j * 18
                self.create_rectangle(x, base - altura, x + 14, base, fill=color, outline="")
                if d[clave]:
                    self.create_text(x + 7, base - altura - 8, text=str(d[clave]), fill=TEXTO,
                                     font=(FUENTE, 8, "bold"))
            self.create_text(centro, base + 11, text=f"{mes[5:]}/{mes[2:4]}", fill=MUDO,
                             font=(FUENTE, 8))


class Indicador(tk.Frame):
    """Tarjeta con un numero grande y una franja de color a la izquierda."""

    def __init__(self, master, titulo, color):
        super().__init__(master, bg=TARJETA, highlightbackground=BORDE, highlightthickness=1)
        tk.Frame(self, bg=color, width=6).pack(side="left", fill="y")
        cuerpo = tk.Frame(self, bg=TARJETA)
        cuerpo.pack(side="left", padx=16, pady=12)
        tk.Label(cuerpo, text=titulo.upper(), bg=TARJETA, fg=MUDO,
                 font=(FUENTE, 8, "bold")).pack(anchor="w")
        self.valor = tk.Label(cuerpo, text="0", bg=TARJETA, fg=TEXTO, font=(FUENTE, 22, "bold"))
        self.valor.pack(anchor="w")

    def poner(self, texto):
        self.valor.config(text=str(texto))


# ---------- Formulario de empleado ----------

class FormEmpleado(tk.Toplevel):
    """Ventana para cargar o modificar un empleado."""

    def __init__(self, master, titulo, datos=None, al_guardar=None):
        super().__init__(master)
        self.title(titulo)
        self.configure(bg=CREMA)
        self.resizable(False, False)
        self.transient(master)
        self.wait_visibility()
        self.grab_set()
        self.al_guardar = al_guardar
        datos = datos or {}

        self.v_nombre = tk.StringVar(value=datos.get("nombre", ""))
        self.v_dni = tk.StringVar(value=datos.get("dni", ""))
        self.v_roles = {r: tk.BooleanVar(value=r in datos.get("roles", []))
                        for r in logica.ROLES}
        self.v_turno = tk.StringVar(value=datos.get("turno", logica.TURNOS[0]))
        self.v_sucursal = tk.StringVar(value=datos.get("sucursal", logica.SUCURSALES[0]))
        self.v_contacto = tk.StringVar(value=datos.get("contacto", ""))

        cab = tk.Frame(self, bg=ESPRESSO)
        cab.pack(fill="x")
        tk.Label(cab, text=titulo, bg=ESPRESSO, fg="white",
                 font=("Georgia", 14, "bold")).pack(anchor="w", padx=22, pady=14)

        cuerpo = tk.Frame(self, bg=CREMA)
        cuerpo.pack(padx=24, pady=(16, 8))
        # (texto, widget, fila, columna, columnas que ocupa)
        campos = [
            ("Nombre y apellido", entrada(cuerpo, self.v_nombre, 46), 0, 0, 2),
            ("DNI", entrada(cuerpo, self.v_dni, 20), 1, 0, 1),
            ("Contacto (opcional)", entrada(cuerpo, self.v_contacto, 20), 1, 1, 1),
            ("Roles (mozo y encargado se pueden combinar)", self._casillas_roles(cuerpo), 2, 0, 2),
            ("Turno", ttk.Combobox(cuerpo, textvariable=self.v_turno, values=logica.TURNOS,
                                   state="readonly", width=20), 3, 0, 1),
            ("Sucursal", ttk.Combobox(cuerpo, textvariable=self.v_sucursal, values=logica.SUCURSALES,
                                      state="readonly", width=20), 3, 1, 1),
        ]
        for texto, widget, fila, col, span in campos:
            tk.Label(cuerpo, text=texto, bg=CREMA, fg=MUDO, font=(FUENTE, 9, "bold")
                     ).grid(row=fila * 2, column=col, columnspan=span, sticky="w",
                            padx=6, pady=(10, 2))
            widget.grid(row=fila * 2 + 1, column=col, columnspan=span, sticky="ew",
                        padx=6, ipady=3)

        botones = tk.Frame(self, bg=CREMA)
        botones.pack(fill="x", padx=30, pady=(4, 18))
        boton(botones, "Guardar", self._guardar).pack(side="right")
        boton(botones, "Cancelar", self.destroy, color=BORDE, hover="#d6c7b5",
              fg=TEXTO).pack(side="right", padx=8)

    def _casillas_roles(self, master):
        """Una casilla por rol, para poder marcar uno o varios."""
        marco = tk.Frame(master, bg=CREMA)
        for rol in logica.ROLES:
            tk.Checkbutton(marco, text=rol.capitalize(), variable=self.v_roles[rol],
                           bg=CREMA, fg=TEXTO, activebackground=CREMA, font=(FUENTE, 11),
                           highlightthickness=0, cursor="hand2",
                           command=lambda r=rol: self._ajustar_roles(r)
                           ).pack(side="left", padx=(0, 16))
        return marco

    def _ajustar_roles(self, elegido):
        """Solo mozo y encargado se combinan: al marcar uno, se desmarcan los que no se pueden
        combinar con el."""
        if not self.v_roles[elegido].get():
            return
        for rol, marcado in self.v_roles.items():
            if rol != elegido and (elegido not in logica.ROLES_COMBINABLES
                                   or rol not in logica.ROLES_COMBINABLES):
                marcado.set(False)

    def _guardar(self):
        roles = [rol for rol, marcado in self.v_roles.items() if marcado.get()]
        try:
            self.al_guardar(self.v_nombre.get(), self.v_dni.get(), roles,
                            self.v_turno.get(),self.v_sucursal.get(), self.v_contacto.get())
        except ValueError as error:
            messagebox.showerror("Dato invalido", str(error), parent=self)
            return
        self.destroy()


# ---------- Vista 1: Empleados ----------

class VistaEmpleados(tk.Frame):
    COLUMNAS = [("id", 35, "ID"), ("nombre", 135, "Nombre"), ("dni", 75, "DNI"),
                ("roles", 120, "Roles"), ("turno", 65, "Turno"), ("sucursal", 130, "Sucursal"),
                ("contacto", 100, "Contacto"), ("ingreso", 85, "Ingreso"), ("estado", 65, "Estado")]

    def __init__(self, master, app):
        super().__init__(master, bg=CREMA)
        self.app = app

        cab = encabezado(self, "Empleados", "Alta, modificación y baja del personal")
        boton(cab, "+  Nuevo empleado", self.nuevo).pack(side="right")

        # Tarjeta de busqueda y filtros
        filtros = tarjeta(self)
        filtros.pack(fill="x", padx=28, pady=(0, 12))
        fila = tk.Frame(filtros, bg=TARJETA)
        fila.pack(fill="x", padx=14, pady=12)
        self.v_texto = tk.StringVar()
        self.v_rol = tk.StringVar(value="todos")
        self.v_sucursal = tk.StringVar(value="todas")
        self.v_estado = tk.StringVar(value="activos")
        for texto, widget in (
            ("Buscar", entrada(fila, self.v_texto, 28)),
            ("Rol", ttk.Combobox(fila, textvariable=self.v_rol, values=["todos"] + logica.ROLES,
                                 state="readonly", width=12)),
            ("Sucursal", ttk.Combobox(fila, textvariable=self.v_sucursal,
                                      values=["todas"] + logica.SUCURSALES,
                                      state="readonly", width=18)),
            ("Estado", ttk.Combobox(fila, textvariable=self.v_estado,
                                    values=["activos", "inactivos", "todos"],
                                    state="readonly", width=12)),
        ):
            tk.Label(fila, text=texto, bg=TARJETA, fg=MUDO,
                     font=(FUENTE, 9, "bold")).pack(side="left", padx=(0, 6))
            widget.pack(side="left", padx=(0, 22), ipady=3)
        for variable in (self.v_texto, self.v_rol, self.v_sucursal, self.v_estado):
            variable.trace_add("write", lambda *_: self.refrescar())

        # Tarjeta con la tabla
        contenedor = tarjeta(self)
        contenedor.pack(fill="both", expand=True, padx=28)
        self.tabla = tabla(contenedor, self.COLUMNAS)
        scroll = ttk.Scrollbar(contenedor, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)
        self.tabla.pack(side="left", fill="both", expand=True, padx=1, pady=1)
        scroll.pack(side="right", fill="y")

        # Pie con acciones
        pie = tk.Frame(self, bg=CREMA)
        pie.pack(fill="x", padx=28, pady=14)
        self.lbl_cantidad = tk.Label(pie, text="", bg=CREMA, fg=MUDO, font=(FUENTE, 10))
        self.lbl_cantidad.pack(side="left")
        if logica.PERMITIR_ELIMINAR:   # boton solo para pruebas (ver empleados.py)
            boton(pie, "Eliminar definitivamente", self.eliminar, color="#7a1f1f",
                  hover="#5e1717").pack(side="left", padx=(18, 0))
        boton(pie, "Reactivar", self.reactivar, color=VERDE, hover="#3f8456").pack(side="right")
        boton(pie, "Dar de baja", self.baja, color=ROJO, hover="#a3403d").pack(side="right", padx=8)
        boton(pie, "Modificar", self.modificar, color=ESPRESSO,
              hover=ESPRESSO_CLARO).pack(side="right")
        self.refrescar()

    def refrescar(self):
        self.tabla.delete(*self.tabla.get_children())
        rol = None if self.v_rol.get() == "todos" else self.v_rol.get()
        sucursal = None if self.v_sucursal.get() == "todas" else self.v_sucursal.get()
        lista = logica.buscar(self.app.empleados, self.v_texto.get(), rol, self.v_estado.get(), sucursal)
        for i, e in enumerate(lista):
            etiquetas = ("par",) if i % 2 else ()
            if not e["activo"]: 
                etiquetas += ("inactivo",)
            self.tabla.insert("", "end", tags=etiquetas, values=(
                e["id"], e["nombre"], e["dni"], " / ".join(r.capitalize() for r in e["roles"]),
                e["turno"].capitalize(), e["sucursal"],
                e["contacto"] or "-", e["fecha_ingreso"], "Activo" if e["activo"] else "Inactivo"))
        self.lbl_cantidad.config(text=f"{len(lista)} empleado(s) en la lista")

    def _seleccionado(self):
        """Devuelve el id del empleado elegido en la tabla (o None)."""
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showinfo("Seleccionar", "Primero elegí un empleado de la lista.")
            return None
        return int(self.tabla.item(seleccion[0])["values"][0])

    def _aplicar(self, accion):
        """Ejecuta una accion de logica, guarda en disco y actualiza la tabla."""
        try:
            accion()
        except ValueError as error:
            messagebox.showerror("No se pudo realizar", str(error))
            return
        self.app.guardar()
        self.refrescar()

    def nuevo(self):
        def guardar(*datos):
            logica.alta(self.app.empleados, *datos)
            self.app.guardar()
            self.refrescar()
        FormEmpleado(self, "Nuevo empleado", al_guardar=guardar)

    def modificar(self):
        id_emp = self._seleccionado()
        if id_emp is None:
            return
        emp = logica.buscar_por_id(self.app.empleados, id_emp)

        def guardar(*datos):
            logica.modificar(self.app.empleados, id_emp, *datos)
            self.app.guardar()
            self.refrescar()
        FormEmpleado(self, "Modificar empleado", datos=emp, al_guardar=guardar)

    def baja(self):
        id_emp = self._seleccionado()
        if id_emp is None:
            return
        motivo = simpledialog.askstring("Dar de baja", "Motivo de la baja:", parent=self)
        if motivo is None:
            return
        self._aplicar(lambda: logica.baja(self.app.empleados, id_emp, motivo))

    def eliminar(self):
        id_emp = self._seleccionado()
        if id_emp is None:
            return
        emp = logica.buscar_por_id(self.app.empleados, id_emp)
        confirmado = messagebox.askyesno(
            "Eliminar definitivamente",
            f"Se va a eliminar para siempre a {emp['nombre']} (DNI {emp['dni']}).\n\n"
            "Esta acción no se puede deshacer.\n¿Querés continuar?",
            icon="warning", default="no", parent=self)
        if confirmado:
            self._aplicar(lambda: logica.eliminar(self.app.empleados, id_emp))

    def reactivar(self):
        id_emp = self._seleccionado()
        if id_emp is not None:
            self._aplicar(lambda: logica.reactivar(self.app.empleados, id_emp))


# ---------- Vista 2: Reportes ----------

class VistaReportes(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=CREMA)
        self.app = app

        cab = encabezado(self, "Reportes", "Resumen del personal (solo lectura)")
        boton(cab, "Exportar a CSV", self.exportar, color=ESPRESSO,
              hover=ESPRESSO_CLARO).pack(side="right")
        boton(cab, "Actualizar", self.refrescar).pack(side="right", padx=8)

        # Fila de indicadores
        fila = tk.Frame(self, bg=CREMA)
        fila.pack(fill="x", padx=22, pady=(0, 12))
        self.kpi = {}
        for i, (clave, titulo, color) in enumerate((
                ("total", "Total", ESPRESSO), ("activos", "Activos", VERDE),
                ("inactivos", "Inactivos", ROJO), ("promedio", "Antigüedad promedio", ACENTO))):
            self.kpi[clave] = Indicador(fila, titulo, color)
            self.kpi[clave].grid(row=0, column=i, sticky="nsew", padx=6)
            fila.columnconfigure(i, weight=1, uniform="kpi")

        # Cuadricula de tarjetas: arriba 3 graficos, abajo 2 listas
        rejilla = tk.Frame(self, bg=CREMA)
        rejilla.pack(fill="both", expand=True, padx=22, pady=(0, 18))
        for c in range(6):
            rejilla.columnconfigure(c, weight=1, uniform="col")
        rejilla.rowconfigure(0, weight=1, uniform="fila")
        rejilla.rowconfigure(1, weight=1, uniform="fila")

        t, cabecera, cuerpo = tarjeta_titulada(rejilla, "Personal por rol")
        t.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=6, pady=6)
        tk.Label(cabecera, text="cuenta cada rol", bg=TARJETA, fg=MUDO,
                 font=(FUENTE, 8)).pack(side="right")
        self.g_rol = GraficoBarras(cuerpo, ACENTO)
        self.g_rol.pack(fill="both", expand=True)

        t, _, cuerpo = tarjeta_titulada(rejilla, "Personal por turno")
        t.grid(row=0, column=2, columnspan=2, sticky="nsew", padx=6, pady=6)
        self.g_turno = GraficoBarras(cuerpo, MOCCA)
        self.g_turno.pack(fill="both", expand=True)

        t, cabecera, cuerpo = tarjeta_titulada(rejilla, "Altas y bajas")
        t.grid(row=0, column=4, columnspan=2, sticky="nsew", padx=6, pady=6)
        tk.Label(cabecera, text="● bajas", bg=TARJETA, fg=ROJO,
                 font=(FUENTE, 8, "bold")).pack(side="right")
        tk.Label(cabecera, text="● altas  ", bg=TARJETA, fg=VERDE,
                 font=(FUENTE, 8, "bold")).pack(side="right")
        self.g_meses = GraficoMeses(cuerpo)
        self.g_meses.pack(fill="both", expand=True)

        t, _, cuerpo = tarjeta_titulada(rejilla, "Antigüedad del personal activo")
        t.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=6, pady=6)
        marco, self.t_antiguedad = tabla_con_scroll(
            cuerpo, [("nombre", 200, "Nombre"), ("antiguedad", 130, "Antigüedad")], alto=4)
        marco.pack(fill="both", expand=True)

        t, _, cuerpo = tarjeta_titulada(rejilla, "Motivos de baja")
        t.grid(row=1, column=3, columnspan=3, sticky="nsew", padx=6, pady=6)
        marco, self.t_bajas = tabla_con_scroll(
            cuerpo, [("nombre", 115, "Nombre"), ("fecha", 85, "Fecha"),
                     ("motivo", 140, "Motivo")], alto=4)
        marco.pack(fill="both", expand=True)

    @staticmethod
    def _llenar(t, filas):
        t.delete(*t.get_children())
        for i, fila in enumerate(filas):
            t.insert("", "end", values=fila, tags=("par",) if i % 2 else ())

    def refrescar(self):
        emp = self.app.empleados
        resumen = rep.resumen(emp)
        for clave in ("total", "activos", "inactivos"):
            self.kpi[clave].poner(resumen[clave])

        antiguedad = rep.antiguedad(emp)
        promedio = sum(m for _, m in antiguedad) // len(antiguedad) if antiguedad else None
        self.kpi["promedio"].poner(
            f"{promedio / 12:.1f} años".replace(".", ",") if promedio is not None else "-")

        self.g_rol.mostrar(rep.contar_por(emp, "roles"))
        self.g_turno.mostrar(rep.contar_por(emp, "turno"))
        self.g_meses.mostrar(rep.altas_bajas_por_mes(emp))
        self._llenar(self.t_antiguedad, [(n, texto_antiguedad(m)) for n, m in antiguedad])
        self._llenar(self.t_bajas, rep.motivos_de_baja(emp))

    def exportar(self):
        ruta = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="empleados.csv",
                                            filetypes=[("CSV", "*.csv")])
        if ruta:
            rep.exportar_csv(self.app.empleados, ruta)
            messagebox.showinfo("Exportado", f"Archivo guardado en:\n{ruta}")


# ---------- Ventana principal ----------

class App(tk.Tk):
    def __init__(self, empleados):
        super().__init__()
        self.title("Gestión de personal - Cafetería")
        self.geometry("1100x700")
        self.minsize(1040, 640)
        self.configure(bg=CREMA)
        self.empleados = empleados
        estilos(self)

        # Barra lateral
        lateral = tk.Frame(self, bg=ESPRESSO, width=210)
        lateral.pack(side="left", fill="y")
        lateral.pack_propagate(False)
        self.logo = cargar_logo()   # se guarda en self para que Tk no lo borre de memoria
        if self.logo:
            self.iconphoto(True, self.logo)   # icono de la ventana
            fondo = CREMA if LOGO_SOBRE_CREMA else ESPRESSO
            marco = tk.Frame(lateral, bg=fondo)
            marco.pack(anchor="w", padx=22, pady=(26, 8))
            tk.Label(marco, image=self.logo, bg=fondo, bd=0).pack(padx=8, pady=8)
        else:
            tk.Label(lateral, text="CAFETERÍA", bg=ESPRESSO, fg=ACENTO,
                     font=("Georgia", 18, "bold")).pack(anchor="w", padx=22, pady=(30, 0))
        tk.Label(lateral, text="Gestión de personal", bg=ESPRESSO, fg="#d9c7b5",
                 font=(FUENTE, 9)).pack(anchor="w", padx=22, pady=(0, 30))
        tk.Label(lateral, text="Práctica profesional II\nAnálisis de Sistemas", bg=ESPRESSO,
                 fg=MUDO, font=(FUENTE, 8), justify="left").pack(side="bottom", pady=20)

        self.contenido = tk.Frame(self, bg=CREMA)
        self.contenido.pack(side="left", fill="both", expand=True)
        self.vistas = {"empleados": VistaEmpleados(self.contenido, self),
                       "reportes": VistaReportes(self.contenido, self)}

        self.botones, self.franjas = {}, {}
        for clave, texto in (("empleados", "Empleados"), ("reportes", "Reportes")):
            fila = tk.Frame(lateral, bg=ESPRESSO)
            fila.pack(fill="x")
            self.franjas[clave] = tk.Frame(fila, bg=ESPRESSO, width=4)
            self.franjas[clave].pack(side="left", fill="y")
            self.botones[clave] = tk.Button(
                fila, text=texto, anchor="w", relief="flat", bd=0, padx=18, pady=13,
                highlightthickness=0,
                cursor="hand2", font=(FUENTE, 11), bg=ESPRESSO, fg="#e8dccf",
                activebackground=ESPRESSO_CLARO, activeforeground="white",
                command=lambda c=clave: self.mostrar(c))
            self.botones[clave].pack(side="left", fill="x", expand=True)
        self.mostrar("empleados")

    def mostrar(self, clave):
        """Muestra una vista y resalta su boton en la barra lateral."""
        for vista in self.vistas.values():
            vista.pack_forget()
        self.vistas[clave].pack(fill="both", expand=True)
        for k, boton_nav in self.botones.items():
            activo = k == clave
            boton_nav.config(bg=ESPRESSO_CLARO if activo else ESPRESSO,
                             fg="white" if activo else "#e8dccf")
            self.franjas[k].config(bg=ACENTO if activo else ESPRESSO)
        if clave == "reportes":
            self.vistas["reportes"].refrescar()

    def guardar(self):
        almacen.guardar(self.empleados)
