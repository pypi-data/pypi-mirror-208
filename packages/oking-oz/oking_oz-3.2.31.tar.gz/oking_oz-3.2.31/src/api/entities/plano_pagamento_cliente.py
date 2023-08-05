# Será criado uma lista
# # com leiaute da http://api.gmimportacao.openk.com.br/ok/swagger/ui/index#!/client/formapagamento
from typing import List
from datetime import datetime

class PlanoPagamentoCliente:
    def __init__(self, codigo_cliente, formas_pagamento):
        self.codigo_cliente: str = codigo_cliente
        self.formas_pagamento: List[str] = formas_pagamento


