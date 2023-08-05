import threading
from datetime import datetime
import logging
import src.database.connection as database
import src.database.utils as utils
from src.api.entities.lista_preco import ListaPreco, Escopo
from src.database.entities.price_list import DbPriceList, PriceListProduct
from src.database.queries import IntegrationType
from src.database.utils import DatabaseConfig
import src.api.okvendas as api_okvendas
from src.entities.price import Price
from src.database import queries
import src
import time
from typing import List, Dict, Tuple
from src.jobs.system_jobs import OnlineLogger
from threading import Lock

lock = Lock()
logger = logging.getLogger()
send_log = OnlineLogger.send_log


def job_insert_prices_semaphore(job_config_dict: dict):
    with lock:
        """
        Job para preços no banco semáforo
        Args:
            job_config_dict: Configuração do job
        """
        logger.info(job_config_dict.get('job_name') + f' | Executando na Thread {threading.current_thread()}')
        db_config = utils.get_database_config(job_config_dict)
        if db_config.sql is None:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Comando sql para inserir precos no semaforo nao encontrado', 'warning', 'PRECO')
        else:
            db = database.Connection(db_config)
            conn = db.get_conect()
            cursor = conn.cursor()

            try:
                send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Inserindo precos no banco semaforo', 'info', 'PRECO')
                logger.info(db_config.sql)
                cursor.execute(db_config.sql)
                send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'{cursor.rowcount} precos inseridos no banco semaforo', 'info', 'PRECO')
            except Exception as ex:
                send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Erro {str(ex)}', 'error', 'PRECO')

            cursor.close()
            conn.commit()
            conn.close()


def job_send_prices(job_config_dict: dict):
    with lock:
        """
        Job para realizar a atualização de preços
        Args:
            job_config_dict: Configuração do job
        """
        logger.info(job_config_dict.get('job_name') + f' | Executando na Thread {threading.current_thread()}')
        try:
            db_config = utils.get_database_config(job_config_dict)
            if db_config.sql is None:
                send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Comando sql para inserir precos no semaforo nao encontrado', 'warning', 'PRECO')
            else:
                prices = query_prices(job_config_dict, db_config)
                if prices is not None and len(prices) > 0:
                    send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Produtos para atualizar preco {len(prices)}', 'info', 'PRECO')

                    for price in prices:
                        try:
                            time.sleep(1)
                            response = api_okvendas.post_prices(src.client_data.get('url_api') + '/catalogo/preco', price, src.client_data.get('token_api'))
                            if response.status == 1 or response.status == "Success":
                                send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Protocolando preço do sku {price.codigo_erp}', 'info', 'PRECO')
                                protocol_price(db_config, price)
                            elif (response.status == 'Error' or response.status > 1) and response.message == "Erro ao atualizar o preço. Produto não existente":
                                send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False,
                                         f'Nao foi possivel atualizar o preco do sku {price.codigo_erp}. Erro recebido da Api: {response.message}', 'warning', 'PRECO')
                                protocol_price(db_config, price)
                            else:
                                send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,
                                         f'Nao foi possivel atualizar o preco do sku {price.codigo_erp}. Erro recebido da Api: {response.message}', 'warning', 'PRECO', price.codigo_erp)
                        except Exception as e:
                            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True, f'Falha ao atualizar preco do sku {price.codigo_erp}: {str(e)}', 'warning', 'PRECO', price.codigo_erp)
                else:
                    send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Nao existem precos a serem enviados no momento', 'warning', 'PRECO')
        except Exception as e:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Erro durante execucao do job: {str(e)}', 'error', 'PRECO')


