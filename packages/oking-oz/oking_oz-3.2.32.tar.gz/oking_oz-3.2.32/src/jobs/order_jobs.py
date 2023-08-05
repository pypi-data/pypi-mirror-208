import logging
import threading
from datetime import datetime
from time import sleep

from src.database.queries import get_order_protocol_nf_command
from src.entities.log import Log
import src
import src.api.okvendas as api_okvendas
import src.database.connection as database
import src.database.utils as utils
from src.database import queries
from src.database.utils import DatabaseConfig
from src.entities.orderb2b import OrderB2B
from src.entities.orderb2c import OrderB2C
from src.entities.tracking import Tracking
from src.entities.invoice import Invoice
from src.entities.order import Order, Queue
from typing import List
from src.jobs.system_jobs import OnlineLogger
from src.api.entities.cliente_erp_code import ClienteErpCode
from threading import Lock

lock = Lock()
logger = logging.getLogger()
send_log = OnlineLogger.send_log

default_limit = 100
queue_status = {
    'pending': 'PEDIDO',
    'paid': 'PEDIDO_PAGO',
    'invoiced': 'FATURADO',
    'shipped': 'ENCAMINHADO_ENTREGA',
    'delivered': 'ENTREGUE',
    'canceled': 'CANCELADO',
    'no_invoice': 'SEM_NOTA_FISCAL'
}


def define_job_start(job_config: dict) -> None:
    global current_job
    current_job = job_config.get('job_name')
    if current_job == 'internaliza_pedidos_job' or current_job == 'internaliza_pedidos_b2b_job':  # Inicia o job a partir dos pedidos AgPagamento
        with lock:
            logger.info(job_config.get('job_name') + f' | Executando na Thread {threading.current_thread()}')
            job_orders(job_config, True)
    elif current_job == 'internaliza_pedidos_pagos_job' or current_job == 'internaliza_pedidos_pagos_b2b_job':  # Inicia o job a partir do pedidos pagos
        with lock:
            logger.info(job_config.get('job_name') + f' | Executando na Thread {threading.current_thread()}')
            job_orders(job_config)


def job_orders(job_config: dict, start_at_pending: bool = False) -> None:
    try:
        db_config = utils.get_database_config(job_config)
        if not current_job.__contains__('b2b'):
            if job_config.get('db_url_api').__contains__('b2c'):
                if start_at_pending:
                    process_b2c_order_queue(job_config, queue_status.get('pending'), db_config, True)

                process_b2c_order_queue(job_config, queue_status.get('paid'), db_config, True)

                process_b2c_order_queue(job_config, queue_status.get('canceled'), db_config)
            else:
                if start_at_pending:
                    process_order_queue(job_config, queue_status.get('pending'), db_config, True)

                process_order_queue(job_config, queue_status.get('paid'), db_config, True)

                process_order_queue(job_config, queue_status.get('canceled'), db_config)

        else:
            if start_at_pending:
                process_b2b_order_queue(job_config, queue_status.get('pending'), db_config, True)

            process_b2b_order_queue(job_config, queue_status.get('paid'), db_config, True)

            process_b2b_order_queue(job_config, queue_status.get('canceled'), db_config)

    except Exception as e:
        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False, f'Erro ao inicializar job: {str(e)}', 'error', 'PEDIDO')


def job_invoice_orders(job_config: dict):
    with lock:
        logger.info(job_config.get('job_name') + f' | Executando na Thread {threading.current_thread()}')
        try:
            db_config = utils.get_database_config(job_config)
            if db_config.sql is None:
                send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                         f'Comando sql para baixar notas fiscais nao encontrado', 'warning', 'PEDIDO')
            else:
                invoices = query_invoices(job_config, db_config)
                for invoice in invoices:
                    try:
                        invoice_sent = api_okvendas.post_invoices(src.client_data.get('url_api') + '/pedido/faturar',
                                                                  invoice, src.client_data.get('token_api'))
                        if invoice_sent is None:
                            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                     f'NF do pedido {invoice.id} enviada com sucesso para api okvendas', 'info', 'PEDIDO')
                            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                     f'Protocolando NF do pedido {invoice.id}', 'info', 'PEDIDO')
                            try:
                                protocol_order_nf(job_config, db_config, invoice.id)
                                send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                         f'Pedido {invoice.id} protocolado com sucesso', 'info', 'PEDIDO')
                            except Exception as e:
                                send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                         f'Erro ao protocolar pedido {invoice.id}: {str(e)}', 'error', 'PEDIDO')

                            continue
                        else:
                            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                     f'Falha ao enviar NF do pedido {invoice.id} para api okvendas: {invoice_sent.message}',
                                     'error',
                                     'PEDIDO')
                    except Exception as e:
                        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                 f'Falha ao enviar NF do pedido {invoice.id}: {str(e)}', 'error', 'PEDIDO')
        except Exception as e:
            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                     f'Falha na execução do job: {str(e)}', 'error', 'PEDIDO')


def job_send_erp_tracking(job_config: dict):
    with lock:
        logger.info(job_config.get('job_name') + f' | Executando na Thread {threading.current_thread()}')
        try:
            db_config = utils.get_database_config(job_config)
            if db_config.sql is None:
                send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                         f'Comando sql para consultar rastreios nao encontrado', 'warning', 'PEDIDO')
            else:
                trackings = query_trackings(db_config)
                for tracking in trackings:
                    try:
                        tracking_sent = api_okvendas.post_tracking(src.client_data.get('url_api') + '/pedido/encaminhar',
                                                                   tracking, src.client_data.get('token_api'))
                        if tracking_sent is None:
                            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                     f'Rastreio do pedido {tracking.id} enviada com sucesso para api okvendas', 'info',
                                     'PEDIDO')
                            continue
                        else:
                            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                     f'Falha ao enviar rastreio do pedido {tracking.id} para api okvendas: {tracking_sent.message}',
                                     'error', 'PEDIDO')
                    except Exception as e:
                        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                 f'Falha ao enviar rastreio do pedido {tracking.id}: {str(e)}', 'error', 'PEDIDO')
        except Exception as e:
            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                     f'Falha na execução do job: {str(e)}', 'error', 'PEDIDO')


