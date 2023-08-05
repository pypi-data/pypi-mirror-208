import threading
import time
import src
from time import sleep
import schedule
import logging
from src.jobs import products_jobs, system_jobs, client_jobs
from src.jobs import stock_jobs
from src.jobs import price_jobs
from src.jobs import order_jobs
from src.jobs import representative_jobs
from src.jobs import client_payment_plan_jobs
from src.jobs import client_payment_plan_semaphore_jobs
from src.api import oking
from src.jobs.system_jobs import OnlineLogger

logger = logging.getLogger()
send_log = OnlineLogger.send_log


# region Estoques

def instantiate_insert_stock_semaphore_job(job_config: dict) -> None:
    """
    Instancia o job de inserção/atualização de estoques na tabela de semáforo
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    logger.info(job_config.get('job_name') + ' | Iniciando execucao')
    stock_jobs.job_insert_stock_semaphore(job_config)


def run_thread_instantiate_insert_stock_semaphore_job(job_config: dict) -> None:
    logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
    time.sleep(1)
    job_thread = threading.Thread(target=stock_jobs.job_insert_stock_semaphore, args=[job_config])
    job_thread.start()


def instantiate_send_stock_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos estoques para a api okVendas
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    logger.info(job_config.get('job_name') + ' | Iniciando execucao')
    stock_jobs.job_send_stocks(job_config)


def run_thread_instantiate_send_stock_job(job_config: dict) -> None:
    logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
    time.sleep(1)
    job_thread = threading.Thread(target=stock_jobs.job_send_stocks, args=[job_config])
    job_thread.start()


def instantiate_send_ud_stock_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos estoques por Unidades de distribuição para a api okVendas
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    logger.info(job_config.get('job_name') + ' | Iniciando execucao')
    stock_jobs.job_send_stocks_ud(job_config)


def run_thread_instantiate_send_ud_stock_job(job_config: dict) -> None:
    logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
    time.sleep(1)
    job_thread = threading.Thread(target=stock_jobs.job_send_stocks_ud, args=[job_config])
    job_thread.start()


# endregion Estoques


# region Precos

def instantiate_insert_price_semaphore_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos preços para o banco semáforo

    Args:
        job_config: Configuração do job obtida na api do oking
    """
    logger.info(job_config.get('job_name') + ' | Iniciando execucao')
    price_jobs.job_insert_prices_semaphore(job_config)


def run_thread_instantiate_insert_price_semaphore_job(job_config: dict) -> None:
    logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
    time.sleep(1)
    job_thread = threading.Thread(target=price_jobs.job_insert_prices_semaphore, args=[job_config])
    job_thread.start()


def instantiate_send_price_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos preços para a api okVendas

    Args:
        job_config: Configuração do job obtida na api do oking
    """
    logger.info(job_config.get('job_name') + ' | Iniciando execucao')
    price_jobs.job_send_prices(job_config)


def run_thread_instantiate_send_price_job(job_config: dict) -> None:
    logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
    time.sleep(1)
    job_thread = threading.Thread(target=price_jobs.job_send_prices, args=[job_config])
    job_thread.start()


def instantiate_prices_list_job(job_config: dict) -> None:
    """
    Instancia o job de envio das listas de preço para o banco semáforo

    Args:
        job_config: Configuração do job obtida na api do oking
    """
    logger.info(job_config.get('job_name') + ' | Iniciando execucao')
    price_jobs.job_prices_list(job_config)


def run_thread_instantiate_prices_list_job(job_config: dict) -> None:
    logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
    time.sleep(1)
    job_thread = threading.Thread(target=price_jobs.job_prices_list, args=[job_config])
    job_thread.start()


def instantiate_product_prices_list_job(job_config: dict) -> None:
    """
    Instancia o job dos produtos das listas de preço

    Args:
        job_config: Configuração do job obtida na api do oking
    """
    logger.info(job_config.get('job_name') + ' | Iniciando execucao')
    price_jobs.job_products_prices_list(job_config)


def run_thread_instantiate_product_prices_list_job(job_config: dict) -> None:
    logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
    time.sleep(1)
    job_thread = threading.Thread(target=price_jobs.job_products_prices_list, args=[job_config])
    job_thread.start()


# endregion Precos


# region imposto
def instantiate_product_tax_job(job_config: dict) -> None:
    """
    Instancia o job dos impostos dos produtos
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    logger.info(job_config.get('job_name') + ' | Iniciando execucao')
    products_jobs.job_product_tax(job_config)


