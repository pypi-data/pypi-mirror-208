from enum import Enum


class TipoPagoOrdenPago(str, Enum):
    devolucion_no_acreditada = '0'
    tercero_a_tercero = '1'
    tercero_a_ventanilla = '2'
    devolucion_extemporanea_no_acreditada = '16'
    devolucion_acreditada = '17'
    devolucion_extemporanea_acreditada = '18'
    devolucion_especial_acreditada = '23'
    devolucion_extemporanea_especial_acreditada = '24'


class TipoOrdenPago(str, Enum):
    envio = 'E'
    recepcion = 'R'


class TipoCuentaOrdenPago(str, Enum):
    clabe = '40'


class PrioridadOrdenPago(str, Enum):
    normal = 0
    alta = 1


class CategoriaOrdenPago(str, Enum):
    cargar_odp = 'CARGAR_ODP'
    cargar_odp_respuesta = 'CARGAR_ODP_RESPUESTA'
    odps_liquidadas_cargos = 'ODPS_LIQUIDADAS_CARGOS'
    odps_liquidadas_cargos_respuesta = 'ODPS_LIQUIDADAS_CARGOS_RESPUESTA'
    odps_liquidadas_abonos = 'ODPS_LIQUIDADAS_ABONOS'
    odps_liquidadas_abonos_respuesta = 'ODPS_LIQUIDADAS_ABONOS'
    odps_canceladas_local = 'ODPS_CANCELADAS_LOCAL'
    odps_canceladas_local_respuesta = 'ODPS_CANCELADAS_LOCAL_RESPUESTA'
    odps_canceladas_x_banxico = 'ODPS_CANCELADAS_X_BANXICO'
    odps_canceladas_x_banxico_respuesta = 'ODPS_CANCELADAS_X_BANXICO_RESPUESTA'


class EstadoOrdenPago(str, Enum):
    liquidada = 'LQ'
    liberada = 'L'
    capturada = 'C'
    autorizada = 'A'


class ClaveOrdenanteOrdenPago(int, Enum):
    AMU = 90714


class FolioOrdenPago(str, Enum):
    cargar_odp = '-1'


class MedioEntregaOrdenPago(str, Enum):
    local = '1'
    spei = '2'
    archivos = '3'
    devoluciones = '4'
    devoluciones_abono = '5'
    ce = '6'
    cei = '7'
    hsbc = '8'
    htvf = '9'
    dtp = '10'
    ifai = '13'
    swift = '17'
    nomina = '18'
