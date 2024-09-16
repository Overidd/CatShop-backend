from payment_gateway.utils import (
   OrderIdentificationType,
   OrderDeliveryType,
   OrderPaymentType,
)

from .models import InvoicePaymentsModel

import requests
from django.conf import settings
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Union


def invoicePayments(order, order_identification:OrderIdentificationType, order_delivery:OrderDeliveryType, order_payment:OrderPaymentType) -> Union[str, None]:
      try:
         url = settings.URL_API_NUBEFACT
         token = settings.API_KEY_NUBEFACT
         order_details = order.order_detail.all()

         items = []
         discount_total = 0
         total_gravada = 0
         igv_total = 0
         total_price = 0
         for detail in order_details:
            discount = detail.discount
            # Calcular valor unitario sin IGV
            valor_unitario = detail.price_unit / 1.18

            # Calcular IGV
            igv = round(valor_unitario * 0.18, 2)

            # Calcular subtotal y total
            subtotal = (valor_unitario * detail.quantity) - discount
            total = detail.price_unit * detail.quantity

            discount_total += discount
            total_gravada += valor_unitario * detail.quantity
            igv_total += igv * detail.quantity
            total_price += total - discount

            item = {
               'unidad_de_medida': 'NIU',
               'descripcion': detail.name_product,
               'cantidad': detail.quantity,
               # 'codigo': 'C001', # Opcional
               'valor_unitario': valor_unitario,  # Obligatorio, Valor sin IGV
               'precio_unitario': detail.price_unit, # Obligatorio, Valor con IGV
               'descuento': discount,
               'subtotal': subtotal, # Obligatorio, Resultado de VALOR UNITARIO por la CANTIDAD menos el DESCUENTO
               'tipo_de_igv': 1,
               'igv': round(igv * detail.quantity, 2),
               'total': total, # Total del producto
               'anticipo_regularizacion': False
            }
            items.append(item)

         # Agregar el costo de delivery, si existe
         if order.price_delivery > 0:
            delivery_price = order.price_delivery
            valor_unitario_delivery = round(delivery_price / 1.18, 2)
            igv_delivery = round(valor_unitario_delivery * 0.18, 2)

            total_gravada += valor_unitario_delivery
            igv_total += igv_delivery
            total_price += delivery_price

            delivery_item = {
               'unidad_de_medida': 'ZZ',
               'descripcion': 'Costo de Envío',
               'cantidad': 1,
               'valor_unitario': valor_unitario_delivery,
               'precio_unitario': delivery_price,
               'descuento': 0,
               'subtotal': valor_unitario_delivery,
               'tipo_de_igv': 1,
               'igv': igv_delivery,
               'total': delivery_price,
               'anticipo_regularizacion': False
            }
            items.append(delivery_item)

         # Redondear los totales finales
         total_gravada = total_gravada
         igv_total = igv_total
         total_price = total_price

         venta_al_credito = []
         date = datetime.now()
         price_quotas = total_price / order_payment.installments, 2
         print(price_quotas)
         if order_payment.installments > 1:
            for i in range(1, order_payment.installments + 1):
                next_month = date + relativedelta(months=i)
                venta_al_credito.append({
                  "cuota": i,
                  "fecha_de_pago": next_month.strftime('%d-%m-%Y'),
                  "importe": price_quotas,
                })
         else:
            venta_al_credito = ""

        # Generar nuevo id InvoicePayments
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
            'moneda': 1,  # 1:Soles, 2:Dolares 
            'porcentaje_de_igv': 18.0,
            "descuento_global": discount_total,# Descuento global
            "total_descuento": discount_total, # Total descuento
            'total_gravada': total_gravada,
            'total_igv': igv_total,
            'total': total_price,
            'enviar_automaticamente_a_la_sunat': True,
            'enviar_automaticamente_al_cliente': True,
            'codigo_unico': order.code, # Código único generado y asignado por tu sistema. Por ejemplo puede estar compuesto por el tipo de documento, serie y número correlativo.
            'formato_de_pdf': "A5",
            'medio_de_pago': order_payment.payment_method,
            'venta_al_credito': venta_al_credito,
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
            print(response_data)
            return None
         
         newInvoicePayments.name_client = order_identification.name
         newInvoicePayments.email_client = order_identification.email
         newInvoicePayments.serie = response_data.get('serie',None)
         newInvoicePayments.number = response_data.get('numero',None)
         newInvoicePayments.link = response_data.get('enlace',None)
         newInvoicePayments.pdf_link = response_data.get('enlace_del_pdf', None)
         newInvoicePayments.xml_link = response_data.get('enlace_del_xml', None)
         newInvoicePayments.accepted_by_sunat = response_data.get('aceptada_por_sunat', False)
         newInvoicePayments.string_for_qr_code = response_data.get('cadena_para_codigo_qr', None)
         newInvoicePayments.save()

         return response_data.get('enlace_del_pdf', None)
      except Exception as e:
         print(e)
         return None
        