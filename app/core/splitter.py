from pypdf import PdfReader, PdfWriter
from app.core.parser import analizar_documento
import os


def dividir_pdf_por_proveedor(ruta_pdf_masivo, carpeta_temporal):
    """
    Recorre un PDF multipágina (Lote).
    Estrategia de Guillotina: Si detecta un proveedor en una página,
    asume que es el inicio de un nuevo documento.
    Las páginas sin firma se añaden al documento anterior (continuación).

    Retorna: Lista de rutas de los archivos generados.
    """
    if not os.path.exists(ruta_pdf_masivo):
        return []

    try:
        reader = PdfReader(ruta_pdf_masivo)
    except Exception as e:
        print(f"❌ Error abriendo lote PDF: {e}")
        return []

    archivos_generados = []

    writer_actual = None
    proveedor_actual = "Desconocido"
    pagina_inicio_actual = 0

    # Asegurar que existe la carpeta temporal
    os.makedirs(carpeta_temporal, exist_ok=True)

    print(f"🔄 Analizando lote masivo de {len(reader.pages)} páginas...")

    for i, page in enumerate(reader.pages):
        # 1. Extraer texto para ver si es una portada de proveedor
        try:
            text = page.extract_text() or ""
        except:
            text = ""

        # 2. Analizar: ¿Hay firma de algún proveedor conocido aquí?
        analisis = analizar_documento(text)
        nuevo_proveedor = analisis.get("proveedor_detectado")

        # --- LÓGICA DE GUILLOTINA ---
        if nuevo_proveedor:
            # ¡HAY FIRMA! -> Esto es una PORTADA (Página 1 de un doc)

            # A) Si ya teníamos un documento abierto escribiéndose...
            if writer_actual:
                # ...lo cerramos y guardamos porque ha empezado uno nuevo.
                print(f"   ✂️ Corte en pág {i}. Fin del doc anterior ({proveedor_actual}).")
                ruta = _guardar_fragmento(writer_actual, proveedor_actual, pagina_inicio_actual, carpeta_temporal)
                archivos_generados.append(ruta)

            # B) Empezamos el NUEVO documento
            writer_actual = PdfWriter()
            writer_actual.add_page(page)
            proveedor_actual = nuevo_proveedor
            pagina_inicio_actual = i

        else:
            # NO HAY FIRMA -> Es una página de continuación (Pág 2, 3...)
            # O es basura / proveedor desconocido.

            if writer_actual:
                # La añadimos al documento que ya estaba abierto
                writer_actual.add_page(page)
                # print(f"   ➕ Pág {i} añadida a {proveedor_actual} (Continuación)")
            else:
                # Caso raro: El PDF empieza con páginas sin firma conocida.
                # Creamos un documento "Huérfano" para no perderlas.
                writer_actual = PdfWriter()
                writer_actual.add_page(page)
                proveedor_actual = "Desconocido"
                pagina_inicio_actual = i

    # 3. Al terminar el bucle, guardar el último documento que quedó abierto
    if writer_actual:
        ruta = _guardar_fragmento(writer_actual, proveedor_actual, pagina_inicio_actual, carpeta_temporal)
        archivos_generados.append(ruta)
        print(f"   🏁 Guardado bloque final ({proveedor_actual}).")

    return archivos_generados


def _guardar_fragmento(writer, proveedor, indice_pag, carpeta):
    """Escribe el PDF temporal en disco"""
    # Nombre único: SPLIT_Pág0_CBM.pdf
    nombre = f"SPLIT_Pag{indice_pag}_{proveedor}.pdf"
    ruta = os.path.join(carpeta, nombre)

    with open(ruta, "wb") as f:
        writer.write(f)

    return ruta