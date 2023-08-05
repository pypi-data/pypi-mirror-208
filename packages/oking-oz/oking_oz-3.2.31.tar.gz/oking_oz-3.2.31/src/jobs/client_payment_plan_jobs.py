import logging
import threading
from typing import List
import src.database.connection as database
from src.api.entities.plano_pagamento_cliente import PlanoPagamentoCliente
from src.database import queries
from src.database.queries import IntegrationType
from src.database.utils import DatabaseConfig
import src.database.utils as utils
#from src.entities.product import Product
#from src.entities.photos_sku import PhotosSku
import src.api.okvendas as api_okvendas
from src.jobs.system_jobs import OnlineLogger
from src.database.entities.client_payment_plan import ClientPaymentPlan
from threading import Lock

lock = Lock()
logger = logging.getLogger()
send_log = OnlineLogger.send_log


def job_client_payment_plan(job_config_dict: dict):
    with lock:
        """
        Job para inserir os planos de pagamentos dos clientes no banco semáforo
        Args:
            job_config_dict: Configuração do job
        """
        logger.info(job_config_dict.get('job_name') + f' | Executando na Thread {threading.current_thread()}')
        db_config = utils.get_database_config(job_config_dict)
        if db_config.sql is None:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Comando sql para inserir os planos de pagamentos dos clientes no semaforo nao encontrado', 'warning', 'CLIENT_PAYMENT_PLAN')
            return

        try:
            db_client_payment_plan = query_list_client_payment_plan(job_config_dict, db_config)
            if not insert_update_semaphore_client_payment_plan(job_config_dict, db_config, db_client_payment_plan):
                send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True, f'Nao foi possivel inserir os planos de pagamentos dos clientes no banco semaforo', 'error', 'CLIENT_PAYMENT_PLAN')
                return

            split_client_payment_plan = dict.fromkeys(set([d.code_client for d in db_client_payment_plan]), [])
            for cpp in db_client_payment_plan:
                if cpp.code_client in cpp.code_client in split_client_payment_plan.keys():
                    if split_client_payment_plan[cpp.code_client] is not None and len(split_client_payment_plan[cpp.code_client]) <= 0:
                       split_client_payment_plan[cpp.code_client] = [cpp.payment_methods]
                    elif len(split_client_payment_plan[cpp.code_client]) > 0:
                       split_client_payment_plan[cpp.code_client].append(cpp.payment_methods)
                    else:
                       split_client_payment_plan[cpp.code_client] = []


            api_payment_plan_list = [PlanoPagamentoCliente(
                codigo_cliente=k,
                formas_pagamento=v) for k, v in split_client_payment_plan.items()]

            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Enviando os planos de pagamentos dos clientes via api okvendas', 'info', 'CLIENT_PAYMENT_PLAN')

            for api_client_payment_plan in api_payment_plan_list:
                try:
                    response_list, status_code, lista = api_okvendas.post_client_payment_plan(api_client_payment_plan)
                    message_response = format_response(lista)
                    if not response_list:
                        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Erro ao processar a forma de pagamento dos clientes do seguinte cliente {api_client_payment_plan.codigo_cliente} {message_response}', 'warning', 'CLIENT_PAYMENT_PLAN')

                    if status_code == 207:
                        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,
                                 f'Inserção/Atualização parcial das formas de pagamento dos clientes do seguinte cliente {api_client_payment_plan.codigo_cliente} {message_response}','warning', 'CLIENT_PAYMENT_PLAN')

                    if protocol_semaphore_client_payment_plan(job_config_dict, db_config, api_client_payment_plan.codigo_cliente):
                        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Plano de Pagamento do cliente {api_client_payment_plan.codigo_cliente} protocolado no banco semaforo', 'info', 'CLIENT_PAYMENT_PLAN')
                    else:
                        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Falha ao protocolar o plano de pagamento do cliente {api_client_payment_plan.codigo_cliente} ', 'warning', 'CLIENT_PAYMENT_PLAN')

                except Exception as e:
                    send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Falha ao enviar a forma de pagamento do cliente {api_client_payment_plan.codigo_cliente} : {str(e)}', 'error', 'CLIENT_PAYMENT_PLAN')

        except Exception as ex:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True, f'Erro {str(ex)}', 'error', 'CLIENT_PAYMENT_PLAN')


def format_response(response):
    message = ''
    lista = response.get('Response')
    if lista is None:
        if response.get('Message') is not None:
            message = response.get('Message')
        return message

    for item in lista:
        if item['Identifiers'] is None or len(item['Identifiers']) <= 0:
            continue

        message = message + f'{item["Message"]} '

    return message


def query_list_client_payment_plan(job_config_dict: dict, db_config: DatabaseConfig) -> List[ClientPaymentPlan]:
    """
        Consultar no banco semáforo os planos de pagamentos dos clientes

        Args:
            job_config_dict: Configuração do job
            db_config: Configuração do banco de dados

        Returns:
        Lista dos planos de pagamentos dos clientes
        """
    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()
    try:
        cursor.execute(db_config.sql)
        rows = cursor.fetchall()
        columns = [col[0].lower() for col in cursor.description]
        results = list(dict(zip(columns, row)) for row in rows)
        cursor.close()
        conn.close()
        if len(results) > 0:
            lists = [ClientPaymentPlan(**p) for p in results]
            return lists

    except Exception as ex:
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f' Erro ao consultar os planos de pagamentos dos clientes no banco semaforo: {str(ex)}', 'error', 'CLIENT_PAYMENT_PLAN')

    return []


def insert_update_semaphore_client_payment_plan(job_config_dict: dict, db_config: DatabaseConfig, lists: List[ClientPaymentPlan]) -> bool:
    """
    Insere os planos de pagamentos dos clientes no banco semáforo
    Args:
        job_config_dict: Configuração do job
        db_config: Configuracao do banco de dados
        lists: Lista dos planos de pagamentos dos clientes

    Returns:
        Boleano indicando se foram inseridos 1 ou mais registros
    """
    params = [(li.code_client, ' ', IntegrationType.PLANO_PAGAMENTO_CLIENTE.value) for li in lists]

    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()
    try:
        for p in params:
            cursor.execute(queries.get_insert_update_semaphore_command(db_config.db_type), queries.get_command_parameter(db_config.db_type, list(p)))
        cursor.close()
        conn.commit()
        conn.close()

        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False,
                 f'{cursor.rowcount} clientes dos planos de pagamento foram inseridos no semaforo', 'info',
                 'CLIENT_PAYMENT_PLAN')

        return cursor.rowcount > 0

    except Exception as ex:
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f' Erro ao consultar os planos de pagamentos dos clientes no banco semaforo: {str(ex)}', 'error', 'CLIENT_PAYMENT_PLAN')

    return False


def protocol_semaphore_client_payment_plan(job_config_dict: dict, db_config: DatabaseConfig, identifier: str) -> bool:
    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()
    try:
        if identifier is not None:
            cursor.execute(queries.get_protocol_semaphore_id_command(db_config.db_type), queries.get_command_parameter(db_config.db_type, [identifier]))
        count = cursor.rowcount
        cursor.close()
        conn.commit()
        conn.close()
        return count > 0

    except Exception as ex:
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f' Erro ao protocolar os planos de pagamentos no banco semaforo: {str(ex)}', 'error', 'CLIENT_PAYMENT_PLAN')