def job_prices_list(job_config_dict: dict):
    with lock:
        """
            Job para integrar listas de preço com o okvendas
    
            Args:
                job_config_dict: Configuração do job
            """
        logger.info(job_config_dict.get('job_name') + f' | Executando na Thread {threading.current_thread()}')
        db_config = utils.get_database_config(job_config_dict)
        if db_config.sql is None:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Comando sql para listas de preco nao encontrado', 'warning', 'PRECO')
            return

        try:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Consultando listas de preco no banco semaforo', 'info', 'PRECO')
            duplicated_db_price_lists = query_price_lists(job_config_dict, db_config)

            # Carrega no dict todas as listas de preço agrupando pelo codigo da lista de preco e incrementando a lista de clientes
            unique_api_price_lists = dict.fromkeys(set([d.price_list_code for d in duplicated_db_price_lists]))
            unique_db_price_lists = dict.fromkeys(set([d.price_list_code for d in duplicated_db_price_lists]))
            for d in duplicated_db_price_lists:
                if unique_db_price_lists[d.price_list_code] is None:
                    unique_db_price_lists[d.price_list_code] = d

                if unique_api_price_lists[d.price_list_code] is None:
                    unique_api_price_lists[d.price_list_code] = ListaPreco(d.price_list_description, d.price_list_code, d.branch_code, d.initial_date, d.final_date,
                                                                           d.active, d.priority, Escopo(d.scope_type, [d.client_code]), d.calculate_ipi)
                else:
                    if not unique_api_price_lists[d.price_list_code].escopo.codigos_escopo.__contains__(d.client_code):
                        unique_api_price_lists[d.price_list_code].escopo.codigos_escopo.append(d.client_code)

            db_price_lists = list(unique_db_price_lists.values())
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Inserindo/atualizando listas de preco no banco semaforo', 'info', 'PRECO')
            if not insert_update_semaphore_price_lists(job_config_dict, db_config, db_price_lists):
                send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Nao foi possivel inserir as listas de preco no banco semaforo', 'error', 'PRECO')
                return

            api_price_lists: List[ListaPreco] = list(unique_api_price_lists.values())
            for api_price_list in api_price_lists:
                try:
                    response_list = api_okvendas.put_price_lists([api_price_list])
                    for res in response_list:
                        if res.status != 1:
                            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Erro ao processar lista de preco {api_price_list.codigo_lista_preco}: {res.message}', 'warning', 'PRECO')

                        if protocol_semaphore_item(job_config_dict, db_config, api_price_list.codigo_lista_preco, None):
                            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Lista de preco {api_price_list.codigo_lista_preco} protocolado no banco semaforo', 'info', 'PRECO')
                        else:
                            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Falha ao protocolar a lista de preco {api_price_list.codigo_lista_preco}', 'warning', 'PRECO')

                except Exception as e:
                    send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Falha no envio da lista de preco {api_price_list.codigo_lista_preco}: {str(e)}', 'error', 'PRECO')

        except Exception as ex:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Erro {str(ex)}', 'error', 'PRECO')


def job_products_prices_list(job_config_dict: dict):
    with lock:
        """
            Job para inserir a relação de produtos com as listas de preço no banco semáforo
    
            Args:
                job_config_dict: Configuração do job
            """
        logger.info(job_config_dict.get('job_name') + f' | Executando na Thread {threading.current_thread()}')
        db_config = utils.get_database_config(job_config_dict)
        if db_config.sql is None:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Comando sql para inserir a relação de produtos com as listas de preco no semaforo nao encontrado', 'warning', 'PRECO')
            return

        try:
            db_price_list_products = query_price_list_products(job_config_dict, db_config)

            if not insert_update_semaphore_price_lists_products(job_config_dict, db_config, db_price_list_products):
                send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Nao foi possivel inserir os produtos das listas de preco no banco semaforo', 'error', 'PRECO')
                return

            split_price_lists = dict.fromkeys(set([d.price_list_code for d in db_price_list_products]), [])
            for prod in db_price_list_products:
                split_price_lists[prod.price_list_code].append(PriceListProduct(prod.price_list_code, prod.erp_code, prod.price, prod.price_from, prod.other_price, prod.ipi))

            for k, v in split_price_lists.items():
                products_file = mount_price_list_products_file(v)
                if not api_okvendas.put_price_lists_products(k, products_file):
                    send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Erro ao processar lista de preco {k}', 'warning', 'PRECO')

                for prod in db_price_list_products:
                    if protocol_semaphore_item(job_config_dict, db_config, prod.price_list_code, prod.erp_code):
                        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Produto {prod.erp_code} da lista de preco {prod.price_list_code} protocolado no banco semaforo', 'info', 'PRECO')
                    else:
                        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Falha ao protocolar o produto {prod.erp_code} da lista de preco {prod.price_list_code}', 'warning', 'PRECO')

        except Exception as ex:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Erro {str(ex)}', 'error', 'PRECO')


def query_prices(job_config_dict: dict, db_config: DatabaseConfig) -> List[Price]:
    """
    Consulta os precos para atualizar no banco de dados
    Args:
        job_config_dict: Configuração do job
        db_config: Configuracao do banco de dados

    Returns:
        Lista de preços para atualizar
    """
    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()
    try:
        cursor.execute(db_config.sql)
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        results = list(dict(zip(columns, row)) for row in rows)
        cursor.close()
        conn.close()
        if len(results) > 0:
            prices = [Price(**p) for p in results]
            return prices

    except Exception as ex:
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f' Erro ao consultar precos no banco semaforo: {str(ex)}', 'error', 'PRECO')

    return []


