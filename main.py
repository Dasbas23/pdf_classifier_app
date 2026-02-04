import sys
import subprocess
from app.gui.main_window import PDFClassifierApp

# =========================================================================
# 🛑 PARCHE PARA ELIMINAR CONSOLAS NEGRAS (FLICKERING) EN WINDOWS
# =========================================================================
# Esto intercepta las llamadas al sistema (Tesseract/Poppler) y fuerza
# a que se ejecuten sin ventana visible.
if sys.platform.startswith("win"):
    # Guardamos la clase Popen original por si acaso
    _Popen = subprocess.Popen


    class Popen(subprocess.Popen):
        def __init__(self, *args, **kwargs):
            # Si no se ha definido startupinfo, lo creamos nosotros
            if 'startupinfo' not in kwargs:
                startupinfo = subprocess.STARTUPINFO()
                # STARTF_USESHOWWINDOW indica que queremos controlar la visibilidad
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                # SW_HIDE (0) fuerza a que la ventana esté oculta
                startupinfo.wShowWindow = subprocess.SW_HIDE
                kwargs['startupinfo'] = startupinfo

            # Llamamos al Popen original con nuestros trucos inyectados
            super().__init__(*args, **kwargs)


    # Reemplazamos la función del sistema por la nuestra parcheada
    subprocess.Popen = Popen
# =========================================================================

if __name__ == "__main__":
    app = PDFClassifierApp()
    app.mainloop()