def process_order_queue(job_config: dict, status: str, db_config: DatabaseConfig,
                        status_to_insert: bool = False) -> None:
    try:
        print()
        print()
        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                 f'Consultando fila de pedidos no status {status}', 'info', 'PEDIDO')
        queue = api_okvendas.get_order_queue(
            url=src.client_data.get('url_api') + '/pedido/fila/{0}',
            token=src.client_data.get('token_api'),
            status=status,
            limit=default_limit)

        qty = 0
        for q_order in queue:
            try:
                sleep(0.5)
                qty = qty + 1
                print()
                send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                         f'Iniciando processamento ({qty} de {len(queue)}) pedido {q_order.order_id}', 'info', 'PEDIDO')
                order = api_okvendas.get_order(
                    url=src.client_data.get('url_api') + '/pedido/{0}',
                    token=src.client_data.get('token_api'),
                    order_id=q_order.order_id
                )

                if order.erp_code is not None and order.erp_code != '':  # Pedido integrado anteriormente

                    if check_order_existence(db_config, order.order_id):
                        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                 f'Pedido ja integrado com o ERP, comparando status com o semaforo', 'info', 'PEDIDO')
                        if check_order_status(db_config, order.order_id,
                                              order.status):  # Valida se o status do pedido eh o mesmo status no semaforo
                            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                     f'Pedido consta com o mesmo status do banco semaforo. Protocolando pedido...',
                                     'info', 'PEDIDO')
                            protocol_order(job_config, db_config=db_config, order=order, queue_order=q_order,
                                           order_erp_id='', client_erp_id='')
                            continue

                        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                 f'Status do pedido diferente do semaforo, chamando procedure de atualizacao...',
                                 'info', 'PEDIDO')
                        if call_update_order_procedure(job_config, db_config, order):
                            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                     f'Pedido atualizado com sucesso', 'info', 'PEDIDO')
                            protocol_order(job_config, db_config=db_config, order=order, queue_order=q_order,
                                           order_erp_id='', client_erp_id='')
                    else:
                        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                 f'Pedido {order.order_id} nao existe no banco semaforo porem ja foi integrado previamente. Protocolando pedido...',
                                 'warning', 'PEDIDO')
                        protocol_non_existent_order(job_config, q_order)

                else:  # Pedido nao integrado anteriormente

                    if check_non_integrated_order_existence(db_config,
                                                            order.order_id):  # Pedido existente no banco semaforo

                        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                 f'Pedido já existente no banco semáforo, porem nao integrado com erp. Chamando procedures',
                                 'info', 'PEDIDO')
                        sp_success, client_erp_id, order_erp_id = call_order_procedures(job_config, db_config,
                                                                                        q_order.order_id)
                        if sp_success:
                            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                     f'Chamadas das procedures executadas com sucesso, protocolando pedido...', 'info',
                                     'PEDIDO')
                            protocol_order(job_config, db_config=db_config, order=order, queue_order=q_order,
                                           order_erp_id=order_erp_id, client_erp_id=client_erp_id)

                    elif status_to_insert:  # Pedido nao existe no semaforo e esta em status de internalizacao (pending e paid)

                        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                 f'Inserindo novo pedido no banco semaforo', 'info', 'PEDIDO')
                        inserted = insert_temp_order(job_config, order, db_config)
                        if inserted:
                            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                     f'Pedido inserido com sucesso, chamando procedures...', 'info', 'PEDIDO')
                            sp_success, client_erp_id, order_erp_id = call_order_procedures(job_config, db_config,
                                                                                            q_order.order_id)
                            if sp_success:
                                send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                         f'Chamadas das procedures executadas com sucesso, protocolando pedido...',
                                         'info', 'PEDIDO')
                                protocol_order(job_config, db_config=db_config, order=order, queue_order=q_order,
                                               order_erp_id=order_erp_id, client_erp_id=client_erp_id)

                    else:  # Pedido nao existe no semaforo e nao esta em status de internalizacao (pending e paid)
                        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                 f'Pedido nao existente no banco semaforo e nao se encontra em status de internalizacao',
                                 'warning', 'PEDIDO')

            except Exception as e:
                send_log(job_config.get('job_name'), job_config.get('enviar_logs'), True,
                         f'Erro no processamento do pedido {q_order.order_id}: {str(e)}', 'error', 'PEDIDO',
                         q_order.order_id)
    except Exception as e:
        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), True,
                 f'Erro ao inicializar job de processamento de pedidos do status {status}: {str(e)}', 'error', 'PEDIDO')


def process_b2c_order_queue(job_config: dict, status: str, db_config: DatabaseConfig,
                            status_to_insert: bool = False) -> None:
    try:
        print()
        print()
        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                 f'Consultando fila de pedidos no status {status}', 'info', 'PEDIDO')
        queue = api_okvendas.get_order_queue(
            url=src.client_data.get('url_api') + '/pedido/fila/{0}',
            token=src.client_data.get('token_api'),
            status=status,
            limit=default_limit)

        qty = 0
        for q_order in queue:
            try:
                sleep(0.5)
                qty = qty + 1
                print()
                send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                         f'Iniciando processamento ({qty} de {len(queue)}) pedido {q_order.order_id}', 'info', 'PEDIDO')
                order = api_okvendas.get_order_b2c(
                    url=src.client_data.get('url_api') + '/pedido/{0}',
                    token=src.client_data.get('token_api'),
                    order_id=q_order.order_id
                )

                if order.erp_code is not None and order.erp_code != '':  # Pedido integrado anteriormente
                    if check_order_existence(db_config, order.order_id):
                        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                 f'Pedido ja integrado com o ERP, comparando status com o semaforo', 'info', 'PEDIDO')
                        if check_order_status(db_config, order.order_id,
                                              order.status):  # Valida se o status do pedido eh o mesmo status no semaforo
                            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                     f'Pedido consta com o mesmo status do banco semaforo. Protocolando pedido...',
                                     'info', 'PEDIDO')
                            protocol_order(job_config, db_config=db_config, order=order, queue_order=q_order,
                                           order_erp_id='', client_erp_id='')
                            continue

                        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                 f'Status do pedido diferente do semaforo, chamando procedure de atualizacao...',
                                 'info', 'PEDIDO')
                        if call_update_order_procedure(job_config, db_config, order):
                            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                     f'Pedido atualizado com sucesso', 'info', 'PEDIDO')
                            protocol_order(job_config, db_config=db_config, order=order, queue_order=q_order,
                                           order_erp_id='', client_erp_id='')
                    else:
                        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                 f'Pedido {order.order_id} nao existe no banco semaforo porem ja foi integrado previamente. Protocolando pedido...',
                                 'warning', 'PEDIDO')
                        protocol_non_existent_order(job_config, q_order)

                else:  # Pedido nao integrado anteriormente

                    if check_non_integrated_order_existence(db_config,
                                                            order.order_id):  # Pedido existente no banco semaforo

                        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                 f'Pedido já existente no banco semáforo, porem nao integrado com erp. Chamando procedures',
                                 'info', 'PEDIDO')
                        sp_success, client_erp_id, order_erp_id = call_order_procedures(job_config, db_config,
                                                                                        q_order.order_id)
                        if sp_success:
                            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                     f'Chamadas das procedures executadas com sucesso, protocolando pedido...', 'info',
                                     'PEDIDO')
                            protocol_order(job_config, db_config=db_config, order=order, queue_order=q_order,
                                           order_erp_id=order_erp_id, client_erp_id=client_erp_id)

                    elif status_to_insert:  # Pedido nao existe no semaforo e esta em status de internalizacao (pending e paid)

                        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                 f'Inserindo novo pedido no banco semaforo', 'info', 'PEDIDO')
                        inserted = insert_temp_b2c_order(job_config, order, db_config)
                        if inserted:
                            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                     f'Pedido inserido com sucesso, chamando procedures...', 'info', 'PEDIDO')
                            sp_success, client_erp_id, order_erp_id = call_order_procedures(job_config, db_config,
                                                                                            q_order.order_id)
                            if sp_success:
                                send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                         f'Chamadas das procedures executadas com sucesso, protocolando pedido...',
                                         'info',
                                         'PEDIDO')
                                protocol_order(job_config, db_config=db_config, order=order, queue_order=q_order,
                                               order_erp_id=order_erp_id, client_erp_id=client_erp_id)

                    else:  # Pedido nao existe no semaforo e nao esta em status de internalizacao (pending e paid)
                        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                 f'Pedido nao existente no banco semaforo e nao se encontra em status de internalizacao',
                                 'warning', 'PEDIDO')

            except Exception as e:
                send_log(job_config.get('job_name'), job_config.get('enviar_logs'), True,
                         f'Erro no processamento do pedido {q_order.order_id}: {str(e)}', 'error', 'PEDIDO',
                         q_order.order_id)
    except Exception as e:
        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), True,
                 f'Erro ao inicializar job de processamento de pedidos do status {status}: {str(e)}', 'error', 'PEDIDO')


