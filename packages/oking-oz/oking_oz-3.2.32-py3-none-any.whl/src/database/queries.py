from enum import IntEnum


class IntegrationType(IntEnum):
    LISTA_PRECO = 1,
    PRECO = 2,
    ESTOQUE = 3,
    PRODUTO = 4,
    LISTA_PRECO_PRODUTO = 5,
    REPRESENTANTE = 6,
    IMPOSTO = 7,
    CLIENTE = 8,
    PLANO_PAGAMENTO_CLIENTE = 9


# Queries nao podem terminar com ponto e virgula

def get_product_protocol_command(connection_type: str):
    if connection_type.lower() == 'mysql':
        return 'update openk_semaforo.produto set data_sincronizacao = now() where codigo_erp = %s and codigo_erp_sku = %s'
    elif connection_type.lower() == 'oracle':
        return 'update openk_semaforo.produto set data_sincronizacao = SYSDATE where codigo_erp = :1 and codigo_erp_sku = :2'
    elif connection_type.lower() == 'sql':
        return 'update openk_semaforo.produto set data_sincronizacao = getdate() where codigo_erp = ? and codigo_erp_sku = ?'


def get_stock_protocol_command(connection_type: str):
    if connection_type.lower() == 'mysql':
        return 'update openk_semaforo.estoque_produto set data_sincronizacao = now() where codigo_erp = %s'
    elif connection_type.lower() == 'oracle':
        return 'update openk_semaforo.estoque_produto set data_sincronizacao = SYSDATE where codigo_erp = :codigo_erp'
    elif connection_type.lower() == 'sql':
        return 'update openk_semaforo.estoque_produto set data_sincronizacao = getdate() where codigo_erp = ?'


def get_price_protocol_command(connection_type: str):
    if connection_type.lower() == 'mysql':
        return 'update openk_semaforo.preco_produto set data_sincronizacao = now() where codigo_erp = %s and preco_atual = %s'
    elif connection_type.lower() == 'oracle':
        return 'update openk_semaforo.preco_produto set data_sincronizacao = SYSDATE where codigo_erp = :1 and preco_atual = :2'
    elif connection_type.lower() == 'sql':
        return 'update openk_semaforo.preco_produto set data_sincronizacao = getdate() where codigo_erp = ? and preco_atual = ?'


def get_insert_client_command(connection_type: str):
    if connection_type.lower() == 'mysql':
        return '''insert into openk_semaforo.cliente (nome, razao_social, cpf, cnpj, email, telefone_residencial, telefone_celular, cep, 
														tipo_logradouro, logradouro, numero, complemento, bairro, cidade, estado, referencia, direcao, codigo_ibge)
					values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) '''
    elif connection_type.lower() == 'oracle':
        return '''INSERT INTO OPENK_SEMAFORO.CLIENTE (NOME, RAZAO_SOCIAL, CPF, CNPJ, EMAIL, TELEFONE_RESIDENCIAL, TELEFONE_CELULAR, CEP, 
														TIPO_LOGRADOURO, LOGRADOURO,NUMERO, COMPLEMENTO, BAIRRO, CIDADE, ESTADO, REFERENCIA, DIRECAO, CODIGO_IBGE) 
				VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17, :18) '''
    elif connection_type.lower() == 'sql':
        return '''insert into openk_semaforo.cliente (nome, razao_social, cpf, cnpj, email, telefone_residencial, telefone_celular, cep, 
														tipo_logradouro, logradouro, numero, complemento, bairro, cidade, estado, referencia, direcao, codigo_ibge)
					values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) '''


def get_insert_b2b_client_command(connection_type: str):
    if connection_type.lower() == 'mysql':
        return '''insert into openk_semaforo.cliente (nome, razao_social, cpf, cnpj, email, telefone_residencial, telefone_celular, cep, 
														tipo_logradouro, logradouro, numero, complemento, bairro, cidade, estado, referencia, direcao, inscricao_estadual, codigo_ibge, cliente_erp)
					values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) '''
    elif connection_type.lower() == 'oracle':
        return '''INSERT INTO OPENK_SEMAFORO.CLIENTE (NOME, RAZAO_SOCIAL, CPF, CNPJ, EMAIL, TELEFONE_RESIDENCIAL, TELEFONE_CELULAR, CEP, 
														TIPO_LOGRADOURO, LOGRADOURO,NUMERO, COMPLEMENTO, BAIRRO, CIDADE, ESTADO, REFERENCIA, DIRECAO, INSCRICAO_ESTADUAL, CODIGO_IBGE, CLIENTE_ERP) 
				VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17, :18, :19, :20) '''
    elif connection_type.lower() == 'sql':
        return '''insert into openk_semaforo.cliente (nome, razao_social, cpf, cnpj, email, telefone_residencial, telefone_celular, cep, 
														tipo_logradouro, logradouro, numero, complemento, bairro, cidade, estado, referencia, direcao, inscricao_estadual, codigo_ibge, cliente_erp)
					values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) '''


def get_insert_b2c_client_command(connection_type: str):
    if connection_type.lower() == 'mysql':
        return '''insert into openk_semaforo.cliente (nome, razao_social, cpf, cnpj, email, telefone_residencial, telefone_celular, cep, 
														tipo_logradouro, logradouro, numero, complemento, bairro, cidade, estado, referencia, direcao)
					values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) '''
    elif connection_type.lower() == 'oracle':
        return '''INSERT INTO OPENK_SEMAFORO.CLIENTE (NOME, RAZAO_SOCIAL, CPF, CNPJ, EMAIL, TELEFONE_RESIDENCIAL, TELEFONE_CELULAR, CEP, 
														TIPO_LOGRADOURO, LOGRADOURO,NUMERO, COMPLEMENTO, BAIRRO, CIDADE, ESTADO, REFERENCIA, DIRECAO) 
				VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17) '''
    elif connection_type.lower() == 'sql':
        return '''insert into openk_semaforo.cliente (nome, razao_social, cpf, cnpj, email, telefone_residencial, telefone_celular, cep, 
														tipo_logradouro, logradouro, numero, complemento, bairro, cidade, estado, referencia, direcao)
					values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) '''


