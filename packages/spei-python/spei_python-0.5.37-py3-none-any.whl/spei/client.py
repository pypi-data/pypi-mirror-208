
import base64
import logging

import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.hashes import SHA256
from lxml import etree  # noqa:  S410

from spei.resources import Orden, Respuesta
from spei.utils import format_data

SOAP_NS = 'http://schemas.xmlsoap.org/soap/envelope/'
PRAXIS_NS = 'http://www.praxis.com.mx/'

logger = logging.getLogger('spei')


class BaseClient(object):

    def __init__(
        self,
        priv_key,
        priv_key_passphrase,
        host,
        username,
        password,
        verify=False,
        http_client=requests,
    ):
        self.priv_key = priv_key
        self.priv_key_passphrase = priv_key_passphrase or None
        self.host = host
        self.session = http_client.Session()
        self.session.headers.update({'Content-Type': 'application/xml'})
        self.session.verify = verify
        self.session.auth = (username, password)

        if priv_key_passphrase:
            self.priv_key_passphrase = priv_key_passphrase.encode('ascii')

        self.pkey = serialization.load_pem_private_key(
            self.priv_key.encode('utf-8'),
            self.priv_key_passphrase,
            default_backend(),
        )

    def generate_checksum(self, message_data):
        message_as_bytes = format_data(message_data)

        signed_message = self.pkey.sign(
            message_as_bytes,
            padding.PKCS1v15(),
            SHA256(),
        )

        return base64.b64encode(signed_message)

    def registra_orden(self, orden_data, orden_cls=Orden, respuesta_cls=Respuesta):
        checksum = self.generate_checksum(orden_data)
        orden = orden_cls(op_firma_dig=checksum, **orden_data)
        soap_request = self._build_request(orden.build_xml())
        response = self.session.post(data=etree.tostring(soap_request), url=self.host)
        response.raise_for_status()
        respuesta = respuesta_cls.parse_respuesta(response.text)
        logger.info(respuesta)
        return respuesta

    def _build_request(self, mensaje_xml):
        namespaces_uris = {
            'soapenv': SOAP_NS,
            'prax': PRAXIS_NS,
        }

        envelope = etree.Element(
            etree.QName(SOAP_NS, 'Envelope'),
            nsmap=namespaces_uris,
        )
        body = etree.SubElement(envelope, etree.QName(SOAP_NS, 'Body'))
        ordenpago = etree.SubElement(body, etree.QName(PRAXIS_NS, 'ordenpago'))
        mensaje = etree.tostring(mensaje_xml)
        ordenpago.text = etree.CDATA(mensaje)

        logger.info(etree.tostring(envelope))

        return envelope