def process_b2b_order_queue(job_config: dict, status: str, db_config: DatabaseConfig,
                            status_to_insert: bool = False) -> None:
    try:
        print()
        print()
        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                 f'Consultando fila de pedidos no status {status}', 'info', 'PEDIDO')
        queue = api_okvendas.get_order_queue(
            url=src.client_data.get('url_api') + '/pedido/fila/{0}',
            token=src.client_data.get('token_api'),
            status=status,
            limit=default_limit)

        qty = 0
        for q_order in queue:
            try:
                sleep(0.5)
                qty = qty + 1
                print()
                send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                         f'Iniciando processamento ({qty} de {len(queue)}) pedido {q_order.order_id}', 'info', 'PEDIDO')
                order = api_okvendas.get_order_b2b(
                    url=src.client_data.get('url_api') + '/pedidoB2B/{0}',
                    token=src.client_data.get('token_api'),
                    order_id=q_order.order_id
                )

                if order.erp_code is not None and order.erp_code != '':  # Pedido integrado anteriormente

                    if check_order_existence(db_config, order.order_id):
                        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                 f'Pedido ja integrado com o ERP, comparando status com o semaforo', 'info', 'PEDIDO')
                        if check_order_status(db_config, order.order_id,
                                              order.status):  # Valida se o status do pedido eh o mesmo status no semaforo
                            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                     f'Pedido consta com o mesmo status do banco semaforo. Protocolando pedido...',
                                     'info', 'PEDIDO')
                            protocol_order(job_config, db_config=db_config, order=order, queue_order=q_order,
                                           order_erp_id='', client_erp_id='')
                            continue

                        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                 f'Status do pedido diferente do semaforo, chamando procedure de atualizacao...',
                                 'info', 'PEDIDO')
                        if call_update_order_procedure(job_config, db_config, order):
                            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                     f'Pedido atualizado com sucesso', 'info', 'PEDIDO')
                            protocol_order(job_config, db_config=db_config, order=order, queue_order=q_order,
                                           order_erp_id='', client_erp_id='')
                    else:
                        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                 f'Pedido {order.order_id} nao existe no banco semaforo porem ja foi integrado previamente. Protocolando pedido...',
                                 'warning', 'PEDIDO')
                        protocol_non_existent_order(job_config, q_order)

                else:  # Pedido nao integrado anteriormente

                    if check_order_existence(db_config, order.order_id):  # Pedido existente no banco semaforo
                        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                 f'Atualizando pedido já existente no banco semaforo', 'info', 'PEDIDO')
                        update_temp_b2b_order(job_config, order, db_config)

                        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                 f'Pedido já existente no banco semáforo, porem nao integrado com erp. Chamando procedures',
                                 'info', 'PEDIDO')
                        sp_success, client_erp_id, order_erp_id = call_order_procedures(job_config, db_config,
                                                                                        q_order.order_id)
                        if sp_success:
                            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                     f'Chamadas das procedures executadas com sucesso, protocolando pedido...', 'info',
                                     'PEDIDO')
                            protocol_order(job_config, db_config=db_config, order=order, queue_order=q_order,
                                           order_erp_id=order_erp_id, client_erp_id=client_erp_id)

                    elif status_to_insert:  # Pedido nao existe no semaforo e esta em status de internalizacao (pending e paid)
                        if 'cancelado' in order.status:  # Se o status do pedidor for cancelado, e ainda nao existir no semaforo, ira protocolar
                            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                     f'Pedido não existe no semaforo, e está com status de internalização (canceled), removendo pedido da fila pelo protocolo {q_order.protocol}',
                                     'info', 'PEDIDO')
                            protocoled_order = api_okvendas.put_protocol_orders([q_order.protocol])
                            if protocoled_order:
                                send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                         f'Pedido protocolado via api OkVendas', 'info', 'PEDIDO')
                            else:
                                send_log(job_config.get('job_name'), job_config.get('enviar_logs'), True,
                                         f'Falha ao protocolar pedido {order.order_id} via api OkVendas', 'warning',
                                         'PEDIDO')

                        else:
                            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                     f'Inserindo novo pedido no banco semaforo', 'info', 'PEDIDO')
                            inserted = insert_temp_b2b_order(job_config, order, db_config)
                            if inserted:
                                send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                         f'Pedido inserido com sucesso, chamando procedures...', 'info', 'PEDIDO')
                                sp_success, client_erp_id, order_erp_id = call_order_procedures(job_config, db_config,
                                                                                                q_order.order_id)
                                if sp_success:
                                    send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                             f'Chamadas das procedures executadas com sucesso, protocolando pedido...',
                                             'info', 'PEDIDO')
                                    protocol_order(job_config, db_config=db_config, order=order, queue_order=q_order,
                                                   order_erp_id=order_erp_id, client_erp_id=client_erp_id)

                    else:  # Pedido nao existe no semaforo e nao esta em status de internalizacao (pending e paid)
                        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                                 f'Pedido nao existente no banco semaforo e nao se encontra em status de internalizacao',
                                 'warning', 'PEDIDO')

            except Exception as e:
                send_log(job_config.get('job_name'), job_config.get('enviar_logs'), True,
                         f'Erro no processamento do pedido {q_order.order_id}: {str(e)}', 'error', 'PEDIDO',
                         q_order.order_id)
    except Exception as e:
        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), True,
                 f'Erro ao inicializar job de processamento de pedidos do status {status}: {str(e)}', 'error', 'PEDIDO')


