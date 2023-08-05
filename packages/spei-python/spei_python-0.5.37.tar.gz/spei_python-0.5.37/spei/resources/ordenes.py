import re

from lxml import etree
from pydantic import BaseModel, conint, validator

from spei import types
from spei.utils import to_snake_case, to_upper_camel_case  # noqa: WPS347


class Orden(BaseModel):
    categoria: types.CategoriaOrdenPago

    op_fecha_oper: int
    op_folio: str
    op_ins_clave: conint(gt=9999, lt=99999)  # noqa: WPS432
    op_monto: str
    op_tp_clave: types.TipoPagoOrdenPago
    op_cve_rastreo: str
    op_estado: types.EstadoOrdenPago
    op_tipo_orden: types.TipoOrdenPago
    op_prioridad: types.PrioridadOrdenPago
    op_me_clave: types.MedioEntregaOrdenPago
    op_topologia: str
    op_usu_clave: str

    op_firma_dig: str = None

    op_nom_ord: str = None
    op_tc_clave_ord: types.TipoCuentaOrdenPago = types.TipoCuentaOrdenPago.clabe
    op_cuenta_ord: str = None
    op_rfc_curp_ord: str = None
    op_ord_clave: types.ClaveOrdenanteOrdenPago = types.ClaveOrdenanteOrdenPago.AMU

    op_nom_ben: str = None
    op_tc_clave_ben: types.TipoCuentaOrdenPago = None
    op_cuenta_ben: str = None
    op_rfc_curp_ben: str = None

    op_iva: float = None
    op_ref_numerica: str = None

    op_nom_ben_2: str = None
    op_tc_clave_ben_2: int = None
    op_cuenta_ben_2: str = None
    op_rfc_curp_ben_2: str = None

    op_clave: int = None
    op_concepto_pago: str = None
    op_concepto_pag_2: str = None
    op_ref_cobranza: str = None

    op_fecha_cap: int = None

    class Config:  # noqa: WPS306, WPS431
        use_enum_values = True

    @validator('op_fecha_oper')
    def op_fecha_oper_must_be_iso_format(cls, value):  # noqa: WPS110, N805
        regex = re.compile(r'^\d{4}(0[1-9]|1[0-2])(0[1-9]|[12][0-9]|3[01])$')
        if re.findall(regex, str(value)):
            return value

        raise ValueError('must be in YYYYMMDD format')

    def build_xml(self):
        mensaje = etree.Element('mensaje', categoria=self.categoria)
        orden_pago = etree.SubElement(mensaje, 'ordenpago')

        for element, value in self.dict(exclude_none=True, exclude={'categoria', 'op_ord_clave'}).items():  # noqa: WPS110, E501
            if element in self.__fields__:
                if element == 'op_firma_dig':
                    subelement = etree.SubElement(orden_pago, 'opFirmaDig')
                    subelement.text = str(value)
                    continue
                upper_camel_case_element = to_upper_camel_case(element)
                subelement = etree.SubElement(orden_pago, upper_camel_case_element)
                subelement.text = str(value)

        return mensaje

    @classmethod
    def parse_xml(cls, orden_xml):
        orden = etree.fromstring(orden_xml)  # noqa: S320
        body = orden.find('{http://schemas.xmlsoap.org/soap/envelope/}Body')
        orden_pago = body.find('{http://www.praxis.com.mx/}ordenpago')

        mensaje_xml = etree.fromstring(orden_pago.text)
        orden = mensaje_xml.find('ordenpago')

        orden_data = {
            'categoria': mensaje_xml.attrib['categoria'],
        }

        for element in orden.getchildren():
            tag = to_snake_case(element.tag)
            if tag in cls.__fields__:
                orden_data[tag] = element.text

        return cls(**orden_data)


class Respuesta(BaseModel):
    id: str
    fecha_oper: int
    err_codigo: int
    err_descripcion: str

    @classmethod
    def parse_respuesta(cls, respuesta_xml):
        response = None

        mensaje = etree.fromstring(respuesta_xml)  # noqa: S320
        for element in mensaje.getchildren():
            response = element.find('{http://www.praxis.com.mx/}respuesta')

        response = etree.fromstring(bytes(response.text, encoding='cp850'))  # noqa: S320, E501

        respuesta = response.find('respuesta')

        respuesta_data = {}
        for element in respuesta.getchildren():  # noqa: WPS440
            tag = to_snake_case(element.tag)
            respuesta_data[tag] = element.text

        return cls(**respuesta_data)