def run_thread_instantiate_product_tax_job(job_config: dict) -> None:
    logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
    time.sleep(1)
    job_thread = threading.Thread(target=products_jobs.job_product_tax, args=[job_config])
    job_thread.start()


def instantiate_product_tax_full_job(job_config: dict) -> None:
    """
    Instancia o job dos impostos em lote dos produtos
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    logger.info(job_config.get('job_name') + ' | Iniciando execucao')
    products_jobs.job_product_tax_full(job_config)


def run_thread_instantiate_product_tax_full_job(job_config: dict) -> None:
    logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
    time.sleep(1)
    job_thread = threading.Thread(target=products_jobs.job_product_tax_full, args=[job_config])
    job_thread.start()


# endregion imposto

# region plano_pagamento_cliente
def instantiate_client_payment_plan_job(job_config: dict) -> None:
    """
    Instancia o job dos planos de pagamentos dos clientes
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    logger.info(job_config.get('job_name') + ' | Iniciando execucao')
    client_payment_plan_jobs.job_client_payment_plan(job_config)


def run_thread_instantiate_client_payment_plan_job(job_config: dict) -> None:
    logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
    time.sleep(1)
    job_thread = threading.Thread(target=client_payment_plan_jobs.job_client_payment_plan, args=[job_config])
    job_thread.start()


def instantiate_insert_client_no_exists_payment_plan_semaphore_job(job_config: dict) -> None:
    """
    Instancia o job dos planos de pagamentos dos clientes
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    logger.info(job_config.get('job_name') + ' | Iniciando execucao')
    client_payment_plan_semaphore_jobs.job_insert_client_no_exists_payment_plan_semaphore(job_config)


def run_thread_instantiate_insert_client_no_exists_payment_plan_semaphore_job(job_config: dict) -> None:
    logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
    time.sleep(1)
    job_thread = threading.Thread(target=client_payment_plan_semaphore_jobs.job_insert_client_no_exists_payment_plan_semaphore, args=[job_config])
    job_thread.start()


# endregion plano_pagamento

# region representante
def instantiate_representative_job(job_config: dict) -> None:
    """
    Instancia o job dos representantes
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    logger.info(job_config.get('job_name') + ' | Iniciando execucao')
    representative_jobs.job_representative(job_config)


def run_thread_instantiate_representative_job(job_config: dict) -> None:
    logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
    time.sleep(1)
    job_thread = threading.Thread(target=representative_jobs.job_representative, args=[job_config])
    job_thread.start()


# endregion representante

# region Produtos
def instantiate_insert_products_semaphore_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos produtos para o banco semáforo
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    logger.info(job_config.get('job_name') + ' | Iniciando execucao')
    products_jobs.job_insert_products_semaphore(job_config)


def run_thread_instantiate_insert_products_semaphore_job(job_config: dict) -> None:
    logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
    time.sleep(1)
    job_thread = threading.Thread(target=products_jobs.job_insert_products_semaphore, args=[job_config])
    job_thread.start()