def protocol_price(db_config: DatabaseConfig, price: Price) -> None:
    """
    Protocola os preços no banco semáforo
    Args:
        db_config: Configuração do banco de dados
        price: Lista de skus para protocolar
    """
    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()
    sql = queries.get_price_protocol_command(db_config.db_type)
    try:
        cursor.execute(sql, queries.get_command_parameter(db_config.db_type, [price.codigo_erp, price.preco_atual]))
    except Exception as e:
        raise Exception(f'Erro ao protocolar preco do sku no banco semaforo {price.codigo_erp}: {str(e)}')

    cursor.close()
    conn.commit()
    conn.close()


def query_price_lists(job_config_dict: dict, db_config: DatabaseConfig) -> List[DbPriceList]:
    """
    Consulta os listas de precos para consultar no banco de dados
    Args:
        job_config_dict: Configuração do job
        db_config: Configuracao do banco de dados

    Returns:
        Lista de preços para atualizar
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
            # print(results)
            lists = [DbPriceList(**p) for p in results]
            return lists

    except Exception as ex:
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f' Erro ao consultar listas de precos: {str(ex)}', 'error', 'PRECO')

    return []


def insert_update_semaphore_price_lists(job_config_dict: dict, db_config: DatabaseConfig, lists: List[DbPriceList]) -> bool:
    """
    Consulta os listas de precos para consultar no banco de dados
    Args:
        job_config_dict: Configuração do job
        db_config: Configuracao do banco de dados
        lists: Lista de listas de preço

    Returns:
        Boleano indicando se foram inseridos 1 ou mais registros
    """
    params = [(li.price_list_code, ' ', IntegrationType.LISTA_PRECO.value) for li in lists]

    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()
    try:
        for p in params:
            cursor.execute(queries.get_insert_update_semaphore_command(db_config.db_type), queries.get_command_parameter(db_config.db_type, list(p)))
        cursor.close()
        conn.commit()
        conn.close()
        return cursor.rowcount > 0

    except Exception as ex:
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f' Erro ao consultar listas de precos no banco semaforo: {str(ex)}', 'error', 'PRECO')

    return False


def insert_update_semaphore_price_lists_products(job_config_dict: dict, db_config: DatabaseConfig, lists: List[PriceListProduct]) -> bool:
    """
    Consulta os listas de precos para consultar no banco de dados
    Args:
        job_config_dict: Configuração do job
        db_config: Configuracao do banco de dados
        lists: Lista de produtos de um(as) listas de preço

    Returns:
        Boleano indicando se foram inseridos 1 ou mais registros
    """
    params = [(li.price_list_code, li.erp_code, IntegrationType.LISTA_PRECO_PRODUTO.value) for li in lists]

    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()
    try:
        for p in params:
            cursor.execute(queries.get_insert_update_semaphore_command(db_config.db_type), queries.get_command_parameter(db_config.db_type, list(p)))
        cursor.close()
        conn.commit()
        conn.close()
        return cursor.rowcount > 0

    except Exception as ex:
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f' Erro ao consultar listas de precos no banco semaforo: {str(ex)}', 'error', 'PRECO')

    return False


def query_price_list_products(job_config_dict: dict, db_config: DatabaseConfig) -> List[PriceListProduct]:
    """
        Consultar no banco semáforo a lista de produtos relacionados a lista de preço

        Args:
            job_config_dict: Configuração do job
            db_config: Configuração do banco de dados

        Returns:
        Lista de produtos relacionados a lista de preço informada
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
            lists = [PriceListProduct(**p) for p in results]
            return lists

    except Exception as ex:
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f' Erro ao consultar produtos da lista de preco no banco semaforo: {str(ex)}', 'error', 'PRECO')

    return []


def mount_price_list_products_file(products: List[PriceListProduct]) -> str:
    file: str = ''
    for p in products:
        file += f'{p.price_list_code},{p.erp_code},{p.price},{p.price_from},{p.other_price},{p.ipi}\n'

    return file


def protocol_semaphore_item(job_config_dict: dict, db_config: DatabaseConfig, identifier: str, identifier2: str) -> bool:
    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()
    try:
        if identifier2 is None:
            cursor.execute(queries.get_protocol_semaphore_id_command(db_config.db_type), queries.get_command_parameter(db_config.db_type, [identifier]))
        else:
            cursor.execute(queries.get_protocol_semaphore_id2_command(db_config.db_type), queries.get_command_parameter(db_config.db_type, [identifier, identifier2]))
        count = cursor.rowcount
        cursor.close()
        conn.commit()
        conn.close()
        return count > 0

    except Exception as ex:
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f' Erro ao protocolar item no banco semaforo: {str(ex)}', 'error', 'PRECO')


