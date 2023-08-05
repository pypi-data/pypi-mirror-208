import datetime
import pytz
import math

import re

from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings
from .settings import (
    XSLT_PATH_CFDI, XSLT_PATH_TFD, TMP_DIR,
)

#from .models import models
from django.utils import timezone
from importlib import import_module
from . import constants


def to_decimal(s):
    """
    Docs.
    """
    try:
        s = str(s)
        s = s.replace("$", "")
        d = Decimal("".join(s.split(",")))
        return d if not math.isnan(d) else 0
    except:
        return Decimal("0")


def to_int(s):
    """
    Docs.
    """
    try:
        return int(s)
    except:
        return 0


def to_precision_decimales(valor_decimal, precision=2):
    """
    Docs.
    """
    if not valor_decimal:
        return Decimal("0.00")
    return Decimal("%s" % valor_decimal).quantize(
        Decimal("0.%0*d" % (precision, 1)), ROUND_HALF_UP
    )


def to_datetime(date, max=False, use_localtime=True, min=False):
    """
    Convierte un datetime naive en aware.
    """
    if max and min:
        raise ValueError(
            u"Los argumentos max y min deben ser mutuamente excluyentes"
        )

    if hasattr(date, "tzinfo") and date.tzinfo and not min and not max:
        return date

    if not isinstance(date, (datetime.date, datetime.datetime)):
        return date

    dt = datetime.datetime
    current_tz = timezone.get_current_timezone() if use_localtime else pytz.utc

    t = dt.min.time()

    # si date es datetime conservamos la hora que trae
    if not min and isinstance(date, (datetime.datetime,)):
        t = date.time()

    if max:
        t = dt.max.time()

    if settings.USE_TZ:
        return current_tz.localize(dt.combine(date, t))

    return timezone.localtime(dt.combine(date, t))

def load_func(func_path):
    """
    Retorna la funcion segun el path especificado, ej:
    cfdi.utils.load_func
    """
    package, module = func_path.rsplit('.', 1)
    return getattr(import_module(package), module)

def obtener_cfdi_base(configuracion, timbrado_prueba=None, pac=None, 
    create_cfdi_instance=False):

    from .classes import CFDI
    from datetime import datetime

    if timbrado_prueba is None:
        timbrado_prueba = configuracion.get("timbrado_prueba")

    cfdi = CFDI() 
    cfdi.noCertificado = configuracion["no_certificado"]
    cfdi.NoCertificado = configuracion["no_certificado"]
    cfdi.certificado = configuracion["certificado"]
    cfdi.Certificado = configuracion["certificado"]
    cfdi.Exportacion = "01"
    if not cfdi.Certificado:
        cfdi.cfdi_status = "No se detectó certificado, corrobore que el certificado de sellos cargado esté correcto"
        return cfdi

    
    #Emisor
    cfdi.emisor_rfc = configuracion["rfc"]
    cfdi.emisor_nombre = configuracion["razon_social"]
    
    cfdi.Emisor = {}
    cfdi.Emisor["Rfc"] = configuracion["rfc"]
    cfdi.Emisor["Nombre"] = configuracion["razon_social"]
    cfdi.Emisor["RegimenFiscal"] = configuracion["regimen_fiscal"]
    cfdi.regimen_fiscal = configuracion["regimen_fiscal"]
    cfdi.pem_path = configuracion.get("pem_path")
    cfdi.pem = configuracion.get("pem")
    if configuracion.get("nueva_version"):
        cfdi.Version = "4.0"
    else:
        cfdi.Version = "3.3"
    #cfdi.pfx_path = configuracion.get("pfx_path")
    cfdi.pfx = configuracion.get("pfx")
    cfdi.suprimir_caracteres_especiales = configuracion.get("suprimir_caracteres_especiales")
    

    
    cfdi.openssl_algo_hash = "-sha256"
    cfdi.TIMBRADO_PRUEBAS = timbrado_prueba 
    cfdi.PAC = pac or configuracion.get("pac")

    if create_cfdi_instance:
        cfdi_instance = Cfdi()
        cfdi_instance.save()
        cfdi.cfdi_instance = cfdi_instance
        cfdi.cfdi_instance.cfdi_status = ""

    return cfdi    


def obtener_cancelacion_cfdi_base(configuracion, uuid, xml, timbrado_prueba=None, 
    pac=None, motivo_cancelacion=None, uuid_relacionado=None):
    cfdi = obtener_cfdi_base(
        configuracion, 
        timbrado_prueba=timbrado_prueba, 
    )
    cfdi.rfc = cfdi.rfc = configuracion["rfc"]
    cfdi.uuid = cfdi.cfdi_uuid = uuid
    cfdi.key = configuracion["key"]
    cfdi.csd_pass = configuracion["csd_pass"]
    cfdi.cfdi_xml = xml
    cfdi.motivo_cancelacion = motivo_cancelacion
    cfdi.uuid_relacionado_cancelacion = uuid_relacionado
    return cfdi

def escape(string):
    if string == None:
        return ''
    string = str(string)
    string = " ".join(string.split())
    return string.replace("&", "&amp;")\
      .replace("'", "&apos;")\
      .replace('"', "&quot;")\
      .replace("<", "&lt;")\
      .replace(">", "&gt;")\
      .replace("|", "")\
      .replace("\n", " ")

def unescape(string):
    if string == None:
        return ''
    return str(string).replace("&apos;", "'")\
      .replace('&quot;', '"')\
      .replace("&lt;", "<")\
      .replace("&gt;", ">")\
      .replace("&amp;", "&")

def get_field(field, value):
    """
    Agrega el campo al XML según el valor de dicho
    campo en la clase CFDI.
    """
    if value == "" or value is None:
        return ""

    return '%s="%s" ' % (field, escape(value))

def get_importe_isr_resico_pf(importe_venta_nominal):
    
    for nivel in constants.TABLAS_RESICO_PF:
        if importe_venta_nominal <= Decimal(nivel[0]):
            return importe_venta_nominal* Decimal(nivel[1] / 100)
    
    raise ValueError(f"El importe de la venta nominal no puede ser mayor a {nivel[0]}")

def get_fecha_xml(comprobante):
    fecha_entrada = datetime.datetime.strptime(
        comprobante.complemento.timbrefiscaldigital.fechatimbrado_str[:19], 
        "%Y-%m-%dT%H:%M:%S"
    )
    tz = "America/Mexico_City"
    fecha_entrada = pytz.timezone(tz).localize(fecha_entrada)
    return fecha_entrada

def chunkstring(string, length):
    return (string[0+i:length+i] for i in range(0, len(string), length))

def to_decimal_prodigia(valor, precision=2):
    return to_precision_decimales(valor, precision)
    
    forzar_redondear_abajo = False
    try:
        valor_split = str(Decimal(valor).normalize()).split(".")[-1] 
        if len(valor_split) > 2 and int(valor_split[2]) <= 5:
            forzar_redondear_abajo = True
    except:
        pass
        
    if forzar_redondear_abajo:
        return to_precision_decimales((math.floor(Decimal(valor) * 100) / 100), precision)
    else:
        return to_precision_decimales(valor, precision)

