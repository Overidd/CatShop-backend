from payment_gateway.utils import (
   OrderIdentificationType,
   OrderDeliveryType,
   OrderPaymentType,
   OrderDetailType,
)

from .models import InvoicePaymentsModel

import requests
from django.conf import settings
from django.db.models import QuerySet
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Union


def invoicePayments(order_identification:OrderIdentificationType, order_delivery:OrderDeliveryType, order_payment:OrderPaymentType, order_details:QuerySet[OrderDetailType] )-> Union[str, None]:
      try:
         url = settings.URL_API_NUBEFACT
         token = settings.API_KEY_NUBEFACT

         items = []
         discount_total = 0
         total_gravada = 0
         igv_total = 0
         total_price = 0
         for detail in order_details:
            discount = detail.discount
            igv = detail.price_unit * 0.18
            valor_unitario = detail.price_unit - igv
            discount_total += discount
            total_gravada += valor_unitario
            igv_total += igv
            total_price += detail.price
            item = {
               'unidad_de_medida': 'NIU',# NIU = PRODUCTO, ZZ = SERVICIO
               # 'codigo': 'C001', # Opcional
               'descripcion': detail.name_product, #O bligatorio 
               'cantidad': detail.quantity, # Obligatorio
               'valor_unitario': valor_unitario, # Obligatorio, Valor sin IGV
               'precio_unitario': detail.price, # Obligatorio, Valor con IGV
               'descuento': discount, # Opcional, descuento del producto antes de los impuestos
               'subtotal': detail.subtotal, # Obligatorio, Resultado de VALOR UNITARIO por la CANTIDAD menos el DESCUENTO
               'tipo_de_igv': 1,
               'igv': igv, # Obligatorio ,total del IGV del producto
               'total': detail.price, # Total del producto
               'anticipo_regularizacion': False
            }
            items.append(item)

            
         venta_al_credito = []
         date = datetime.now()
         price_quotas = total_price / order_payment.installments
         if order_payment.installments > 1:
            for i in range(1, order_payment.installments + 1):
               next_month = date + relativedelta(months=1)
               venta_al_credito.append({
                  "cuota": i,
                  "fecha_de_pago":next_month.strftime('%d-%m-%Y'),
                  "importe": price_quotas,
               })
         else:
            venta_al_credito = ""

            # Generar new id InvoicePayments
         newInvoicePayments = InvoicePaymentsModel.objects.create()

         invoice_data = {
            'operacion': 'generar_comprobante',
            'tipo_de_comprobante': 2,
            'serie': 'BBB1',
            'numero': newInvoicePayments.id,            
            'sunat_transaction': 1,  
            'cliente_tipo_de_documento': 1, # 6:ruc, 1:DNI, 4:carnet-extranjeria, 7:Pasaporte, -:Variosm ventas menores a 700 soles
            'cliente_numero_de_documento': order_identification.document_number, # DNI, RUC
            'cliente_denominacion': order_identification.name, # Razón o nombre completo del CLIENTE.
            'cliente_direccion': order_delivery.address, #Direccion
            'cliente_email': order_identification.email, # Email del cliente
            'fecha_de_emision': datetime.now().strftime('%d-%m-%Y'),
            'moneda': 1, # 1:Soles, 2:Dolares ..
            'porcentaje_de_igv': 18.0,
            "descuento_global": discount_total, # Descuento global
            "total_descuento": discount_total, # Total descuento
            'total_gravada': total_gravada,
            'total_igv': igv_total,
            'total': total_price,
            'enviar_automaticamente_a_la_sunat': True,
            'enviar_automaticamente_al_cliente': True,
            'codigo_unico': '', # Código único generado y asignado por tu sistema. Por ejemplo puede estar compuesto por el tipo de documento, serie y número correlativo.

            # 'condiciones_de_pago' #Ejemplo: CRÉDITO 15 DÍAS
            'formato_de_pdf': "A5", #  Se puede elegir entre A4, A5 o TICKET. se deja en blanco se genera el formato definido por defecto en NUBEFACT
            'medio_de_pago': order_payment.payment_method, #Nota: Si es al Crédito, se debe de usar “venta_al_credito”
            'venta_al_credito': venta_al_credito,# Permite venta_al_credito anidadas, se refiere a los ITEMS o LÍNEAS del comprobante, el detalle en un cuadro más abajo
            'items': items,
         }

         nubefact_response = requests.post(
            url=url,
            headers={
                'Authorization': f'Bearer {token}'
            },
            json=invoice_data
         )

         response_data = nubefact_response.json()
         response_status = nubefact_response.status_code
      
         if response_status != 200:
            return None

         data = response_data.get('data', {})

         newInvoicePayments.name_client = order_identification.name
         newInvoicePayments.email_client = order_identification.email
         newInvoicePayments.serie = data.get('serie',None)
         newInvoicePayments.number = data.get('numero',None)
         newInvoicePayments.link = data.get('enlace',None)
         newInvoicePayments.pdf_link = data.get('enlace_del_pdf', None)
         newInvoicePayments.xml_link = data.get('enlace_del_xml', None)
         newInvoicePayments.accepted_by_sunat = data.get('aceptada_por_sunat', False)
         newInvoicePayments.string_for_qr_code = data.get('cadena_para_codigo_qr', None)
         newInvoicePayments.save()

         return data.get('enlace_del_pdf', None)
      except Exception as e:
         print(e)
         return None
        