def get_insert_order_command(connection_type: str):
    if connection_type.lower() == 'mysql':
        return '''insert into openk_semaforo.pedido (pedido_id, pedido_venda_id, data_pedido, status, cliente_id, valor, valor_desconto, valor_frete, 
					valor_adicional, data_pagamento, tipo_pagamento, bandeira, parcelas, condicao_pagamento_erp, codigo_rastreio, data_previsao_entrega, 
					transportadora, modo_envio, canal_id, loja_id, opcao_pagamento_erp, end_entrega_cep, end_entrega_tipo_logradouro, 
					end_entrega_logradouro, end_entrega_numero, end_entrega_complemento, end_entrega_bairro, end_entrega_cidade, 
					end_entrega_estado, end_entrega_referencia_ent, end_entrega_codigo_ibge)
					values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) '''
    elif connection_type.lower() == 'oracle':
        return '''INSERT INTO OPENK_SEMAFORO.PEDIDO (PEDIDO_ID, PEDIDO_VENDA_ID, DATA_PEDIDO, STATUS, CLIENTE_ID, VALOR, VALOR_DESCONTO, VALOR_FRETE, 
					VALOR_ADICIONAL, DATA_PAGAMENTO, TIPO_PAGAMENTO, BANDEIRA, PARCELAS, CONDICAO_PAGAMENTO_ERP, CODIGO_RASTREIO, DATA_PREVISAO_ENTREGA, 
					TRANSPORTADORA, MODO_ENVIO, CANAL_ID, LOJA_ID, OPCAO_PAGAMENTO_ERP, END_ENTREGA_CEP, END_ENTREGA_TIPO_LOGRADOURO, 
					END_ENTREGA_LOGRADOURO, END_ENTREGA_NUMERO, END_ENTREGA_COMPLEMENTO, END_ENTREGA_BAIRRO, END_ENTREGA_CIDADE, 
					END_ENTREGA_ESTADO, END_ENTREGA_REFERENCIA_ENT, END_ENTREGA_CODIGO_IBGE)
					VALUES (:1, :2, TO_DATE(:3, 'YYYY-MM-DD HH24:MI:SS'), :4, :5, :6, :7, :8, :9, TO_DATE(:10, 'YYYY-MM-DD HH24:MI:SS'), :11, :12, :13, :14, :15, TO_DATE(:16, 'YYYY-MM-DD HH24:MI:SS'), :17, :18, :19, :20, :21, :22, :23, :24, :25, :26, :27, :28, :29, :30, :31) '''
    elif connection_type.lower() == 'sql':
        return '''insert into openk_semaforo.pedido (pedido_id, pedido_venda_id, data_pedido, status, cliente_id, valor, valor_desconto, valor_frete, 
					valor_adicional, data_pagamento, tipo_pagamento, bandeira, parcelas, condicao_pagamento_erp, codigo_rastreio, data_previsao_entrega, 
					transportadora, modo_envio, canal_id, loja_id, opcao_pagamento_erp, end_entrega_cep, end_entrega_tipo_logradouro, 
					end_entrega_logradouro, end_entrega_numero, end_entrega_complemento, end_entrega_bairro, end_entrega_cidade, 
					end_entrega_estado, end_entrega_referencia_ent, end_entrega_codigo_ibge)
					values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) '''


def get_insert_b2c_order_command(connection_type: str):
    if connection_type.lower() == 'mysql':
        return '''insert into openk_semaforo.pedido (pedido_id, pedido_venda_id, data_pedido, status, cliente_id, valor, valor_desconto, valor_frete, 
					valor_adicional, data_pagamento, tipo_pagamento, bandeira, parcelas, condicao_pagamento_erp, codigo_rastreio, data_previsao_entrega, 
					transportadora, modo_envio, canal_id, loja_id, end_entrega_cep, end_entrega_tipo_logradouro, end_entrega_logradouro, 
					end_entrega_numero, end_entrega_complemento, end_entrega_bairro, end_entrega_cidade, end_entrega_estado, 
					end_entrega_referencia_ent, end_entrega_codigo_ibge)
					values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) '''
    elif connection_type.lower() == 'oracle':
        return '''INSERT INTO OPENK_SEMAFORO.PEDIDO (PEDIDO_ID, PEDIDO_VENDA_ID, DATA_PEDIDO, STATUS, CLIENTE_ID, VALOR, VALOR_DESCONTO, VALOR_FRETE, 
					VALOR_ADICIONAL, DATA_PAGAMENTO, TIPO_PAGAMENTO, BANDEIRA, PARCELAS, CONDICAO_PAGAMENTO_ERP, CODIGO_RASTREIO, DATA_PREVISAO_ENTREGA, 
					TRANSPORTADORA, MODO_ENVIO, CANAL_ID, LOJA_ID, END_ENTREGA_CEP, END_ENTREGA_TIPO_LOGRADOURO, END_ENTREGA_LOGRADOURO, 
					END_ENTREGA_NUMERO, END_ENTREGA_COMPLEMENTO, END_ENTREGA_BAIRRO, END_ENTREGA_CIDADE, END_ENTREGA_ESTADO, 
					END_ENTREGA_REFERENCIA_ENT, END_ENTREGA_CODIGO_IBGE)
					VALUES (:1, :2, TO_DATE(:3, 'YYYY-MM-DD HH24:MI:SS'), :4, :5, :6, :7, :8, :9, TO_DATE(:10, 'YYYY-MM-DD HH24:MI:SS'), :11, :12, :13, :14, :15, TO_DATE(:16, 'YYYY-MM-DD HH24:MI:SS'), :17, :18, :19, :20, :21, :22, :23, :24, :25, :26, :27, :28, :29, :30) '''
    elif connection_type.lower() == 'sql':
        return '''insert into openk_semaforo.pedido (pedido_id, pedido_venda_id, data_pedido, status, cliente_id, valor, valor_desconto, valor_frete, 
					valor_adicional, data_pagamento, tipo_pagamento, bandeira, parcelas, condicao_pagamento_erp, codigo_rastreio, data_previsao_entrega, 
					transportadora, modo_envio, canal_id, loja_id, end_entrega_cep, end_entrega_tipo_logradouro, 
					end_entrega_logradouro, end_entrega_numero, end_entrega_complemento, end_entrega_bairro, end_entrega_cidade, 
					end_entrega_estado, end_entrega_referencia_ent, end_entrega_codigo_ibge)
					values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) '''


def get_insert_b2b_order_command(connection_type: str):
    if connection_type.lower() == 'mysql':
        return '''insert into openk_semaforo.pedido (pedido_id, pedido_venda_id, data_pedido, status, cliente_id, valor, valor_desconto, valor_frete, 
					valor_adicional, data_pagamento, tipo_pagamento, bandeira, parcelas, condicao_pagamento_erp, codigo_rastreio, data_previsao_entrega, 
					transportadora, modo_envio, canal_id, representante_erp, loja_id, opcao_pagamento_erp, cnpj_intermediador, codigo_pedido_canal, end_entrega_cep, end_entrega_tipo_logradouro, end_entrega_logradouro, end_entrega_numero, end_entrega_complemento, end_entrega_bairro, end_entrega_cidade, end_entrega_estado, end_entrega_referencia_ent, end_entrega_codigo_ibge)
					values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) '''
    elif connection_type.lower() == 'oracle':
        return '''INSERT INTO OPENK_SEMAFORO.PEDIDO (PEDIDO_ID, PEDIDO_VENDA_ID, DATA_PEDIDO, STATUS, CLIENTE_ID, VALOR, VALOR_DESCONTO, VALOR_FRETE, 
					VALOR_ADICIONAL, DATA_PAGAMENTO, TIPO_PAGAMENTO, BANDEIRA, PARCELAS, CONDICAO_PAGAMENTO_ERP, CODIGO_RASTREIO, DATA_PREVISAO_ENTREGA, 
					TRANSPORTADORA, MODO_ENVIO, CANAL_ID, REPRESENTANTE_ERP, LOJA_ID, OPCAO_PAGAMENTO_ERP, CNPJ_INTERMEDIADOR, CODIGO_PEDIDO_CANAL, END_ENTREGA_CEP, END_ENTREGA_TIPO_LOGRADOURO, END_ENTREGA_LOGRADOURO, END_ENTREGA_NUMERO, END_ENTREGA_COMPLEMENTO, END_ENTREGA_BAIRRO, END_ENTREGA_CIDADE, END_ENTREGA_ESTADO, END_ENTREGA_REFERENCIA_ENT, END_ENTREGA_CODIGO_IBGE)
					VALUES (:1, :2, TO_DATE(:3, 'YYYY-MM-DD HH24:MI:SS'), :4, :5, :6, :7, :8, :9, TO_DATE(:10, 'YYYY-MM-DD HH24:MI:SS'), :11, :12, :13, :14, :15, TO_DATE(:16, 'YYYY-MM-DD HH24:MI:SS'), :17, :18, :19, :20, :21, :22, :23, :24, :25, :26, :27, :28, :29, :30, :31, :32, :33, :34 ) '''
    elif connection_type.lower() == 'sql':
        return '''insert into openk_semaforo.pedido (pedido_id, pedido_venda_id, data_pedido, status, cliente_id, valor, valor_desconto, valor_frete, 
					valor_adicional, data_pagamento, tipo_pagamento, bandeira, parcelas, condicao_pagamento_erp, codigo_rastreio, data_previsao_entrega, 
					transportadora, modo_envio, canal_id, representante_erp, loja_id, opcao_pagamento_erp, cnpj_intermediador, codigo_pedido_canal, end_entrega_cep, end_entrega_tipo_logradouro, end_entrega_logradouro, end_entrega_numero, end_entrega_complemento, end_entrega_bairro, end_entrega_cidade, end_entrega_estado, end_entrega_referencia_ent, end_entrega_codigo_ibge)
					values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? , ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) '''


