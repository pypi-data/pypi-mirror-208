import logging
import threading
import time

import src.database.connection as database
import src.database.utils as utils
from src.jobs.client_payment_plan_jobs import query_list_client_payment_plan, insert_update_semaphore_client_payment_plan
from src.jobs.system_jobs import OnlineLogger
from threading import Lock

lock = Lock()
logger = logging.getLogger()
send_log = OnlineLogger.send_log
CLIENT_PAYMENT_PLAN = 'CLIENT_PAYMENT_PLAN'


def job_insert_client_no_exists_payment_plan_semaphore(job_config_dict: dict):
    with lock:
        """
        Job para inserir os clientes dos planos de pagamento que não existem no banco semáforo
        Args:
            job_config_dict: Configuração do job
        """
        logger.info(job_config_dict.get('job_name') + f' | Executando na Thread {threading.current_thread()}')
        db_config = utils.get_database_config(job_config_dict)
        if db_config.sql is None:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False,
                     'Comando sql para inserir os clientes dos planos de pagamento que não existem no banco semáforo nao foi encontrado', 'warning', CLIENT_PAYMENT_PLAN)
        else:
            db = database.Connection(db_config)
            conn = db.get_conect()
            cursor = conn.cursor()

            try:

                db_client_payment_plan = query_list_client_payment_plan(job_config_dict, db_config)

                if len(db_client_payment_plan) <= 0:
                    send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,
                             f'Não existem registros de clientes novos com planos de pagamento do lado do ERP, que não estejam cadastrados no banco semaforo \n {db_config.sql}', 'info', CLIENT_PAYMENT_PLAN)

                    return

                send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False,
                         f'Inserindo clientes novos dos planos de pagamento do ERP, que ainda não existem no banco semaforo \n {db_config.sql}', 'info', CLIENT_PAYMENT_PLAN)

                if not insert_update_semaphore_client_payment_plan(job_config_dict, db_config, db_client_payment_plan):
                    send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True, f'Nao foi possivel inserir os planos de pagamentos dos clientes novos no banco semaforo', 'error', 'CLIENT_PAYMENT_PLAN')
                    return

            except Exception as ex:
                send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,
                         f'Erro ao inserir os clientes novos dos planos de pagamento, que ainda não existem no banco semaforo {str(ex)}', 'error', CLIENT_PAYMENT_PLAN)

            cursor.close()
            conn.commit()
            conn.close()
