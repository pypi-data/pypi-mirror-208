from datetime import datetime

class ClienteErpCode:
    cpf_cnpj: str
    codigo_cliente: str

    def __init__(self, cpf_cnpj: str, codigo_cliente: str) -> None:
        self.cpf_cnpj = cpf_cnpj
        self.codigo_cliente = codigo_cliente