def get_update_b2b_order_command(connection_type: str):
    if connection_type.lower() == 'mysql':
        return '''update openk_semaforo.pedido
					SET condicao_pagamento_erp = %s
					  , transportadora = %s
					  , modo_envio = %s
					  , canal_id = %s
					  , representante_erp = %s
					  , opcao_pagamento_erp = %s
					  , cnpj_intermediador = %s
					  , codigo_pedido_canal = %s
					  , end_entrega_cep = %s
					  , end_entrega_tipo_logradouro = %s
					  , end_entrega_logradouro = %s
					  , end_entrega_numero = %s
					  , end_entrega_complemento = %s
					  , end_entrega_bairro = %s
					  , end_entrega_cidade = %s
					  , end_entrega_estado = %s
					  , end_entrega_referencia_ent = %s
					  , end_entrega_codigo_ibge = %s
					WHERE pedido_id = %s '''
    elif connection_type.lower() == 'oracle':
        return '''UPDATE OPENK_SEMAFORO.PEDIDO
					SET CONDICAO_PAGAMENTO_ERP = :1
					  , TRANSPORTADORA = :2
					  , MODO_ENVIO = :3
					  , CANAL_ID = :4
					  , REPRESENTANTE_ERP = :5
					  , OPCAO_PAGAMENTO_ERP = :6
					  , CNPJ_INTERMEDIADOR = :7
					  , CODIGO_PEDIDO_CANAL = :8
					  , END_ENTREGA_CEP = :9
					  , END_ENTREGA_TIPO_LOGRADOURO = :10
					  , END_ENTREGA_LOGRADOURO = :11
					  , END_ENTREGA_NUMERO = :12
					  , END_ENTREGA_COMPLEMENTO = :13
					  , END_ENTREGA_BAIRRO = :14
					  , END_ENTREGA_CIDADE = :15
					  , END_ENTREGA_ESTADO = :16
					  , END_ENTREGA_REFERENCIA_ENT = :17
					  , END_ENTREGA_CODIGO_IBGE = :18
					WHERE PEDIDO_ID = :19 '''
    elif connection_type.lower() == 'sql':
        return '''update openk_semaforo.pedido
					SET condicao_pagamento_erp = ?
					  , transportadora = ?
					  , modo_envio = ?
					  , canal_id = ?
					  , representante_erp = ?
					  , opcao_pagamento_erp = ?
					  , cnpj_intermediador = ?
					  , codigo_pedido_canal = ?
					  , end_entrega_cep = ?
					  , end_entrega_tipo_logradouro = ?
					  , end_entrega_logradouro = ?
					  , end_entrega_numero = ?
					  , end_entrega_complemento = ?
					  , end_entrega_bairro = ?
					  , end_entrega_cidade = ?
					  , end_entrega_estado = ?
					  , end_entrega_referencia_ent = ?
					  , end_entrega_codigo_ibge = ?
					WHERE pedido_id = ? '''


def get_insert_order_items_command(connection_type: str):
    if connection_type.lower() == 'mysql':
        return '''insert into openk_semaforo.itens_pedido (pedido_id, sku, codigo_erp, quantidade, ean, valor, valor_desconto, valor_frete) 
					values (%s, %s, %s, %s, %s, %s, %s, %s) '''
    elif connection_type.lower() == 'oracle':
        return '''INSERT INTO OPENK_SEMAFORO.ITENS_PEDIDO (PEDIDO_ID, SKU, CODIGO_ERP, QUANTIDADE, EAN, VALOR, VALOR_DESCONTO, VALOR_FRETE)
					VALUES (:1, :2, :3, :4, :5, :6, :7, :8)'''
    elif connection_type.lower() == 'sql':
        return '''insert into openk_semaforo.itens_pedido (pedido_id, sku, codigo_erp, quantidade, ean, valor, valor_desconto, valor_frete) 
					values (?, ?, ?, ?, ?, ?, ?, ?) '''


def get_insert_b2c_order_items_command(connection_type: str):
    if connection_type.lower() == 'mysql':
        return '''insert into openk_semaforo.itens_pedido (pedido_id, sku, codigo_erp, quantidade, ean, valor, valor_desconto, valor_frete) 
					values (%s, %s, %s, %s, %s, %s, %s, %s) '''
    elif connection_type.lower() == 'oracle':
        return '''INSERT INTO OPENK_SEMAFORO.ITENS_PEDIDO (PEDIDO_ID, SKU, CODIGO_ERP, QUANTIDADE, EAN, VALOR, VALOR_DESCONTO, VALOR_FRETE)
					VALUES (:1, :2, :3, :4, :5, :6, :7, :8)'''
    elif connection_type.lower() == 'sql':
        return '''insert into openk_semaforo.itens_pedido (pedido_id, sku, codigo_erp, quantidade, ean, valor, valor_desconto, valor_frete) 
					values (?, ?, ?, ?, ?, ?, ?, ?) '''


def get_insert_b2b_order_items_command(connection_type: str):
    if connection_type.lower() == 'mysql':
        return '''insert into openk_semaforo.itens_pedido (pedido_id, sku, codigo_erp, quantidade, ean, valor, valor_desconto, valor_frete, cnpj_filial_venda, codigo_filial_erp, codigo_filial_expedicao_erp, codigo_filial_faturamento_erp) 
					values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) '''
    elif connection_type.lower() == 'oracle':
        return '''INSERT INTO OPENK_SEMAFORO.ITENS_PEDIDO (PEDIDO_ID, SKU, CODIGO_ERP, QUANTIDADE, EAN, VALOR, VALOR_DESCONTO, VALOR_FRETE, CNPJ_FILIAL_VENDA, CODIGO_FILIAL_ERP, CODIGO_FILIAL_EXPEDICAO_ERP, CODIGO_FILIAL_FATURAMENTO_ERP)
					VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12)'''
    elif connection_type.lower() == 'sql':
        return '''insert into openk_semaforo.itens_pedido (pedido_id, sku, codigo_erp, quantidade, ean, valor, valor_desconto, valor_frete, cnpj_filial_venda, codigo_filial_erp, codigo_filial_expedicao_erp, codigo_filial_faturamento_erp) 
					values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) '''