def protocol_order(job_config: dict, db_config: DatabaseConfig, order, queue_order: Queue, order_erp_id: str = '',
                   client_erp_id: str = '') -> None:
    db = database.Connection(db_config)
    try:
        if order_erp_id != '':
            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                     f'Protocolando pedido com codigo_referencia {order_erp_id}', 'info', 'PEDIDO')
            updated_order_code = api_okvendas.put_order_erp_code(
                src.client_data.get('url_api') + '/pedido/integradoERP',
                src.client_data.get('token_api'),
                order.order_id,
                order_erp_id)
            if updated_order_code:
                send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                         f'Codigo Erp do pedido atualizado via api OkVendas', 'info', 'PEDIDO')
            else:
                send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                         f'Falha ao atualizar o Codigo Erp do pedido via api OkVendas', 'warning', 'PEDIDO')

        if client_erp_id != '':
            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                     f'Salvando codigo do erp do cliente no banco semaforo {client_erp_id}', 'info', 'PEDIDO')
            conn = db.get_conect()
            cursor = conn.cursor()
            cursor.execute(queries.get_client_protocol_command(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type, [client_erp_id, order.order_id]))
            cursor.close()
            conn.commit()
            conn.close()

            client_erp_code = ClienteErpCode(
                cpf_cnpj=order.user.cpf if order.user.cnpj is None or order.user.cnpj == '' else order.user.cnpj,
                codigo_cliente=client_erp_id)

            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                     f'Protocolando cliente via api okvendas com codigo_referencia {client_erp_id}', 'info', 'PEDIDO')
            updated_client_code = api_okvendas.put_client_erp_code(client_erp_code)
            if updated_client_code:
                send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                         f'Codigo Erp do cliente atualizado via api OkVendas', 'info', 'PEDIDO')
            else:
                send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                         f'Falha ao atualizar o Codigo Erp do cliente via api OkVendas', 'warning', 'PEDIDO')

        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                 f'Removendo pedido da fila pelo protocolo {queue_order.protocol}', 'info', 'PEDIDO')
        protocoled_order = api_okvendas.put_protocol_orders([queue_order.protocol])
        if protocoled_order:
            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                     f'Pedido protocolado via api OkVendas', 'info', 'PEDIDO')
        else:
            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                     f'Falha ao protocolar pedido via api OkVendas', 'warning', 'PEDIDO')

        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                 f'Protocolando pedido no banco semaforo', 'info', 'PEDIDO')
        conn = db.get_conect()
        cursor = conn.cursor()
        cursor.execute(queries.get_order_protocol_command(db_config.db_type),
                       queries.get_command_parameter(db_config.db_type, [order_erp_id, order.order_id]))
        cursor.close()
        conn.commit()
        conn.close()
    except Exception as e:
        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), True,
                 f'Erro ao protocolar pedidos: {str(e)}', 'error', 'PEDIDO', order.order_id)


def protocol_order_nf(job_config: dict, db_config: DatabaseConfig, order_id) -> None:
    db = database.Connection(db_config)
    try:
        conn = db.get_conect()
        cursor = conn.cursor()
        cursor.execute(queries.get_order_protocol_nf_command(db_config.db_type),
                       queries.get_command_parameter(db_config.db_type, [order_id]))
        cursor.close()
        conn.commit()
        conn.close()
    except Exception as e:
        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), True,
                 f'Erro ao protocolar nota fiscal: {str(e)}', 'error', 'PEDIDO', order_id)
        raise e


def protocol_non_existent_order(job_config: dict, queue_order: Queue) -> None:
    try:
        protocoled_order = api_okvendas.put_protocol_orders([queue_order.protocol])
        if protocoled_order:
            logger.info(current_job + f' | Pedido {queue_order.order_id} protocolado via api OkVendas')
        else:
            logger.warning(current_job + f' | Falha ao protocolar pedido {queue_order.order_id} via api OkVendas')
    except Exception as ex:
        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), True,
                 f'Erro ao protocolar pedido {queue_order.order_id}: {str(ex)}', 'error', 'PEDIDO',
                 queue_order.order_id)


def insert_temp_order(job_config: dict, order: Order, db_config: DatabaseConfig) -> bool:
    step = ''
    db = database.Connection(db_config)
    conn = db.get_conect()
    try:
        step = 'conexao'
        cursor = conn.cursor()

        existent_client = None
        if order.user.erp_code is not None and order.user.erp_code != '' and order.user.erp_code != '0':  # Por padrao o erp_code vem = '0' da api okvendas
            cursor.execute(queries.get_query_client_erp(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type, [order.user.erp_code]))
            existent_client = cursor.fetchone()

        if existent_client is None:
            # insere cliente
            step = 'insere cliente'
            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                     f'\tPedido {order.order_id}: Inserindo cliente', 'info', 'PEDIDO')
            cursor.execute(queries.get_insert_client_command(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type, [
                               order.user.name or order.user.company_name,
                               order.user.company_name or order.user.name,
                               order.user.cpf,
                               order.user.cnpj,
                               order.user.email,
                               order.user.residential_phone,
                               order.user.mobile_phone,
                               order.user.address.zipcode,
                               order.user.address.address_type,
                               order.user.address.address_line,
                               order.user.address.number,
                               order.user.address.complement,
                               order.user.address.neighbourhood or " ",
                               order.user.address.city,
                               order.user.address.state,
                               order.user.address.reference,
                               'IN',
                               order.user.address.ibge_code
                           ]))
        else:
            # update no cliente existente
            step = 'update cliente'
            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                     f'\tPedido {order.order_id}: Atualizando cliente existente', 'info', 'PEDIDO')
            cursor.execute(queries.get_update_client_sql(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type, [
                               order.user.name,
                               order.user.company_name or order.user.name,
                               order.user.cpf,
                               order.user.cnpj,
                               order.user.email,
                               order.user.residential_phone,
                               order.user.mobile_phone,
                               order.user.address.zipcode,
                               order.user.address.address_type,
                               order.user.address.address_line,
                               order.user.address.number,
                               order.user.address.complement,
                               order.user.address.neighbourhood,
                               order.user.address.city,
                               order.user.address.state,
                               order.user.address.reference,
                               order.user.address.ibge_code,
                               order.user.erp_code
                           ]))

        if cursor.rowcount > 0:
            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                     f'Cliente inserido/atualizado para o pedido {order.order_id}', 'info', 'PEDIDO')
            if order.user.erp_code is not None and order.user.erp_code not in ['', '0']:
                send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                         f'Consultando id do cliente no banco semaforo pelo codigo erp', 'info', 'PEDIDO')
                cursor.execute(queries.get_query_client_erp(db_config.db_type),
                               queries.get_command_parameter(db_config.db_type, [order.user.erp_code]))
            elif order.user.cpf is not None and order.user.cpf != '':
                send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                         f'Consultando id do cliente no banco semaforo pelo cpf', 'info', 'PEDIDO')
                cursor.execute(queries.get_query_client_cpf(db_config.db_type),
                               queries.get_command_parameter(db_config.db_type, [order.user.cpf]))
            elif order.user.cnpj is not None and order.user.cnpj != '':
                send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                         f'Consultando id do cliente no banco semaforo pelo cnpj', 'info', 'PEDIDO')
                cursor.execute(queries.get_query_client_cnpj(db_config.db_type),
                               queries.get_command_parameter(db_config.db_type, [order.user.cnpj]))

            client_id_data = cursor.fetchone()
            if client_id_data is None:
                raise Exception('Nao foi possivel obter o cliente inserido do banco de dados')

            client_id, = client_id_data
            if client_id is None or client_id <= 0:
                cursor.close()
                raise Exception('Nao foi possivel obter o cliente inserido do banco de dados')

            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                     f'Cliente no banco semaforo encontrado {client_id}', 'info', 'PEDIDO')
        else:
            cursor.close()
            raise Exception('O cliente nao foi inserido')

        # insere pedido
        step = 'insere pedido'
        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                 f'\tPedido {order.order_id}: Inserindo cabecalho pedido', 'info', 'PEDIDO')
        cursor.execute(queries.get_insert_order_command(db_config.db_type),
                       queries.get_command_parameter(db_config.db_type, [
                           order.order_id,
                           order.order_code,
                           str(datetime.strptime(order.date.replace('T', ' '),
                                                 '%Y-%m-%d %H:%M:%S') if order.date is not None else ''),
                           order.status,
                           client_id,
                           order.total_amount,
                           order.total_discount,
                           order.freight_amount,
                           order.additional_payment_amount,
                           str(datetime.strptime(order.paid_date.replace('T', ' '),
                                                 '%Y-%m-%d %H:%M:%S') if order.paid_date is not None else ''),
                           order.payment_type,
                           order.flag,
                           order.parcels,
                           order.erp_payment_condition,
                           order.tracking_code,
                           str(datetime.strptime(order.delivery_forecast.replace('T', ' '),
                                                 '%Y-%m-%d %H:%M:%S') if order.delivery_forecast is not None else ''),
                           order.carrier,
                           order.shipping_mode,
                           order.channel_id,
                           job_config.get('db_seller'),
                           order.erp_payment_option,
                           order.user.address.zipcode,
                           order.user.address.address_type,
                           order.user.address.address_line,
                           order.user.address.number,
                           order.user.address.complement,
                           order.user.address.neighbourhood or " ",
                           order.user.address.city,
                           order.user.address.state,
                           order.user.address.reference,
                           order.user.address.ibge_code
                       ]))

        if cursor.rowcount > 0:
            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                     f'Pedido {order.order_id} inserido', 'info', 'PEDIDO')
            cursor.execute(queries.get_query_order(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type, [order.order_id]))
            (order_id,) = cursor.fetchone()
            if order_id is None or order_id <= 0:
                cursor.close()
                raise Exception('Nao foi possivel obter o pedido inserido no banco de dados')
        else:
            cursor.close()
            raise Exception('O cliente nao foi inserido')

        # insere itens
        step = 'insere itens'
        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                 f'\tPedido {order.order_id} com id semaforo {order_id}: Inserindo itens do pedido', 'info', 'PEDIDO')
        for item in order.items:
            cursor.execute(queries.get_insert_order_items_command(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type, [
                               order_id,
                               item.sku,
                               item.erp_code,
                               item.quantity,
                               item.ean,
                               item.value,
                               item.discount,
                               item.freight_value
                           ]))

        cursor.close()
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), True,
                 f'Passo {step} - Erro durante a inserção dos dados do pedido {order.order_id}: {str(e)}', 'error',
                 'PEDIDO',
                 str(order.order_id))
        conn.rollback()
        conn.close()
        return False