def instantiate_update_products_semaphore_job(job_config: dict) -> None:
    """
    Instancia o job de atualização dos produtos no banco semáforo
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    logger.info(job_config.get('job_name') + ' | Iniciando execucao')
    products_jobs.job_update_products_semaphore(job_config)


def run_thread_instantiate_update_products_semaphore_job(job_config: dict) -> None:
    logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
    time.sleep(1)
    job_thread = threading.Thread(target=products_jobs.job_update_products_semaphore, args=[job_config])
    job_thread.start()


def instantiate_send_products_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos produtos para a api okVendas
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    logger.info(job_config.get('job_name') + ' | Iniciando execucao')
    products_jobs.job_send_products(job_config)


def run_thread_instantiate_send_products_job(job_config: dict) -> None:
    logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
    time.sleep(1)
    job_thread = threading.Thread(target=products_jobs.job_send_products, args=[job_config])
    job_thread.start()


# endregion Produtos


# region Pedidos

def instantiate_orders_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos pedidos para o ERP, incluindo pedidos ainda não pagos
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    logger.info(job_config.get('job_name') + ' | Iniciando execucao')
    order_jobs.define_job_start(job_config)


def run_thread_instantiate_orders_job(job_config: dict) -> None:
    logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
    time.sleep(1)
    job_thread = threading.Thread(target=order_jobs.define_job_start, args=[job_config])
    job_thread.start()


def instantiate_paid_orders_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos pedidos pagos para o ERP
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    logger.info(job_config.get('job_name') + ' | Iniciando execucao')
    order_jobs.define_job_start(job_config)


def run_thread_instantiate_paid_orders_job(job_config: dict) -> None:
    logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
    time.sleep(1)
    job_thread = threading.Thread(target=order_jobs.define_job_start, args=[job_config])
    job_thread.start()


def instantiate_b2b_orders_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos pedidos B2B para o ERP, incluindo pedidos ainda não pagos
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    logger.info(job_config.get('job_name') + ' | Iniciando execucao')
    order_jobs.define_job_start(job_config)


def run_thread_instantiate_b2b_orders_job(job_config: dict) -> None:
    logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
    time.sleep(1)
    job_thread = threading.Thread(target=order_jobs.define_job_start, args=[job_config])
    job_thread.start()


def instantiate_paid_b2b_orders_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos pedidos pagos B2B para o ERP
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    logger.info(job_config.get('job_name') + ' | Iniciando execucao')
    order_jobs.define_job_start(job_config)


def run_thread_instantiate_paid_b2b_orders_job(job_config: dict) -> None:
    logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
    time.sleep(1)
    job_thread = threading.Thread(target=order_jobs.define_job_start, args=[job_config])
    job_thread.start()


def instantiate_invoice_job(job_config: dict) -> None:
    """
    Intancia o job de envio das NFs de pedidos para a api okvendas
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    logger.info(job_config.get('job_name') + ' | Iniciando execucao')
    order_jobs.job_invoice_orders(job_config)


def run_thread_instantiate_invoice_job(job_config: dict) -> None:
    logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
    time.sleep(1)
    job_thread = threading.Thread(target=order_jobs.job_invoice_orders, args=[job_config])
    job_thread.start()


def instantiate_erp_tracking_job(job_config: dict) -> None:
    """
    Intancia o job de envio do rastreio de pedidos para a api okvendas
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    logger.info(job_config.get('job_name') + ' | Iniciando execucao')
    order_jobs.job_send_erp_tracking(job_config)


def run_thread_instantiate_erp_tracking_job(job_config: dict) -> None:
    logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
    time.sleep(1)
    job_thread = threading.Thread(target=order_jobs.job_send_erp_tracking, args=[job_config])
    job_thread.start()


# endregion Pedidos


# region Clientes

def instantiate_client_b2b_integration_job(job_config: dict) -> None:
    """
    Instancia o job de envio de clientes para a api okvendas
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    logger.info(job_config.get('job_name') + ' | Iniciando execucao')
    client_jobs.job_send_clients(job_config)


def run_thread_instantiate_client_b2b_integration_job(job_config: dict) -> None:
    logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
    time.sleep(1)
    job_thread = threading.Thread(target=client_jobs.job_send_clients, args=[job_config])
    job_thread.start()


def instantiate_client_integration_job(job_config: dict) -> None:
    """
    Instancia o job de envio de clientes para a api okvendas
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    logger.warning(job_config.get('job_name') + ' | Job nao implementado!')


def run_thread_instantiate_client_integration_job(job_config: dict) -> None:
    logger.warning(job_config.get('job_name') + ' | Job nao implementado!')
    # logger.info((f'Adicionando job {job_config.get("job_name")} na thread')
    # job_thread = threading.Thread(target=, args=[job_config])
    # logger.info((f'Iniciando a thread do job {job_config.get("job_name")}')
    # job_thread.start()


def intantiate_send_approved_clients_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos clientes B2B aprovados para o ERP

    Args:
        job_config: Configuração do job obtida na api do oking
    """
    logger.info(job_config.get('job_name') + ' | Iniciando execucao')
    client_jobs.job_send_approved_clients(job_config)


def run_thread_intantiate_send_approved_clients_job(job_config: dict) -> None:
    logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
    time.sleep(1)
    job_thread = threading.Thread(target=client_jobs.job_send_approved_clients, args=[job_config])
    job_thread.start()


# endregion Clientes