def get_query_client_id(connection_type: str):
    if connection_type.lower() == 'mysql':
        return 'select id from openk_semaforo.cliente where email = %s'
    elif connection_type.lower() == 'oracle':
        return 'SELECT ID FROM OPENK_SEMAFORO.CLIENTE WHERE EMAIL = :email'
    elif connection_type.lower() == 'sql':
        return 'select id from openk_semaforo.cliente where email = ?'


def get_query_client_erp(connection_type: str):
    if connection_type.lower() == 'mysql':
        return 'select id from openk_semaforo.cliente where cliente_erp = %s'
    elif connection_type.lower() == 'oracle':
        return 'SELECT ID FROM OPENK_SEMAFORO.CLIENTE WHERE CLIENTE_ERP = :cliente_erp '
    elif connection_type.lower() == 'sql':
        return 'select id from openk_semaforo.cliente where client_erp = ?'


def get_query_client_cpf(connection_type: str):
    if connection_type.lower() == 'mysql':
        return 'select id from openk_semaforo.cliente where cpf = %s'
    elif connection_type.lower() == 'oracle':
        return 'SELECT ID FROM OPENK_SEMAFORO.CLIENTE WHERE CPF = :cpf '
    elif connection_type.lower() == 'sql':
        return 'select id from openk_semaforo.cliente where cpf = ?'


def get_query_client_cnpj(connection_type: str):
    if connection_type.lower() == 'mysql':
        return 'select id from openk_semaforo.cliente where cnpj = %s'
    elif connection_type.lower() == 'oracle':
        return 'SELECT ID FROM OPENK_SEMAFORO.CLIENTE WHERE CNPJ = :cnpj '
    elif connection_type.lower() == 'sql':
        return 'select id from openk_semaforo.cliente where cnpj = ?'


def get_insert_out_clients(connection_type: str) -> str:
    if connection_type.lower() == 'mysql':
        return '''insert into openk_semaforo.cliente (cliente_erp, data_alteracao, data_sincronizacao)
					values (%s, %s, %s) '''
    elif connection_type.lower() == 'oracle':
        return '''INSERT INTO OPENK_SEMAFORO.CLIENTE (CLIENTE_ERP, DATA_ALTERACAO, DATA_SINCRONIZACAO)
					VALUES (:1, :2, :3)'''
    elif connection_type.lower() == 'sql':
        return '''insert into openk_semaforo.cliente (cliente_erp, data_alteracao, data_sincronizacao)
					values (?, ?, ?) '''


def get_update_client_sql(connection_type: str):
    if connection_type.lower() == 'mysql':
        return '''update openk_semaforo.cliente
					SET nome = %s
					  , razao_social = %s
					  , cpf = %s
					  , cnpj = %s
					  , email = %s
					  , telefone_residencial = %s
					  , telefone_celular = %s
					  , cep = %s
					  , tipo_logradouro = %s
					  , logradouro = %s
					  , numero = %s
					  , complemento = %s
					  , bairro = %s
					  , cidade = %s
					  , estado = %s
					  , referencia = %s
					  , codigo_ibge = %s
					WHERE cliente_erp = %s '''
    elif connection_type.lower() == 'oracle':
        return '''UPDATE OPENK_SEMAFORO.CLIENTE
					SET NOME = :1
					  , RAZAO_SOCIAL = :2
					  , CPF = :3
					  , CNPJ = :4
					  , EMAIL = :5
					  , TELEFONE_RESIDENCIAL = :6
					  , TELEFONE_CELULAR = :7
					  , CEP = :8
					  , TIPO_LOGRADOURO = :9
					  , LOGRADOURO = :10
					  , NUMERO = :11
					  , COMPLEMENTO = :12
					  , BAIRRO = :13
					  , CIDADE = :14
					  , ESTADO = :15
					  , REFERENCIA = :16
					  , CODIGO_IBGE = :17
					WHERE CLIENTE_ERP = :18 '''
    elif connection_type.lower() == 'sql':
        return '''update openk_semaforo.cliente
							SET nome = ?
							  , razao_social = ?
							  , cpf = ?
							  , cnpj = ?
							  , email = ?
							  , telefone_residencial = ?
							  , telefone_celular = ?
							  , cep = ?
							  , tipo_logradouro = ?
							  , logradouro = ?
							  , numero = ?
							  , complemento = ?
							  , bairro = ?
							  , cidade = ?
							  , estado = ?
							  , referencia = ?
							  , codigo_ibge = ?
							WHERE cliente_erp = ? '''

    def get_update_client_sql(connection_type: str):
        if connection_type.lower() == 'mysql':
            return '''update openk_semaforo.cliente
						SET nome = %s
						  , razao_social = %s
						  , cpf = %s
						  , cnpj = %s
						  , email = %s
						  , telefone_residencial = %s
						  , telefone_celular = %s
						  , cep = %s
						  , tipo_logradouro = %s
						  , logradouro = %s
						  , numero = %s
						  , complemento = %s
						  , bairro = %s
						  , cidade = %s
						  , estado = %s
						  , referencia = %s
						  , codigo_ibge = %s
						WHERE cliente_erp = %s '''
        elif connection_type.lower() == 'oracle':
            return '''UPDATE OPENK_SEMAFORO.CLIENTE
						SET NOME = :1
						  , RAZAO_SOCIAL = :2
						  , CPF = :3
						  , CNPJ = :4
						  , EMAIL = :5
						  , TELEFONE_RESIDENCIAL = :6
						  , TELEFONE_CELULAR = :7
						  , CEP = :8
						  , TIPO_LOGRADOURO = :9
						  , LOGRADOURO = :10
						  , NUMERO = :11
						  , COMPLEMENTO = :12
						  , BAIRRO = :13
						  , CIDADE = :14
						  , ESTADO = :15
						  , REFERENCIA = :16
						  , CODIGO_IBGE = :17
						WHERE CLIENTE_ERP = :18 '''
        elif connection_type.lower() == 'sql':
            return '''update openk_semaforo.cliente
								SET nome = ?
								  , razao_social = ?
								  , cpf = ?
								  , cnpj = ?
								  , email = ?
								  , telefone_residencial = ?
								  , telefone_celular = ?
								  , cep = ?
								  , tipo_logradouro = ?
								  , logradouro = ?
								  , numero = ?
								  , complemento = ?
								  , bairro = ?
								  , cidade = ?
								  , estado = ?
								  , referencia = ?
								  , codigo_ibge = ?
								WHERE cliente_erp = ? '''