def insert_temp_b2c_order(job_config: dict, order: OrderB2C, db_config: DatabaseConfig) -> bool:
    step = ''
    db = database.Connection(db_config)
    conn = db.get_conect()
    try:
        step = 'conexao'
        cursor = conn.cursor()

        existent_client = None
        if order.user.erp_code is not None and order.user.erp_code != '' and order.user.erp_code != '0':  # Por padrao o erp_code vem = '0' da api okvendas
            cursor.execute(queries.get_query_client_erp(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type, [order.user.erp_code]))
            existent_client = cursor.fetchone()

        if existent_client is None:
            # insere cliente
            step = 'insere cliente'
            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                     f'\tPedido {order.order_id}: Inserindo cliente', 'info', 'PEDIDO')
            cursor.execute(queries.get_insert_b2c_client_command(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type, [
                               order.user.name or order.user.company_name,
                               order.user.company_name or order.user.name,
                               order.user.cpf,
                               order.user.cnpj,
                               order.user.email,
                               order.user.residential_phone,
                               order.user.mobile_phone,
                               order.user.address.zipcode,
                               order.user.address.address_type,
                               order.user.address.address_line,
                               order.user.address.number,
                               order.user.address.complement,
                               order.user.address.neighbourhood or " ",
                               order.user.address.city,
                               order.user.address.state,
                               order.user.address.reference,
                               'IN'
                           ]))
        else:
            # update no cliente existente
            step = 'update cliente'
            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                     f'\tPedido {order.order_id}: Atualizando cliente existente', 'info', 'PEDIDO')
            cursor.execute(queries.get_update_b2c_client_sql(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type, [
                               order.user.name,
                               order.user.company_name or order.user.name,
                               order.user.cpf,
                               order.user.cnpj,
                               order.user.email,
                               order.user.residential_phone,
                               order.user.mobile_phone,
                               order.user.address.zipcode,
                               order.user.address.address_type,
                               order.user.address.address_line,
                               order.user.address.number,
                               order.user.address.complement,
                               order.user.address.neighbourhood,
                               order.user.address.city,
                               order.user.address.state,
                               order.user.address.reference,
                               order.user.erp_code
                           ]))

        if cursor.rowcount > 0:
            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                     f'Cliente inserido/atualizado para o pedido {order.order_id}', 'info', 'PEDIDO')
            cursor.execute(queries.get_query_client_erp(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type, [order.user.erp_code]))
            (client_id,) = cursor.fetchone()
            if client_id is None or client_id <= 0:
                cursor.close()
                raise Exception('Nao foi possivel obter o cliente inserido do banco de dados')
        else:
            cursor.close()
            raise Exception('O cliente nao foi inserido')

        # insere pedido
        step = 'insere pedido'
        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                 f'\tPedido {order.order_id}: Inserindo cabecalho pedido', 'info', 'PEDIDO')
        cursor.execute(queries.get_insert_b2c_order_command(db_config.db_type),
                       queries.get_command_parameter(db_config.db_type, [
                           order.order_id,
                           order.order_code,
                           str(datetime.strptime(order.date.replace('T', ' '),
                                                 '%Y-%m-%d %H:%M:%S') if order.date is not None else ''),
                           order.status,
                           client_id,
                           order.total_amount,
                           order.total_discount,
                           order.freight_amount,
                           order.additional_payment_amount,
                           str(datetime.strptime(order.paid_date.replace('T', ' '),
                                                 '%Y-%m-%d %H:%M:%S') if order.paid_date is not None else ''),
                           order.payment_type,
                           order.flag,
                           order.parcels,
                           order.erp_payment_condition,
                           order.tracking_code,
                           str(datetime.strptime(order.delivery_forecast.replace('T', ' '),
                                                 '%Y-%m-%d %H:%M:%S') if order.delivery_forecast is not None else ''),
                           order.carrier,
                           order.shipping_mode,
                           order.channel_id,
                           job_config.get('db_seller'),
                           order.user.address.zipcode,
                           order.user.address.address_type,
                           order.user.address.address_line,
                           order.user.address.number,
                           order.user.address.complement,
                           order.user.address.neighbourhood or " ",
                           order.user.address.city,
                           order.user.address.state,
                           order.user.address.reference,
                           order.user.address.ibge_code
                       ]))

        if cursor.rowcount > 0:
            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                     f'Pedido {order.order_id} inserido', 'info', 'PEDIDO')
            cursor.execute(queries.get_query_order(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type, [order.order_id]))
            (order_id,) = cursor.fetchone()
            if order_id is None or order_id <= 0:
                cursor.close()
                raise Exception('Nao foi possivel obter o pedido inserido no banco de dados')
        else:
            cursor.close()
            raise Exception('O cliente nao foi inserido')

        # insere itens
        step = 'insere itens'
        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                 f'\tPedido {order.order_id} com id semaforo {order_id}: Inserindo itens do pedido', 'info', 'PEDIDO')
        for item in order.items:
            cursor.execute(queries.get_insert_b2c_order_items_command(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type, [
                               order_id,
                               item.sku,
                               item.erp_code,
                               item.quantity,
                               item.ean,
                               item.value,
                               item.discount,
                               item.freight_value
                           ]))

        cursor.close()
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), True,
                 f'Passo {step} - Erro durante a inserção dos dados do pedido {order.order_id}: {str(e)}', 'error',
                 'PEDIDO',
                 str(order.order_id))
        conn.rollback()
        conn.close()
        return False


