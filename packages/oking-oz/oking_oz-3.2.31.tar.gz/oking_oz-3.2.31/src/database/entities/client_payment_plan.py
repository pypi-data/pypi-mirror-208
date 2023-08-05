from typing import List
from datetime import datetime

class ClientPaymentPlan:
    def __init__(self, codigo_cliente, formas_pagamento):
        self.code_client: str = codigo_cliente
        self.payment_methods: List[str] = formas_pagamento