def instantiate_periodic_execution_notification(job_config: dict) -> None:
    """
    Instancia o job que realiza a notificacao de execucao da integracao para a api okvendas
    Args:
        job_config: Configuração do job
    """
    logger.info(job_config.get('job_name') + ' | Iniciando execucao')
    system_jobs.send_execution_notification(job_config)


def run_thread_instantiate_periodic_execution_notification(job_config):
    logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
    time.sleep(1)
    job_thread = threading.Thread(target=system_jobs.send_execution_notification, args=[job_config])
    job_thread.start()


# region ConfigJobs


def run_thread(job_name, job_config):
    # Estoque
    if job_name == 'insere_estoque_produto_semaforo_job':
        run_thread_instantiate_insert_stock_semaphore_job(job_config)
    elif job_name == 'envia_estoque_produtos_job':
        run_thread_instantiate_send_stock_job(job_config)
    elif job_name == 'envia_estoque_produtos_ud_job':
        run_thread_instantiate_send_ud_stock_job(job_config)

    # Preco
    elif job_name == 'insere_preco_produto_semaforo_job':
        run_thread_instantiate_insert_price_semaphore_job(job_config)

    elif job_name == 'envia_preco_produtos_job':
        run_thread_instantiate_send_price_job(job_config)

    elif job_name == 'lista_preco_job':
        run_thread_instantiate_prices_list_job(job_config)

    elif job_name == 'produto_lista_preco_job':
        run_thread_instantiate_product_prices_list_job(job_config)

    # Catalogacao
    elif job_name == 'envia_catalogo_produto_semaforo_job':
        run_thread_instantiate_insert_products_semaphore_job(job_config)

    elif job_name == 'envia_catalogo_produto_loja_job':
        run_thread_instantiate_send_products_job(job_config)

    elif job_name == 'imposto_produto_job':
        run_thread_instantiate_product_tax_job(job_config)

    elif job_name == 'imposto_produto_lote_job':
        run_thread_instantiate_product_tax_full_job(job_config)

    # Pedidos
    elif job_name == 'internaliza_pedidos_job':
        run_thread_instantiate_orders_job(job_config)
    elif job_name == 'internaliza_pedidos_pagos_job':
        run_thread_instantiate_paid_orders_job(job_config)
    elif job_name == 'internaliza_pedidos_b2b_job':
        run_thread_instantiate_b2b_orders_job(job_config)
    elif job_name == 'internaliza_pedidos_pagos_b2b_job':
        run_thread_instantiate_paid_b2b_orders_job(job_config)
    elif job_name == 'envia_nota_loja_job':
        run_thread_instantiate_invoice_job(job_config)
    elif job_name == 'envia_rastreio_pedido_job':
        run_thread_instantiate_erp_tracking_job(job_config)

    # Clientes
    elif job_name == 'integra_cliente_b2b_job':
        run_thread_instantiate_client_b2b_integration_job(job_config)
    elif job_name == 'integra_cliente_job':
        run_thread_instantiate_client_integration_job(job_config)
    elif job_name == 'integra_cliente_aprovado_job':
        run_thread_intantiate_send_approved_clients_job(job_config)

    # PlanoPagamentoCliente
    elif job_name == 'envia_plano_pagamento_cliente_job':
        run_thread_instantiate_client_payment_plan_job(job_config)
    elif job_name == 'insere_cliente_plano_pagamento_semaforo_job':
        run_thread_instantiate_insert_client_no_exists_payment_plan_semaphore_job(job_config)

    # Representantes
    elif job_name == 'envia_representante_job':
        run_thread_instantiate_representative_job(job_config)

    # Notificacao
    elif job_name == 'periodic_execution_notification':
        run_thread_instantiate_periodic_execution_notification(job_config)


def schedule_job(job_config: dict, time_unit: str, time: int) -> None:
    logger.info(f'Adicionando job {job_config.get("job_name")} ao schedule de {time} em {time} {time_unit}')
    #func = get_job_from_name(job_config.get('job_name'))
    job_name = job_config.get('job_name')

    if time_unit == 'M':  # Minutos
        schedule.every(time).minutes.do(run_thread, job_name, job_config)
        #schedule.every(time).minutes.do(func, job_config)
    elif time_unit == 'H':  # Horas
        schedule.every(time).hours.do(run_thread, job_name, job_config)
        #schedule.every(time).minutes.do(func, job_config)
    elif time_unit == 'D':  # Dias
        schedule.every(time).days.do(run_thread, job_name, job_config)
        #schedule.every(time).minutes.do(func, job_config)