def insert_temp_b2b_order(job_config: dict, order: OrderB2B, db_config: DatabaseConfig) -> bool:
    step = ''
    db = database.Connection(db_config)
    conn = db.get_conect()
    try:
        step = 'conexao'
        cursor = conn.cursor()

        existent_client = None
        if order.user.erp_code is not None and order.user.erp_code != '' and order.user.erp_code != '0':  # Por padrao o erp_code vem = '0' da api okvendas
            cursor.execute(queries.get_query_client_erp(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type, [order.user.erp_code]))
            existent_client = cursor.fetchone()

        if existent_client is None:
            # insere cliente
            step = 'insere cliente'
            logger.info(f'')
            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                     f'\tPedido {order.order_id}: Inserindo cliente', 'info', 'PEDIDO')

            erp_code = order.user.erp_code if order.user.erp_code is not None and order.user.erp_code not in ['', '0'] else None

            cursor.execute(queries.get_insert_b2b_client_command(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type, [
                               order.user.name or order.user.company_name,
                               order.user.company_name or order.user.name,
                               order.user.cpf,
                               order.user.cnpj,
                               order.user.email,
                               order.user.residential_phone,
                               order.user.mobile_phone,
                               order.user.address.zipcode,
                               order.user.address.address_type,
                               order.user.address.address_line,
                               order.user.address.number,
                               order.user.address.complement,
                               order.user.address.neighbourhood or " ",
                               order.user.address.city,
                               order.user.address.state,
                               order.user.address.reference,
                               'IN',
                               order.user.state_registry,
                               order.user.address.ibge_code,
                               erp_code,
                           ]))
        else:
            # update no cliente existente
            step = 'update cliente'
            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                     f'\tPedido {order.order_id}: Atualizando cliente existente', 'info', 'PEDIDO')
            cursor.execute(queries.get_update_b2b_client_sql(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type, [
                               order.user.name,
                               order.user.company_name or order.user.name,
                               order.user.cpf,
                               order.user.cnpj,
                               order.user.email,
                               order.user.residential_phone,
                               order.user.mobile_phone,
                               order.user.address.zipcode,
                               order.user.address.address_type,
                               order.user.address.address_line,
                               order.user.address.number,
                               order.user.address.complement,
                               order.user.address.neighbourhood,
                               order.user.address.city,
                               order.user.address.state,
                               order.user.address.reference,
                               order.user.address.ibge_code,
                               order.user.state_registry,
                               order.user.erp_code
                           ]))

        if cursor.rowcount > 0:
            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                     f'Cliente inserido/atualizado para o pedido {order.order_id}', 'info', 'PEDIDO')
            if order.user.erp_code is not None and order.user.erp_code not in ['', '0']:
                send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                         f'Consultando id do cliente no banco semaforo pelo codigo erp', 'info', 'PEDIDO')
                cursor.execute(queries.get_query_client_erp(db_config.db_type),
                               queries.get_command_parameter(db_config.db_type, [order.user.erp_code]))
            elif order.user.cpf is not None and order.user.cpf != '':
                send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                         f'Consultando id do cliente no banco semaforo pelo cpf', 'info', 'PEDIDO')
                cursor.execute(queries.get_query_client_cpf(db_config.db_type),
                               queries.get_command_parameter(db_config.db_type, [order.user.cpf]))
            elif order.user.cnpj is not None and order.user.cnpj != '':
                send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                         f'Consultando id do cliente no banco semaforo pelo cnpj', 'info', 'PEDIDO')
                cursor.execute(queries.get_query_client_cnpj(db_config.db_type),
                               queries.get_command_parameter(db_config.db_type, [order.user.cnpj]))

            client_id_data = cursor.fetchone()
            if client_id_data is None:
                raise Exception('Nao foi possivel obter o cliente inserido do banco de dados')

            client_id, = client_id_data
            if client_id is None or client_id <= 0:
                cursor.close()
                raise Exception('Nao foi possivel obter o cliente inserido do banco de dados')

            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                     f'Cliente no banco semaforo encontrado {client_id}', 'info', 'PEDIDO')
        else:
            cursor.close()
            raise Exception('O cliente nao foi inserido')

        # insere pedido
        step = 'insere pedido'
        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                 f'\tPedido {order.order_id}: Inserindo cabecalho pedido', 'info', 'PEDIDO')
        cursor.execute(queries.get_insert_b2b_order_command(db_config.db_type),
                       queries.get_command_parameter(db_config.db_type, [
                           order.order_id,
                           order.sale_order_id,
                           str(datetime.strptime(order.order_date.replace('T', ' '),
                                                 '%Y-%m-%d %H:%M:%S') if order.order_date is not None else ''),
                           order.status,
                           client_id,
                           order.total_amount,
                           order.discount_amount,
                           order.freight_amount,
                           0.0,
                           str(datetime.strptime(order.payments[0].bonds[0].paid_date.replace('T', ' '),
                                                 '%Y-%m-%d %H:%M:%S') if len(order.payments) > 0 and len(
                               order.payments[0].bonds) > 0 and order.paid_date is not None else ''),
                           order.payment_type,
                           order.flag,
                           order.installments,
                           order.erp_payment_condition,
                           order.tracking_code,
                           str(datetime.strptime(order.delivery_forecast.replace('T', ' '),
                                                 '%Y-%m-%d %H:%M:%S') if order.delivery_forecast is not None else ''),
                           order.carrier,
                           '',
                           order.channel_id,
                           order.erp_representative,
                           job_config.get('db_seller'),
                           order.erp_payment_option,
                           order.cnpj_intermediary,
                           order.channel_order_code,
                           order.user.delivery_address.zipcode,
                           order.user.delivery_address.address_type,
                           order.user.delivery_address.address_line,
                           order.user.delivery_address.number,
                           order.user.delivery_address.complement,
                           order.user.delivery_address.neighbourhood or " ",
                           order.user.delivery_address.city,
                           order.user.delivery_address.state,
                           order.user.delivery_address.reference,
                           order.user.delivery_address.ibge_code
                       ]))

        if cursor.rowcount > 0:
            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                     f'Pedido {order.order_id} inserido', 'info', 'PEDIDO')
            cursor.execute(queries.get_query_order(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type, [order.order_id]))
            (order_id,) = cursor.fetchone()
            if order_id is None or order_id <= 0:
                cursor.close()
                raise Exception('Nao foi possivel obter o pedido inserido no banco de dados')
        else:
            cursor.close()
            raise Exception('O cliente nao foi inserido')

        # insere itens
        step = 'insere itens'
        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                 f'\tPedido {order.order_id} com id semaforo {order_id}: Inserindo itens do pedido', 'info', 'PEDIDO')
        for item in order.items:
            cursor.execute(queries.get_insert_b2b_order_items_command(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type, [
                               order_id,
                               item.sku,
                               item.erp_code,
                               item.quantity,
                               item.ean,
                               item.value,
                               item.discount,
                               0,  # Valor do frete não necessario, usar o do cabeçalho
                               item.selling_branch_cnpj,
                               item.branch_erp_code,
                               item.expedition_branch,
                               item.invoice_branch
                           ]))

        cursor.close()
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), True,
                 f'Passo {step} - Erro durante a inserção dos dados do pedido {order.order_id}: {str(e)}', 'error',
                 'PEDIDO'
                 , str(order.order_id))
        conn.rollback()
        conn.close()
        return False


