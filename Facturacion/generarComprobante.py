import requests
from datetime import datetime
from .models import CabeceraComandaModel, ComprobanteModel


def emitirComprobante(tipo_comprobante,
                      cliente_tipo_documento,
                      cliente_documento,
                      cliente_email,
                      cabecera_id,
                      observaciones
                      ):
    # sunat_transaction sirve para indicar que tipo de transaccion estas realizando, generalmente es el 1 "VENTA INTERNA"
    # moneda => 1: SOLES , 2: DOLARES, 3: EUROS
    # formato_de_pdf => A4, A5, TICKET
    # buscar el cliente segun su documento
    cliente_denominacion = ""
    documento = 0
    comanda = CabeceraComandaModel.objects.get(cabeceraId=cabecera_id)
    # el total de la comanda ya es un precio que incluye igv
    # el monto total gravada es el monto sin el igv
    total = float(comanda.cabeceraTotal)
    total_gravada = total / 1.18
    total_igv = total - total_gravada

    if len(cliente_documento) > 0:
        base_url_apiperu = "https://apiperu.dev/api/"
        if cliente_tipo_documento == "RUC":
            base_url_apiperu = base_url_apiperu + \
                "ruc/{}".format(cliente_documento)
        elif cliente_documento == "DNI":
            base_url_apiperu = base_url_apiperu + \
                "dni/{}".format(cliente_documento)

        headers = {
            "Authorization": "Bearer a04884fe9d80a7ea2bed4eb934e31be4517cfdca620ca09dceed9eea76a2571b",
            "Content-Type": "application/json"
        }
        respuestaApiPeru = requests.get(url=base_url_apiperu, headers=headers)

        if cliente_tipo_documento == "RUC":
            documento = 6
            print(respuestaApiPeru.json())
            cliente_denominacion = respuestaApiPeru.json()[
                'data']['nombre_o_razon_social']
        elif cliente_tipo_documento == "DNI":
            documento = 1
            cliente_denominacion = respuestaApiPeru.json()[
                'data']['nombre_completo']
    else:
        if total > 700:
            return {'errors': 'Para un monto mayor a 700 es necesario una identificacion.'}
        documento = "-"
        cliente_denominacion = "VARIOS"
        cliente_documento = "VARIOS"

    # items
    # codigo => codigo interno que manejamos nosotros
    # tipo de igv es para ver que declaracion tiene ese item si es gravado inafecto o exonerado
    # unidad de medida es NIU para productos y ZZ para servicios
    # valor unitario es SIN IGV
    # precio unitario es CON IGV
    # subtotal => valor_unitario * cantidad

    # NOTA: Para registrar un producto en la SUNAT no puede haber un producto con precio 0.00
    items = []
    for detalle in comanda.cabeceraDetalles.all():
        precio_unitario = float(detalle.inventario.inventarioPrecio)
        valor_unitario = precio_unitario / 1.18
        cantidad = detalle.detalleCantidad
        items.append({
            "unidad_de_medida": "NIU",
            "codigo": detalle.detalleId,
            "descripcion": detalle.inventario.inventarioPlato,
            "cantidad": cantidad,
            "valor_unitario": valor_unitario,
            "precio_unitario": precio_unitario,
            "subtotal": valor_unitario * cantidad,
            "tipo_de_igv": 1,
            "igv": (precio_unitario - valor_unitario) * cantidad,
            "total": precio_unitario * cantidad,
            "anticipo_regularizacion": False
        })
    # La serie:
    # Las facturas y notas asociadas empiezan con F
    # Las boletas y notas asociadas empiezan con B
    serie = ""
    ultimoComprobante = None
    if tipo_comprobante == 1:
        serie = "FFF1"
        ultimoComprobante = ComprobanteModel.objects.filter(comprobanteSerie=serie).order_by(
            '-comprobanteNumero').first()
    elif tipo_comprobante == 2:
        serie = "BBB1"
        ultimoComprobante = ComprobanteModel.objects.filter(comprobanteSerie=serie).order_by(
            '-comprobanteNumero').first()
    # tipo_comprobante => 1: Factura, 2: Boleta, 3: Nota credito, 4: Nota debito
    if ultimoComprobante is None:
        numero = 1
    else:
        numero = ultimoComprobante.comprobanteNumero+1
    comprobante_body = {
        "operacion": "generar_comprobante",
        "tipo_de_comprobante": tipo_comprobante,
        "serie": serie,
        "numero": numero,
        "sunat_transaction": 1,
        "cliente_tipo_de_documento": 6,
        "cliente_numero_de_documento": cliente_documento,
        "cliente_denominacion": cliente_denominacion,
        "cliente_direccion": "",
        "cliente_email": cliente_email,
        "fecha_de_emision": datetime.now().strftime("%d-%m-%Y"),
        "moneda": 1,
        "porcentaje_de_igv": 18.00,
        "total_gravada": total_gravada,
        "total_igv": total_igv,
        "total": total,
        "detraccion": False,
        "observaciones": observaciones,
        "enviar_automaticamente_a_la_sunat": True,
        "enviar_automaticamente_al_cliente": True,
        "medio_de_pago": "EFECTIVO",
        "formato_de_pdf": "A4",
        "items": items
    }
    print(comprobante_body)
    url_nubefact = "https://api.nubefact.com/api/v1/47abbe5d-f8fe-4f5e-b90c-7699c392c1f7"
    headers_nubefact = {
        "Authorization": "70a287fd9f314413a8ce47cdbff6bd0c09e7a9aa7ad64c9582b247d89f892ede",
        "Content-Type": "application/json"
    }
    respuesta_nubefact = requests.post(
        url=url_nubefact, json=comprobante_body, headers=headers_nubefact)
    return respuesta_nubefact.json()


def buscarComprobante():
    pass
