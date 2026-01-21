import re
# [CAMBIO] Ya no importamos PROVEEDORES de config, sino el cargador dinámico
from app.core.provider_manager import cargar_proveedores


def analizar_documento(texto_pdf):
    """
    Recibe el texto crudo del PDF.
    1. Carga reglas desde JSON.
    2. Busca proveedor.
    3. Extrae pedido.
    """
    resultado = {
        "proveedor_detectado": None,
        "numero_pedido": None,
        "confianza": "Baja",
        "log_info": ""
    }

    if not texto_pdf:
        return resultado

    # [CAMBIO] Cargamos los proveedores al momento de analizar
    # Esto permite editar el JSON y que la app funcione sin reiniciar
    diccionario_proveedores = cargar_proveedores()

    # 1. IDENTIFICACIÓN DEL PROVEEDOR
    proveedor_encontrado = None

    for nombre_prov, reglas in diccionario_proveedores.items():
        firmas = reglas.get("firma", [])
        # Buscamos si alguna firma está en el texto
        for firma in firmas:
            if firma.lower() in texto_pdf.lower():
                proveedor_encontrado = nombre_prov
                break

        if proveedor_encontrado:
            break

    if not proveedor_encontrado:
        resultado["log_info"] = "No se detectó ninguna firma de proveedor conocida."
        return resultado

    # 2. EXTRACCIÓN DE DATOS
    resultado["proveedor_detectado"] = proveedor_encontrado
    reglas_activas = diccionario_proveedores[proveedor_encontrado]
    patron = reglas_activas.get("patron_pedido")

    try:
        match = re.search(patron, texto_pdf, re.IGNORECASE | re.MULTILINE)

        if match:
            pedido_limpio = match.group(1).strip()
            resultado["numero_pedido"] = pedido_limpio
            resultado["confianza"] = "Alta"
            resultado["carpeta_destino"] = reglas_activas.get("carpeta_destino")
        else:
            resultado["log_info"] = f"Proveedor {proveedor_encontrado} identificado, pero falló la Regex."

    except Exception as e:
        resultado["log_info"] = f"Error ejecutando Regex: {e}"

    return resultado