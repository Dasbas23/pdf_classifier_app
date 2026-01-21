import shutil
import os
from app.config import DEFAULT_ERROR_DIR


def mover_y_renombrar(ruta_origen, datos_analisis, carpeta_base_salida):
    """
    Toma el archivo original y lo mueve a su destino final.
    Ahora acepta 'carpeta_base_salida' dinámica desde la GUI.
    """
    nombre_archivo_original = os.path.basename(ruta_origen)

    # CASO 1: Éxito (Tenemos proveedor y pedido/albarán)
    if datos_analisis["proveedor_detectado"] and datos_analisis["numero_pedido"]:
        proveedor = datos_analisis["proveedor_detectado"]
        raw_pedido = datos_analisis["numero_pedido"]

        # [MEJORA] Limpieza profunda del nombre (quitamos espacios y puntos del albarán)
        # Ejemplo: "02AL 1.090 9" -> "02AL10909"
        pedido_limpio = "".join([c for c in raw_pedido if c.isalnum() or c in "-_"])

        subcarpeta = datos_analisis.get("carpeta_destino", proveedor)
        dir_final = os.path.join(carpeta_base_salida, subcarpeta)

        extension = os.path.splitext(nombre_archivo_original)[1]
        nuevo_nombre = f"{pedido_limpio}{extension}"

    # CASO 2: Fallo (Revisión manual)
    else:
        dir_final = os.path.join(carpeta_base_salida, "Revision_Manual")
        nuevo_nombre = nombre_archivo_original

    os.makedirs(dir_final, exist_ok=True)
    ruta_destino_final = os.path.join(dir_final, nuevo_nombre)

    if os.path.exists(ruta_destino_final):
        base, ext = os.path.splitext(nuevo_nombre)
        ruta_destino_final = os.path.join(dir_final, f"{base}_DUPLICADO_{os.urandom(2).hex()}{ext}")

    try:
        shutil.move(ruta_origen, ruta_destino_final)
        return True, ruta_destino_final
    except Exception as e:
        return False, str(e)