def get_update_client_cpf_sql(connection_type: str):
    if connection_type.lower() == 'mysql':
        return '''update openk_semaforo.cliente
					SET nome = %s
					  , razao_social = %s
					  , cpf = %s
					  , cnpj = %s
					  , email = %s
					  , telefone_residencial = %s
					  , telefone_celular = %s
					  , cep = %s
					  , tipo_logradouro = %s
					  , logradouro = %s
					  , numero = %s
					  , complemento = %s
					  , bairro = %s
					  , cidade = %s
					  , estado = %s
					  , referencia = %s
					  , codigo_ibge = %s
					WHERE cpf = %s '''
    elif connection_type.lower() == 'oracle':
        return '''UPDATE OPENK_SEMAFORO.CLIENTE
					SET NOME = :1
					  , RAZAO_SOCIAL = :2
					  , CPF = :3
					  , CNPJ = :4
					  , EMAIL = :5
					  , TELEFONE_RESIDENCIAL = :6
					  , TELEFONE_CELULAR = :7
					  , CEP = :8
					  , TIPO_LOGRADOURO = :9
					  , LOGRADOURO = :10
					  , NUMERO = :11
					  , COMPLEMENTO = :12
					  , BAIRRO = :13
					  , CIDADE = :14
					  , ESTADO = :15
					  , REFERENCIA = :16
					  , CODIGO_IBGE = :17
					WHERE CPF = :18 '''
    elif connection_type.lower() == 'sql':
        return '''update openk_semaforo.cliente
							SET nome = ?
							  , razao_social = ?
							  , cpf = ?
							  , cnpj = ?
							  , email = ?
							  , telefone_residencial = ?
							  , telefone_celular = ?
							  , cep = ?
							  , tipo_logradouro = ?
							  , logradouro = ?
							  , numero = ?
							  , complemento = ?
							  , bairro = ?
							  , cidade = ?
							  , estado = ?
							  , referencia = ?
							  , codigo_ibge = ?
							WHERE cpf = ? '''


def get_update_client_cnpj_sql(connection_type: str):
    if connection_type.lower() == 'mysql':
        return '''update openk_semaforo.cliente
					SET nome = %s
					  , razao_social = %s
					  , cpf = %s
					  , cnpj = %s
					  , email = %s
					  , telefone_residencial = %s
					  , telefone_celular = %s
					  , cep = %s
					  , tipo_logradouro = %s
					  , logradouro = %s
					  , numero = %s
					  , complemento = %s
					  , bairro = %s
					  , cidade = %s
					  , estado = %s
					  , referencia = %s
					  , codigo_ibge = %s
					WHERE cnpj = %s '''
    elif connection_type.lower() == 'oracle':
        return '''UPDATE OPENK_SEMAFORO.CLIENTE
					SET NOME = :1
					  , RAZAO_SOCIAL = :2
					  , CPF = :3
					  , CNPJ = :4
					  , EMAIL = :5
					  , TELEFONE_RESIDENCIAL = :6
					  , TELEFONE_CELULAR = :7
					  , CEP = :8
					  , TIPO_LOGRADOURO = :9
					  , LOGRADOURO = :10
					  , NUMERO = :11
					  , COMPLEMENTO = :12
					  , BAIRRO = :13
					  , CIDADE = :14
					  , ESTADO = :15
					  , REFERENCIA = :16
					  , CODIGO_IBGE = :17
					WHERE CNPJ = :18 '''
    elif connection_type.lower() == 'sql':
        return '''update openk_semaforo.cliente
							SET nome = ?
							  , razao_social = ?
							  , cpf = ?
							  , cnpj = ?
							  , email = ?
							  , telefone_residencial = ?
							  , telefone_celular = ?
							  , cep = ?
							  , tipo_logradouro = ?
							  , logradouro = ?
							  , numero = ?
							  , complemento = ?
							  , bairro = ?
							  , cidade = ?
							  , estado = ?
							  , referencia = ?
							  , codigo_ibge = ?
							WHERE cnpj = ? '''


def get_update_b2b_client_sql(connection_type: str):
    if connection_type.lower() == 'mysql':
        return '''update openk_semaforo.cliente
					SET nome = %s
					  , razao_social = %s
					  , cpf = %s
					  , cnpj = %s
					  , email = %s
					  , telefone_residencial = %s
					  , telefone_celular = %s
					  , cep = %s
					  , tipo_logradouro = %s
					  , logradouro = %s
					  , numero = %s
					  , complemento = %s
					  , bairro = %s
					  , cidade = %s
					  , estado = %s
					  , referencia = %s
					  , codigo_ibge = %s
					  , inscricao_estadual = %s
					WHERE cliente_erp = %s '''
    elif connection_type.lower() == 'oracle':
        return '''UPDATE OPENK_SEMAFORO.CLIENTE
					SET NOME = :1
					  , RAZAO_SOCIAL = :2
					  , CPF = :3
					  , CNPJ = :4
					  , EMAIL = :5
					  , TELEFONE_RESIDENCIAL = :6
					  , TELEFONE_CELULAR = :7
					  , CEP = :8
					  , TIPO_LOGRADOURO = :9
					  , LOGRADOURO = :10
					  , NUMERO = :11
					  , COMPLEMENTO = :12
					  , BAIRRO = :13
					  , CIDADE = :14
					  , ESTADO = :15
					  , REFERENCIA = :16
					  , CODIGO_IBGE = :17
					  , INSCRICAO_ESTADUAL = :18
					WHERE CLIENTE_ERP = :19 '''
    elif connection_type.lower() == 'sql':
        return '''update openk_semaforo.cliente
							SET nome = ?
							  , razao_social = ?
							  , cpf = ?
							  , cnpj = ?
							  , email = ?
							  , telefone_residencial = ?
							  , telefone_celular = ?
							  , cep = ?
							  , tipo_logradouro = ?
							  , logradouro = ?
							  , numero = ?
							  , complemento = ?
							  , bairro = ?
							  , cidade = ?
							  , estado = ?
							  , referencia = ?
							  , codigo_ibge = ?
							  , inscricao_estadual = ?
							WHERE cliente_erp = ? '''


def get_update_b2b_client_cpf_sql(connection_type: str):
    if connection_type.lower() == 'mysql':
        return '''update openk_semaforo.cliente
					SET nome = %s
					  , razao_social = %s
					  , cpf = %s
					  , cnpj = %s
					  , email = %s
					  , telefone_residencial = %s
					  , telefone_celular = %s
					  , cep = %s
					  , tipo_logradouro = %s
					  , logradouro = %s
					  , numero = %s
					  , complemento = %s
					  , bairro = %s
					  , cidade = %s
					  , estado = %s
					  , referencia = %s
					  , codigo_ibge = %s
					  , inscricao_estadual = %s
					WHERE cpf = %s '''
    elif connection_type.lower() == 'oracle':
        return '''UPDATE OPENK_SEMAFORO.CLIENTE
					SET NOME = :1
					  , RAZAO_SOCIAL = :2
					  , CPF = :3
					  , CNPJ = :4
					  , EMAIL = :5
					  , TELEFONE_RESIDENCIAL = :6
					  , TELEFONE_CELULAR = :7
					  , CEP = :8
					  , TIPO_LOGRADOURO = :9
					  , LOGRADOURO = :10
					  , NUMERO = :11
					  , COMPLEMENTO = :12
					  , BAIRRO = :13
					  , CIDADE = :14
					  , ESTADO = :15
					  , REFERENCIA = :16
					  , CODIGO_IBGE = :17
					  , INSCRICAO_ESTADUAL = :18
					WHERE CPF = :19 '''
    elif connection_type.lower() == 'sql':
        return '''update openk_semaforo.cliente
							SET nome = ?
							  , razao_social = ?
							  , cpf = ?
							  , cnpj = ?
							  , email = ?
							  , telefone_residencial = ?
							  , telefone_celular = ?
							  , cep = ?
							  , tipo_logradouro = ?
							  , logradouro = ?
							  , numero = ?
							  , complemento = ?
							  , bairro = ?
							  , cidade = ?
							  , estado = ?
							  , referencia = ?
							  , codigo_ibge = ?
							  , inscricao_estadual = ?
							WHERE cpf = ? '''