def update_temp_b2b_order(job_config: dict, order: OrderB2B, db_config: DatabaseConfig) -> bool:
    step = ''
    db = database.Connection(db_config)
    conn = db.get_conect()
    try:
        step = 'conexao'
        cursor = conn.cursor()

        # update no cliente existente
        step = 'update cliente'
        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                 f'\tPedido {order.order_id}: Atualizando cliente existente', 'info', 'PEDIDO')
        cursor.execute(queries.get_update_b2b_client_sql(db_config.db_type),
                       queries.get_command_parameter(db_config.db_type, [
                           order.user.name,
                           order.user.company_name or order.user.name,
                           order.user.cpf,
                           order.user.cnpj,
                           order.user.email,
                           order.user.residential_phone,
                           order.user.mobile_phone,
                           order.user.address.zipcode,
                           order.user.address.address_type,
                           order.user.address.address_line,
                           order.user.address.number,
                           order.user.address.complement,
                           order.user.address.neighbourhood,
                           order.user.address.city,
                           order.user.address.state,
                           order.user.address.reference,
                           order.user.address.ibge_code,
                           order.user.state_registry,
                           order.user.erp_code
                       ]))

        if cursor.rowcount > 0:
            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                     f'Cliente atualizado para o pedido {order.order_id}', 'info', 'PEDIDO')
            if order.user.erp_code is not None and order.user.erp_code not in ['', '0']:
                send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                         f'Consultando id do cliente no banco semaforo pelo codigo erp', 'info', 'PEDIDO')
                cursor.execute(queries.get_query_client_erp(db_config.db_type),
                               queries.get_command_parameter(db_config.db_type, [order.user.erp_code]))
            elif order.user.cpf is not None and order.user.cpf != '':
                send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                         f'Consultando id do cliente no banco semaforo pelo cpf', 'info', 'PEDIDO')
                cursor.execute(queries.get_query_client_cpf(db_config.db_type),
                               queries.get_command_parameter(db_config.db_type, [order.user.cpf]))
            elif order.user.cnpj is not None and order.user.cnpj != '':
                send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                         f'Consultando id do cliente no banco semaforo pelo cnpj', 'info', 'PEDIDO')
                cursor.execute(queries.get_query_client_cnpj(db_config.db_type),
                               queries.get_command_parameter(db_config.db_type, [order.user.cnpj]))

            client_id_data = cursor.fetchone()
            if client_id_data is None:
                raise Exception('Nao foi possivel obter o cliente atualizado do banco de dados')

            client_id, = client_id_data
            if client_id is None or client_id <= 0:
                cursor.close()
                raise Exception('Nao foi possivel obter o cliente atualizado do banco de dados')

            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                     f'Cliente no banco semaforo encontrado {client_id}', 'info', 'PEDIDO')
        else:
            cursor.close()
            raise Exception('O cliente nao foi inserido')

        # atualizando pedido
        step = 'atualizando pedido'
        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                 f'\tPedido {order.order_id}: Atualizando cabecalho pedido', 'info', 'PEDIDO')
        cursor.execute(queries.get_update_b2b_order_command(db_config.db_type),
                       queries.get_command_parameter(db_config.db_type, [
                           order.erp_payment_condition,
                           order.carrier,
                           '',
                           order.channel_id,
                           order.erp_representative,
                           order.erp_payment_option,
                           order.cnpj_intermediary,
                           order.channel_order_code,
                           order.user.delivery_address.zipcode,
                           order.user.delivery_address.address_type,
                           order.user.delivery_address.address_line,
                           order.user.delivery_address.number,
                           order.user.delivery_address.complement,
                           order.user.delivery_address.neighbourhood or " ",
                           order.user.delivery_address.city,
                           order.user.delivery_address.state,
                           order.user.delivery_address.reference,
                           order.user.delivery_address.ibge_code,
                           order.order_id
                       ]))

        if cursor.rowcount > 0:
            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                     f'Pedido {order.order_id} atualizado', 'info', 'PEDIDO')
            cursor.execute(queries.get_query_order(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type, [order.order_id]))
            (order_id,) = cursor.fetchone()
            if order_id is None or order_id <= 0:
                cursor.close()
                raise Exception('Nao foi possivel obter o pedido que foi atualizado no banco de dados')
        else:
            cursor.close()
            raise Exception('O pedido nao foi atualizado')

        cursor.close()
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), True,
                 f'Passo {step} - Erro durante a atualização do cabeçalho do pedido {order.order_id}: {str(e)}',
                 'error',
                 'PEDIDO'
                 , str(order.order_id))
        conn.rollback()
        conn.close()
        return False


