"""Punto de entrada. Ejecutar con:  python main.py   (desde la carpeta src)."""

import sys
import tkinter as tk
from tkinter import messagebox

from empleados import almacen
from gui import App

if __name__ == "__main__":
    try:
        datos = almacen.cargar()
    except ValueError as error:   # archivo danado: avisamos y NO seguimos (no se pisan datos)
        raiz = tk.Tk()
        raiz.withdraw()
        messagebox.showerror("Error al abrir los datos", str(error))
        sys.exit(1)
    App(datos).mainloop()