def get_update_b2b_client_cnpj_sql(connection_type: str):
    if connection_type.lower() == 'mysql':
        return '''update openk_semaforo.cliente
					SET nome = %s
					  , razao_social = %s
					  , cpf = %s
					  , cnpj = %s
					  , email = %s
					  , telefone_residencial = %s
					  , telefone_celular = %s
					  , cep = %s
					  , tipo_logradouro = %s
					  , logradouro = %s
					  , numero = %s
					  , complemento = %s
					  , bairro = %s
					  , cidade = %s
					  , estado = %s
					  , referencia = %s
					  , codigo_ibge = %s
					  , inscricao_estadual = %s
					WHERE cnpj = %s '''
    elif connection_type.lower() == 'oracle':
        return '''UPDATE OPENK_SEMAFORO.CLIENTE
					SET NOME = :1
					  , RAZAO_SOCIAL = :2
					  , CPF = :3
					  , CNPJ = :4
					  , EMAIL = :5
					  , TELEFONE_RESIDENCIAL = :6
					  , TELEFONE_CELULAR = :7
					  , CEP = :8
					  , TIPO_LOGRADOURO = :9
					  , LOGRADOURO = :10
					  , NUMERO = :11
					  , COMPLEMENTO = :12
					  , BAIRRO = :13
					  , CIDADE = :14
					  , ESTADO = :15
					  , REFERENCIA = :16
					  , CODIGO_IBGE = :17
					  , INSCRICAO_ESTADUAL = :18
					WHERE CNPJ = :19 '''
    elif connection_type.lower() == 'sql':
        return '''update openk_semaforo.cliente
							SET nome = ?
							  , razao_social = ?
							  , cpf = ?
							  , cnpj = ?
							  , email = ?
							  , telefone_residencial = ?
							  , telefone_celular = ?
							  , cep = ?
							  , tipo_logradouro = ?
							  , logradouro = ?
							  , numero = ?
							  , complemento = ?
							  , bairro = ?
							  , cidade = ?
							  , estado = ?
							  , referencia = ?
							  , codigo_ibge = ?
							  , inscricao_estadual = ?
							WHERE cnpj = ? '''


def get_update_b2c_client_sql(connection_type: str):
    if connection_type.lower() == 'mysql':
        return '''update openk_semaforo.cliente
					SET nome = %s
					  , razao_social = %s
					  , cpf = %s
					  , cnpj = %s
					  , email = %s
					  , telefone_residencial = %s
					  , telefone_celular = %s
					  , cep = %s
					  , tipo_logradouro = %s
					  , logradouro = %s
					  , numero = %s
					  , complemento = %s
					  , bairro = %s
					  , cidade = %s
					  , estado = %s
					  , referencia = %s
					WHERE cliente_erp = %s '''
    elif connection_type.lower() == 'oracle':
        return '''UPDATE OPENK_SEMAFORO.CLIENTE
					SET NOME = :1
					  , RAZAO_SOCIAL = :2
					  , CPF = :3
					  , CNPJ = :4
					  , EMAIL = :5
					  , TELEFONE_RESIDENCIAL = :6
					  , TELEFONE_CELULAR = :7
					  , CEP = :8
					  , TIPO_LOGRADOURO = :9
					  , LOGRADOURO = :10
					  , NUMERO = :11
					  , COMPLEMENTO = :12
					  , BAIRRO = :13
					  , CIDADE = :14
					  , ESTADO = :15
					  , REFERENCIA = :16
					WHERE CLIENTE_ERP = :17 '''
    elif connection_type.lower() == 'sql':
        return '''update openk_semaforo.cliente
							SET nome = ?
							  , razao_social = ?
							  , cpf = ?
							  , cnpj = ?
							  , email = ?
							  , telefone_residencial = ?
							  , telefone_celular = ?
							  , cep = ?
							  , tipo_logradouro = ?
							  , logradouro = ?
							  , numero = ?
							  , complemento = ?
							  , bairro = ?
							  , cidade = ?
							  , estado = ?
							  , referencia = ?
							WHERE cliente_erp = ? '''


def get_update_b2c_client_cpf_sql(connection_type: str):
    if connection_type.lower() == 'mysql':
        return '''update openk_semaforo.cliente
					SET nome = %s
					  , razao_social = %s
					  , cpf = %s
					  , cnpj = %s
					  , email = %s
					  , telefone_residencial = %s
					  , telefone_celular = %s
					  , cep = %s
					  , tipo_logradouro = %s
					  , logradouro = %s
					  , numero = %s
					  , complemento = %s
					  , bairro = %s
					  , cidade = %s
					  , estado = %s
					  , referencia = %s
					WHERE cpf = %s '''
    elif connection_type.lower() == 'oracle':
        return '''UPDATE OPENK_SEMAFORO.CLIENTE
					SET NOME = :1
					  , RAZAO_SOCIAL = :2
					  , CPF = :3
					  , CNPJ = :4
					  , EMAIL = :5
					  , TELEFONE_RESIDENCIAL = :6
					  , TELEFONE_CELULAR = :7
					  , CEP = :8
					  , TIPO_LOGRADOURO = :9
					  , LOGRADOURO = :10
					  , NUMERO = :11
					  , COMPLEMENTO = :12
					  , BAIRRO = :13
					  , CIDADE = :14
					  , ESTADO = :15
					  , REFERENCIA = :16
					WHERE CPF = :17 '''
    elif connection_type.lower() == 'sql':
        return '''update openk_semaforo.cliente
							SET nome = ?
							  , razao_social = ?
							  , cpf = ?
							  , cnpj = ?
							  , email = ?
							  , telefone_residencial = ?
							  , telefone_celular = ?
							  , cep = ?
							  , tipo_logradouro = ?
							  , logradouro = ?
							  , numero = ?
							  , complemento = ?
							  , bairro = ?
							  , cidade = ?
							  , estado = ?
							  , referencia = ?
							WHERE cpf = ? '''