def call_order_procedures(job_config: dict, db_config: DatabaseConfig, order_id: int) -> (bool, str, str):
    client_erp_id = ''
    order_erp_id = ''
    success = True
    db = database.Connection(db_config)
    conn = db.get_conect()
    try:
        cursor = conn.cursor()
        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False, f'Executando procedure de cliente',
                 'info', 'PEDIDO')
        if db_config.is_sql_server():
            cursor.execute('exec openk_semaforo.sp_processa_cliente @pedido = ?', order_id)
            (client_erp_id,) = cursor.fetchone()
        elif db_config.is_oracle():
            client_out_value = cursor.var(str)
            cursor.callproc('OPENK_SEMAFORO.SP_PROCESSA_CLIENTE', [order_id, client_out_value])
            client_erp_id = client_out_value.getvalue()
        elif db_config.is_mysql():
            result = cursor.callproc('openk_semaforo.SP_PROCESSA_CLIENTE', [order_id, (0, 'CHAR')])
            client_erp_id = result[1]

        if client_erp_id is not None:
            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                     f'Cliente ERP criado com sucesso {client_erp_id}', 'info', 'PEDIDO')
            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                     f'Executando procedure de pedido', 'info', 'PEDIDO')
            if db_config.is_sql_server():
                cursor.execute('exec openk_semaforo.sp_processa_pedido @pedido = ?', order_id)
                (order_erp_id,) = cursor.fetchone()
            elif db_config.is_oracle():
                order_out_value = cursor.var(str)
                cursor.callproc('OPENK_SEMAFORO.SP_PROCESSA_PEDIDO', [order_id, int(client_erp_id), order_out_value])
                order_erp_id = order_out_value.getvalue()
            elif db_config.is_mysql():
                result = cursor.callproc('openk_semaforo.SP_PROCESSA_PEDIDO',
                                         [order_id, int(client_erp_id), (0, 'CHAR')])
                order_erp_id = result[2]

            if order_erp_id is not None:
                send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                         f'Pedido ERP criado com sucesso {order_erp_id}', 'info', 'PEDIDO')
            else:
                success = False
                send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                         f'Nao foi possivel obter o id do pedido do ERP (retorno da procedure)', 'warning', 'PEDIDO')
        else:
            success = False
            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                     f'Nao foi possivel obter o id do cliente do ERP (retorno da procedure)', 'warning', 'PEDIDO')

        cursor.close()
        if success:
            conn.commit()
        else:
            conn.rollback()
        conn.close()
        return success, client_erp_id, order_erp_id
    except Exception as e:
        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), True,
                 f'Erro no método de chamada da procedure de internalização do pedido {order_id}: {str(e)}', 'error',
                 'PEDIDO',
                 str(order_id))
        conn.rollback()
        conn.close()


def call_update_order_procedure(job_config: dict, db_config: DatabaseConfig, order) -> bool:
    success = True
    db = database.Connection(db_config)
    conn = db.get_conect()
    try:
        cursor = conn.cursor()
        updated: bool = False
        if db_config.is_sql_server():
            cursor.execute('exec openk_semaforo.sp_atualiza_pedido @pedido = ?', order.order_id)
            (updated,) = cursor.fetchone()
        elif db_config.is_oracle() or db_config.is_mysql():
            order_updated = cursor.var(int)
            cursor.callproc('OPENK_SEMAFORO.SP_ATUALIZA_PEDIDO', [order.order_id, order.status, order_updated])
            updated = order_updated.getvalue()
        if updated is None or updated <= 0:
            success = False
            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                     f'Nao foi possivel atualizar o pedido informado', 'warning', 'PEDIDO')

        cursor.close()
        if success:
            conn.commit()
        else:
            conn.rollback()
        conn.close()
        return success
    except Exception as e:
        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), True,
                 f'Erro no método de chamada da procedure de atualização do pedido {order.order_id}: {str(e)}', 'error',
                 'PEDIDO', str(order.order_id))
        conn.rollback()
        conn.close()


def check_order_existence(db_config: DatabaseConfig, order_id: int) -> bool:
    db = database.Connection(db_config)
    conn = db.get_conect()
    try:
        cursor = conn.cursor()
        cursor.execute(queries.get_query_order(db_config.db_type),
                       queries.get_command_parameter(db_config.db_type, [order_id]))
        existent_order = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return existent_order is not None and existent_order > 0
    except Exception as e:
        conn.close()
        return False


def check_non_integrated_order_existence(db_config: DatabaseConfig, order_id: int) -> bool:
    db = database.Connection(db_config)
    conn = db.get_conect()
    try:
        cursor = conn.cursor()
        cursor.execute(queries.get_query_non_integrated_order(db_config.db_type),
                       queries.get_command_parameter(db_config.db_type, [order_id]))
        existent_order = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return existent_order is not None and existent_order > 0
    except Exception as e:
        conn.close()
        return False


def query_invoices(job_config: dict, db_config: DatabaseConfig) -> List[Invoice]:
    """
    Consulta as notas fiscais a serem enviadas na api do okvendas
    Args:
        job_config: Configuração do job
        db_config: Configuracao do banco de dados

    Returns:
        Lista de notas fiscais para enviar
    """
    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()
    invoices = List[Invoice]
    try:
        if db_config.is_oracle():
            conn.outputtypehandler = database.output_type_handler
        cursor.execute(db_config.sql.replace(';', ''))
        rows = cursor.fetchall()
        columns = [col[0].lower() for col in cursor.description]
        results = [dict(zip(columns, row)) for row in rows]
        cursor.close()
        conn.close()
        if len(results) > 0:
            invoices = [Invoice(**p) for p in results]

    except Exception as ex:
        logger.error(f' ')
        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                 f'Erro ao consultar notas fiscais no banco: {str(ex)}', 'error', 'PEDIDO')

    return invoices


def query_trackings(job_config: dict, db_config: DatabaseConfig) -> List[Tracking]:
    """
    Consulta os rastreios a serem enviados na api do okvendas
    Args:
        job_config: Configuração do job
        db_config: Configuracao do banco de dados

    Returns:
        Lista de notas fiscais para enviar
    """
    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()
    trackings = List[Tracking]
    try:
        cursor.execute(db_config.sql.replace(';', ''))
        rows = cursor.fetchall()
        columns = [col[0].lower() for col in cursor.description]
        results = [dict(zip(columns, row)) for row in rows]
        cursor.close()
        conn.close()
        if len(results) > 0:
            trackings = [Tracking(**p) for p in results]

    except Exception as ex:
        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False,
                 f'Erro ao consultar rastreios no banco: {str(ex)}', 'error', 'PEDIDO')

    return trackings


def check_order_status(db_config: DatabaseConfig, order_id: int, order_status: str) -> bool:
    status_sorted = {
        'Aguardando pagamento.': 1,
        'Pedido confirmado.': 2,
        'Faturado': 3,
        'Em Separação': 4,
        'Separado': 5,
        'Encaminhado para entrega.': 6,
        'Pedido entregue.': 7,
        'Pedido cancelado.': 8,
        'Cancelado a pedido do cliente.': 9,
        'Cancelado, sem pagamento': 10
    }

    with database.Connection(db_config).get_conect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(queries.get_query_order_status(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type, [order_id]))
            result = cursor.fetchone()
            if result is None:
                return False

            semaphore_status, = result
            cursor.execute(queries.get_query_order_sync_date(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type, [order_id]))
            result = cursor.fetchone()
            if result is None:
                return False

            has_sync_date, = result
            return (status_sorted[semaphore_status] >= status_sorted[order_status] and has_sync_date) \
                   or (status_sorted[order_status] >= status_sorted[semaphore_status] and status_sorted[
                order_status] not in [2, 7, 8, 9])
            # True se o pedido possuir data_sincronizacao e o status no semaforo for maior ou igual que o status do pedido no okvendas
            # OU se o status do okvendas for maior ou igual que o status no semaforo, sendo que o status do okvendas nao seja pago ou cancelado
