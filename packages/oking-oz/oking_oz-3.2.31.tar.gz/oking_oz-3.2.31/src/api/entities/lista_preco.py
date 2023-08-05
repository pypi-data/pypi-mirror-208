from typing import List
from datetime import datetime


class Escopo:
    def __init__(self, tipo_escopo: int, codigos_escopo: List[str]):
        self.tipo_escopo: int = tipo_escopo
        self.codigos_escopo: List[str] = codigos_escopo


class ListaPreco:
    def __init__(self, descricao_lista_preco: str, codigo_lista_preco: str, codigo_filial: str, data_inicial: datetime, data_final: datetime, ativo: bool, prioridade: int, escopo: Escopo, calcula_ipi: str):
        self.descricao_lista_preco: str = descricao_lista_preco
        self.codigo_lista_preco: str = codigo_lista_preco
        self.codigo_filial: datetime = codigo_filial
        self.data_inicial: datetime = data_inicial
        self.data_final: str = data_final
        self.ativo: bool = ativo
        self.prioridade: int = prioridade
        self.escopo: Escopo = escopo
        self.calcula_ipi: str = calcula_ipi


class ListaPrecoResponse:
    def __init__(self, Identifiers, Status, Message, Protocolo):
        self.identifiers: List[str] = Identifiers
        self.status: int = Status
        self.message: str = Message
        self.protocol: str = Protocolo