def get_update_b2c_client_cnpj_sql(connection_type: str):
    if connection_type.lower() == 'mysql':
        return '''update openk_semaforo.cliente
					SET nome = %s
					  , razao_social = %s
					  , cpf = %s
					  , cnpj = %s
					  , email = %s
					  , telefone_residencial = %s
					  , telefone_celular = %s
					  , cep = %s
					  , tipo_logradouro = %s
					  , logradouro = %s
					  , numero = %s
					  , complemento = %s
					  , bairro = %s
					  , cidade = %s
					  , estado = %s
					  , referencia = %s
					WHERE cnpj = %s '''
    elif connection_type.lower() == 'oracle':
        return '''UPDATE OPENK_SEMAFORO.CLIENTE
					SET NOME = :1
					  , RAZAO_SOCIAL = :2
					  , CPF = :3
					  , CNPJ = :4
					  , EMAIL = :5
					  , TELEFONE_RESIDENCIAL = :6
					  , TELEFONE_CELULAR = :7
					  , CEP = :8
					  , TIPO_LOGRADOURO = :9
					  , LOGRADOURO = :10
					  , NUMERO = :11
					  , COMPLEMENTO = :12
					  , BAIRRO = :13
					  , CIDADE = :14
					  , ESTADO = :15
					  , REFERENCIA = :16
					WHERE CNPJ = :17 '''
    elif connection_type.lower() == 'sql':
        return '''update openk_semaforo.cliente
							SET nome = ?
							  , razao_social = ?
							  , cpf = ?
							  , cnpj = ?
							  , email = ?
							  , telefone_residencial = ?
							  , telefone_celular = ?
							  , cep = ?
							  , tipo_logradouro = ?
							  , logradouro = ?
							  , numero = ?
							  , complemento = ?
							  , bairro = ?
							  , cidade = ?
							  , estado = ?
							  , referencia = ?
							WHERE cnpj = ? '''


def get_query_non_integrated_order(connection_type: str):
    if connection_type.lower() == 'mysql':
        return 'select id from openk_semaforo.pedido where pedido_id = %s and data_sincronizacao is null'
    elif connection_type.lower() == 'oracle':
        return 'SELECT ID FROM OPENK_SEMAFORO.PEDIDO WHERE PEDIDO_ID = :order_id AND DATA_SINCRONIZACAO IS NULL'
    elif connection_type.lower() == 'sql':
        return 'select id from openk_semaforo.pedido where pedido_id = ? and data_sincronizacao is null'


def get_query_order(connection_type: str):
    if connection_type.lower() == 'mysql':
        return 'select id from openk_semaforo.pedido where pedido_id = %s'
    elif connection_type.lower() == 'oracle':
        return 'SELECT ID FROM OPENK_SEMAFORO.PEDIDO WHERE PEDIDO_ID = :order_id'
    elif connection_type.lower() == 'sql':
        return 'select id from openk_semaforo.pedido where pedido_id = ?'


def get_query_order_status(connection_type: str):
    if connection_type.lower() == 'mysql':
        return 'select status from openk_semaforo.pedido where pedido_id = %s'
    elif connection_type.lower() == 'oracle':
        return 'SELECT STATUS FROM OPENK_SEMAFORO.PEDIDO WHERE PEDIDO_ID = :order_id'
    elif connection_type.lower() == 'sql':
        return 'select status from openk_semaforo.pedido where pedido_id = ?'


def get_query_order_sync_date(connection_type: str):
    if connection_type.lower() == 'mysql':
        return 'select if(data_sincronizacao is not null, true, false) from openk_semaforo.pedido where pedido_id = %s'
    elif connection_type.lower() == 'oracle':
        return 'SELECT CASE WHEN DATA_SINCRONIZACAO IS NULL THEN 0 ELSE 1 END FROM OPENK_SEMAFORO.PEDIDO WHERE PEDIDO_ID = :order_id'
    elif connection_type.lower() == 'sql':
        return 'select if(data_sincronizacao is not null, true, false) from openk_semaforo.pedido where pedido_id = ?'


def get_command_parameter(connection_type: str, parameters: list):
    if connection_type.lower() == 'mysql':
        return tuple(parameters)
    elif connection_type.lower() == 'oracle':
        return parameters
    elif connection_type.lower() == 'sql':
        return parameters


def get_order_protocol_command(connection_type: str):
    if connection_type.lower() == 'mysql':
        return 'update openk_semaforo.pedido set data_sincronizacao = now(), codigo_referencia = %s where pedido_id = %s'
    elif connection_type.lower() == 'oracle':
        return 'UPDATE OPENK_SEMAFORO.PEDIDO SET DATA_SINCRONIZACAO = SYSDATE, CODIGO_REFERENCIA = :order_erp_id WHERE PEDIDO_ID = :order_id'
    elif connection_type.lower() == 'sql':
        return 'update openk_semaforo.pedido set data_sincronizacao = getdate(), codigo_referencia = ? where pedido_id = ?'


def get_order_protocol_nf_command(connection_type: str):
    if connection_type.lower() == 'mysql':
        return 'update openk_semaforo.pedido set data_sincronizacao_nf = now() where pedido_id = %s'
    elif connection_type.lower() == 'oracle':
        return 'UPDATE OPENK_SEMAFORO.PEDIDO SET DATA_SINCRONIZACAO_NF = SYSDATE WHERE PEDIDO_ID = :order_id'
    elif connection_type.lower() == 'sql':
        return 'update openk_semaforo.pedido set data_sincronizacao_nf = getdate() where pedido_id = ?'


def get_client_protocol_command(connection_type: str):
    if connection_type.lower() == 'mysql':
        return 'update openk_semaforo.cliente set cliente_erp = %s where id = (select cliente_id from openk_semaforo.pedido where pedido_id = %s)'
    elif connection_type.lower() == 'oracle':
        return '''UPDATE OPENK_SEMAFORO.CLIENTE C
				SET CLIENTE_ERP = :1 
				WHERE ID = (SELECT CLIENTE_ID FROM OPENK_SEMAFORO.PEDIDO WHERE PEDIDO_ID = :2)'''
    elif connection_type.lower() == 'sql':
        return 'update openk_semaforo.cliente set cliente_erp = ? where id = (select cliente_id from openk_semaforo.pedido where pedido_id = ?)'


def get_out_client_protocol_command(connection_type: str):
    if connection_type.lower() == 'mysql':
        return 'update openk_semaforo.cliente set data_sincronizacao = now() where cliente_erp = %s'
    elif connection_type.lower() == 'oracle':
        return 'UPDATE OPENK_SEMAFORO.CLIENTE C SET DATA_SINCRONIZACAO = SYSDATE WHERE CLIENTE_ERP = :1 '
    elif connection_type.lower() == 'sql':
        return 'update openk_semaforo.cliente set data_sincronizacao = getdate() where cliente_erp = ? '


def get_insert_update_semaphore_command(connection_type: str):
    if connection_type.lower() == 'mysql':
        return 'insert into openk_semaforo.semaforo(identificador, identificador2, tipo_id, data_alteracao, data_sincronizacao) values (%s, %s, %s, now(), null) on duplicate key update data_alteracao = now()'
    elif connection_type.lower() == 'oracle':
        return '''
		MERGE INTO OPENK_SEMAFORO.SEMAFORO sem
		USING (
			SELECT
				:1 AS identificador,
				:2 AS identificador2,
				:3 AS tipo_id
			FROM DUAL
		) tmp ON (tmp.identificador = sem.identificador AND tmp.identificador2 = sem.identificador2 AND tmp.tipo_id = sem.tipo_id)
		
		WHEN MATCHED THEN
			UPDATE SET sem.DATA_ALTERACAO = SYSDATE
		
		WHEN NOT MATCHED THEN  
		INSERT (IDENTIFICADOR, IDENTIFICADOR2, TIPO_ID, DATA_ALTERACAO, DATA_SINCRONIZACAO)
		VALUES (tmp.identificador, tmp.identificador2, tmp.tipo_id, sysdate, null)
		'''
    elif connection_type.lower() == 'sql':
        return '''
		MERGE INTO OPENK_SEMAFORO.SEMAFORO sem
		USING (
			SELECT
				? AS identificador,
				? AS identificador2,
				? AS tipo_id
		) tmp ON (tmp.identificador = sem.identificador AND tmp.identificador2 = sem.identificador2 AND tmp.tipo_id = sem.tipo_id)
		
		WHEN MATCHED THEN
			UPDATE SET sem.DATA_ALTERACAO = getdate()
		
		WHEN NOT MATCHED THEN
		INSERT (IDENTIFICADOR, IDENTIFICADOR2, TIPO_ID, DATA_ALTERACAO, DATA_SINCRONIZACAO)
		VALUES (tmp.identificador, tmp.identificador2, tmp.tipo_id, getdate(), null)
		'''