def get_job_from_name(job_name: str):
    # Estoque
    if job_name == 'insere_estoque_produto_semaforo_job':
        return instantiate_insert_stock_semaphore_job
    elif job_name == 'envia_estoque_produtos_job':
        return instantiate_send_stock_job
    elif job_name == 'envia_estoque_produtos_ud_job':
        return instantiate_send_ud_stock_job

    # Preco
    elif job_name == 'insere_preco_produto_semaforo_job':
        return instantiate_insert_price_semaphore_job

    elif job_name == 'envia_preco_produtos_job':
        return instantiate_send_price_job

    elif job_name == 'lista_preco_job':
        return instantiate_prices_list_job

    elif job_name == 'produto_lista_preco_job':
        return instantiate_product_prices_list_job

    # Catalogacao
    elif job_name == 'envia_catalogo_produto_semaforo_job':
        return instantiate_insert_products_semaphore_job

    elif job_name == 'envia_catalogo_produto_loja_job':
        return instantiate_send_products_job

    elif job_name == 'imposto_produto_job':
        return instantiate_product_tax_job

    elif job_name == 'imposto_produto_lote_job':
        return instantiate_product_tax_full_job

    # Pedidos
    elif job_name == 'internaliza_pedidos_job':
        return instantiate_orders_job
    elif job_name == 'internaliza_pedidos_pagos_job':
        return instantiate_paid_orders_job
    elif job_name == 'internaliza_pedidos_b2b_job':
        return instantiate_b2b_orders_job
    elif job_name == 'internaliza_pedidos_pagos_b2b_job':
        return instantiate_paid_b2b_orders_job
    elif job_name == 'envia_nota_loja_job':
        return instantiate_invoice_job
    elif job_name == 'envia_rastreio_pedido_job':
        return instantiate_erp_tracking_job

    # Clientes
    elif job_name == 'integra_cliente_b2b_job':
        return instantiate_client_b2b_integration_job
    elif job_name == 'integra_cliente_job':
        return instantiate_client_integration_job
    elif job_name == 'integra_cliente_aprovado_job':
        return intantiate_send_approved_clients_job

    # PlanoPagamentoCliente
    elif job_name == 'envia_plano_pagamento_cliente_job':
        return instantiate_client_payment_plan_job
    elif job_name == 'insere_cliente_plano_pagamento_semaforo_job':
        return instantiate_insert_client_no_exists_payment_plan_semaphore_job

    # Representantes
    elif job_name == 'envia_representante_job':
        return instantiate_representative_job

    # Notificacao
    elif job_name == 'periodic_execution_notification':
        return instantiate_periodic_execution_notification

# endregion ConfigJobs


modules: list = [oking.Module(**m) for m in src.client_data.get('modulos')]
assert modules is not None, 'Nao foi possivel obter os modulos da integracao. Por favor, entre em contato com o suporte.'
for module in modules:
    schedule_job({
        'db_host': src.client_data.get('host'),
        'db_port': src.client_data.get('port'),
        'db_user': src.client_data.get('user'),
        'db_type': src.client_data.get('db_type'),
        'db_seller': src.client_data.get('loja_id'),
        'db_url_api': src.client_data.get('url_api'),
        'db_name': src.client_data.get('database'),
        'db_pwd': src.client_data.get('password'),
        'db_client': src.client_data.get('diretorio_client'),
        'send_logs': module.send_logs,
        'job_name': module.job_name,
        'sql': module.sql
    }, module.time_unit, module.time)

# Job para notificar execucao periodica do Oking a cada 30 min
schedule_job({
    'job_name': 'periodic_execution_notification',
    'execution_start_time': src.start_time,
    'job_qty': len(schedule.get_jobs()),
    'integration_id': src.client_data.get('integracao_id')
}, 'M', 30)


def main():
    logger.info('Iniciando oking __main__')
    while True:
        try:
            schedule.run_pending()
            sleep(5)
        except Exception as e:
            logger.error(f'Erro não tratado capturado: {str(e)}')
            send_log('__main__', src.client_data.get('enviar_logs'), False, f'', 'error', '')


if __name__ == "__main__":
    main()