def get_protocol_semaphore_id_command(connection_type: str):
    if connection_type.lower() == 'mysql':
        return 'update openk_semaforo.semaforo set data_sincronizacao = now() where identificador = %s'
    elif connection_type.lower() == 'oracle':
        return 'update openk_semaforo.semaforo set data_sincronizacao = sysdate where identificador = :1'
    elif connection_type.lower() == 'sql':
        return 'update openk_semaforo.semaforo set data_sincronizacao = getdate() where identificador = ?'

def get_protocol_semaphore_id2_command(connection_type: str):
    if connection_type.lower() == 'mysql':
        return 'update openk_semaforo.semaforo set data_sincronizacao = now() where identificador = %s and identificador2 = %s'
    elif connection_type.lower() == 'oracle':
        return 'update openk_semaforo.semaforo set data_sincronizacao = sysdate where identificador = :1 and identificador2 = :2'
    elif connection_type.lower() == 'sql':
        return 'update openk_semaforo.semaforo set data_sincronizacao = getdate() where identificador = ? and identificador2 = ?'

def get_protocol_semaphore_id3_command(connection_type: str):
    if connection_type.lower() == 'mysql':
        return 'update openk_semaforo.semaforo set data_sincronizacao = now() where identificador = %s and tipo_id = %s'
    elif connection_type.lower() == 'oracle':
        return 'update openk_semaforo.semaforo set data_sincronizacao = sysdate where identificador = :1 and tipo_id = :2'
    elif connection_type.lower() == 'sql':
        return 'update openk_semaforo.semaforo set data_sincronizacao = getdate() where identificador = ? and tipo_id = ?'

def get_insert_in_clients(connection_type: str):
    if connection_type.lower() == 'mysql':
        return '''
			insert into cliente (nome, razao_social, cpf, cnpj, email, telefone_residencial, telefone_celular, cep, tipo_logradouro, logradouro, numero, complemento, bairro, cidade, estado, referencia,
								cliente_erp, direcao, data_sincronizacao, data_alteracao, codigo_ibge, inscricaoestadual)
		    value (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, null, %s, %s, null, %s, %s)
		    on duplicate key update
		    	data_alteracao = values(data_alteracao),
		    	data_sincronizacao = null
		'''
    elif connection_type.lower() == 'oracle':
        return '''
			MERGE INTO OPENK_SEMAFORO.CLIENTE c
			USING (
				SELECT
					:1 AS CPF,
					:2 AS CNPJ,
					:3 AS DATA_ALTERACAO
				FROM DUAL
			) tmp ON (tmp.CPF = c.CPF OR tmp.CNPJ = c.CNPJ)
			
			WHEN MATCHED THEN
				UPDATE SET
					c.DATA_ALTERACAO = tmp.DATA_ALTERACAO,
					c.DATA_SINCRONIZACAO = NULL
			
			WHEN NOT MATCHED THEN
			INSERT (NOME, RAZAO_SOCIAL, CPF, CNPJ, EMAIL, TELEFONE_RESIDENCIAL, TELEFONE_CELULAR, CEP, TIPO_LOGRADOURO, LOGRADOURO, NUMERO, COMPLEMENTO, BAIRRO, CIDADE, ESTADO,
					REFERENCIA, CLIENTE_ERP, DIRECAO, DATA_ALTERACAO, DATA_SINCRONIZACAO, CODIGO_IBGE, INSCRICAO_ESTADUAL)
			VALUES (:4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17, :18, :19, NULL, :20, :21, NULL, :22, :23)
		'''
    elif connection_type.lower() == 'sql':
        return '''
			MERGE INTO OPENK_SEMAFORO.CLIENTE c
			USING (
				SELECT
					? AS NOME,
					? AS RAZAO_SOCIAL,
					? AS CPF,
					? AS CNPJ,
					? AS EMAIL,
					? AS TELEFONE_RESIDENCIAL,
					? AS TELEFONE_CELULAR,
					? AS CEP,
					? AS TIPO_LOGRADOURO,
					? AS LOGRADOURO,
					? AS NUMERO,
					? AS COMPLEMENTO,
					? AS BAIRRO,
					? AS CIDADE,
					? AS ESTADO,
					? AS REFERENCIA,
					? AS DIRECAO,
					? AS DATA_ALTERACAO,
					? AS CODIGO_IBGE,
					? AS INSCRICAO_ESTADUAL,
					? AS CLIENTE_ERP
				FROM DUAL
			) tmp ON (tmp.CPF = c.CPF OR tmp.CNPJ = c.CNPJ)
			
			WHEN MATCHED THEN
				UPDATE SET
					c.DATA_ALTERACAO = tmp.DATA_ALTERACAO,
					c.DATA_SINCRONIZACAO = NULL
			
			WHEN NOT MATCHED THEN
			INSERT (NOME, RAZAO_SOCIAL, CPF, CNPJ, EMAIL, TELEFONE_RESIDENCIAL, TELEFONE_CELULAR, CEP, TIPO_LOGRADOURO, LOGRADOURO, NUMERO, COMPLEMENTO, BAIRRO, CIDADE, ESTADO,
					REFERENCIA, CLIENTE_ERP, DIRECAO, DATA_ALTERACAO, DATA_SINCRONIZACAO, CODIGO_IBGE, INSCRICAO_ESTADUAL)
			VALUES (tmp.NOME, tmp.RAZAO_SOCIAL, tmp.CPF, tmp.CNPJ, tmp.EMAIL, tmp.TELEFONE_RESIDENCIAL, tmp.TELEFONE_CELULAR, tmp.CEP, tmp.TIPO_LOGRADOURO, tmp.LOGRADOURO, tmp.NUMERO, tmp.COMPLEMENTO,
					tmp.BAIRRO, tmp.CIDADE, tmp.ESTADO, tmp.REFERENCIA, NULL, tmp.DIRECAO, tmp.DATA_ALTERACAO, NULL, tmp.CODIGO_IBGE, tmp.INSCRICAO_ESTADUAL)
		'''


def get_update_in_clients(connection_type: str):
    if connection_type.lower() == 'mysql':
        return 'update openk_semaforo.cliente set data_alteracao = %s, data_sincronizacao = null where id = %s'
    elif connection_type.lower() == 'oracle':
        return 'UPDATE OPENK_SEMAFORO.CLIENTE SET DATA_ALTERACAO = :1, DATA_SINCRONIZACAO = NULL WHERE id = :2'
    elif connection_type.lower() == 'sql':
        return 'UPDATE OPENK_SEMAFORO.CLIENTE SET DATA_ALTERACAO = ?, DATA_SINCRONIZACAO = NULL WHERE id = ?'
