import csv
import logging
import threading
from typing import List
import src
import src.database.connection as database
import pandas as pd
from src.api.entities.imposto_produto import ImpostoProduto
from src.database import queries
from src.database.queries import IntegrationType
from src.database.utils import DatabaseConfig
import src.database.utils as utils
from src.entities.product import Product
from src.entities.photos_sku import PhotosSku
import src.api.okvendas as api_okvendas
from src.jobs.system_jobs import OnlineLogger
from src.database.entities.product_tax import ProductTax
from threading import Lock

lock = Lock()
logger = logging.getLogger()
send_log = OnlineLogger.send_log


def job_update_products_semaphore(job_config_dict: dict):
    with lock:
        logger.info(job_config_dict.get('job_name') + f' | Executando na Thread {threading.current_thread()}')
        try:
            db_config = utils.get_database_config(job_config_dict)
            if db_config.sql is None:
                send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Comando sql para criar produtos nao encontrado', 'warning', 'PRODUTO')
                return

            db = database.Connection(db_config)
            connection = db.get_conect()
            cursor = connection.cursor()

            cursor.execute(db_config.sql)
            cursor.close()

            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Produtos marcados para atualizar no banco semaforo: {cursor.rowcount}', 'info', 'PRODUTO')
            connection.commit()
            connection.close()

        except Exception as e:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Erro ao atualizar produtos no banco semaforo: {str(e)}', 'error', 'PRODUTO')


def job_insert_products_semaphore(job_config_dict: dict):
    with lock:
        """
        Job que realiza a insercao dos produtos no banco semaforo
        Args:
            job_config_dict: Dicionario contendo configuracoes do job (obtidos na api oking)
        """
        logger.info(job_config_dict.get('job_name') + f' | Executando na Thread {threading.current_thread()}')
        try:
            db_config = utils.get_database_config(job_config_dict)
            if db_config.sql is None:
                send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Comando sql para inserir produtos no semaforo nao encontrado', 'warning', 'PRODUTO')
                return

            # abre a connection com o banco
            db = database.Connection(db_config)
            connection = db.get_conect()
            cursor = connection.cursor()

            try:
                # sql: str = db_config.sql
                # if db_config.sql[len(db_config.sql) - 1] is ';':
                #     sql = db_config.sql[len(db_config.sql) - 1] = ' '

                send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Inserindo produtos no banco semáforo', 'info', 'PRODUTO')
                cursor.execute(db_config.sql)
                connection.commit()
                send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'{cursor.rowcount} produtos inseridos no banco semáforo', 'info', 'PRODUTO')
            except Exception as e:
                send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True, f'Erro ao inserir produtos no banco semaforo: {str(e)}', 'error', 'PRODUTO')
                cursor.close()
                connection.close()

            cursor.close()
            connection.close()
        except Exception as e:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True, f'Erro ao durante a execucao do job: {str(e)}', 'error', 'PRODUTO')


def job_send_products(job_config_dict: dict):
    with lock:
        """
        Job que realiza a leitura dos produtos contidos no banco semaforo e envia para a api okvendas
        Args:
            job_config_dict: Dicionario contendo configuracoes do job (obtidos na api oking)
        """
        logger.info(job_config_dict.get('job_name') + f' | Executando na Thread {threading.current_thread()}')
        try:
            db_config = utils.get_database_config(job_config_dict)
            if db_config.sql is None:
                send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Comando sql para criar produtos nao encontrado', 'warning', 'PRODUTO')
                return

            produtos_repetidos = query_products(db_config)

            keys_photos_sent = {}
            photos_sku = mount_list_photos(produtos_repetidos)
            produtos = remove_repeat_products(produtos_repetidos)

            if len(produtos) <= 0:
                send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Nao existem produtos para criar no momento', 'warning', 'PRODUTO')
                return

            for prod in produtos:
                try:
                    response = api_okvendas.post_produtos([prod])
                    if src.print_payloads:
                        print(response)

                    if response is not None and len(response) > 0:
                        for res in response:
                            if res.status > 1:
                                send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False,
                                         f'Erro ao gerar produto {res.codigo_erp} na api okvendas. Erro gerado na api: {res.message}', 'warning', 'PRODUTO')
                            else:
                                send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Produto {res.codigo_erp} criado com sucesso', 'info', 'PRODUTO')
                                if src.print_payloads:
                                    print(f'prod.codigo_erp = {prod.codigo_erp}, prod.preco_estoque[0].codigo_erp_atributo = {prod.preco_estoque[0].codigo_erp_atributo} ')
                                protocol_products(job_config_dict, [prod], db_config)

                                keys_photos_sent[(prod.codigo_erp, prod.preco_estoque[0].codigo_erp_atributo)] = ""

                    else:
                        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True, f'Erro no envio do produto codigo_erp: {prod.codigo_erp} codigo_referencia: {prod.codigo_referencia} Exceção: {str(e)}', 'error', 'PRODUTO')

                except Exception as e:
                    send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True, f'Erro durante o envio de produtos: {str(e)}', 'error', 'PRODUTO')

            if send_photos_products(photos_sku, keys_photos_sent, 50):
                logger.info(job_config_dict.get('job_name') + f' | Fotos dos produtos cadastradas com sucesso')
            else:
                print(" Erro ao cadastrar as fotos do produto")
                logger.error(job_config_dict.get('job_name') + f' | Erro durante o cadastro das fotos dos produtos')

        except Exception as e:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Erro durante a execucao do job: {str(e)}', 'error', 'PRODUTO')


def query_products(db_config: DatabaseConfig):
    """
    Consulta os produtos contidos no banco semaforo juntamente com os dados do banco do ERP
    Args:
        db_config: Configuracao do banco de dados

    Returns:
        Lista de produtos
    """
    # abre a connection com o banco
    db = database.Connection(db_config)
    connection = db.get_conect()
    # connection.start_transaction()
    cursor = connection.cursor()

    # obtem os dados do banco
    # logger.warning(query)
    cursor.execute(db_config.sql)
    columns = [col[0] for col in cursor.description]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    cursor.close()
    connection.close()

    produtos = []
    for result in results:
        produtos.append(Product(result))

    return produtos


def protocol_products(job_config_dict: dict, products: list, db_config: DatabaseConfig) -> None:
    """
    Protocola no banco semaforo os produtos que foram enviados para a api okvendas
    Args:
        job_config_dict: Configuração do job
        products: Lista de produtos enviados para a api okvendas
        db_config: Configuracao do banco de dados
    """
    try:
        if len(products) > 0:
            db = database.Connection(db_config)
            connection = db.get_conect()
            cursor = connection.cursor()
            for prod in products:
                try:
                    dados_produto = [prod.codigo_erp, prod.preco_estoque[0].codigo_erp_atributo]
                    send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Protocolando codigo_erp {dados_produto[0]} sku {dados_produto[1]}', 'info', 'PRODUTO')
                    cursor.execute(queries.get_product_protocol_command(db_config.db_type), queries.get_command_parameter(db_config.db_type, dados_produto))
                    send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Linhas afetadas {cursor.rowcount}', 'info', 'PRODUTO')
                except Exception as e:
                    send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Erro ao protocolar produto {prod.codigo_erp}: {str(e)}', 'error', 'PRODUTO')
            cursor.close()
            connection.commit()
            connection.close()
    except Exception as e:
        raise e


def mount_list_photos(products: List[Product]):
    photos = {}

    for product in products:
        # Grouping by codigo_erp and codigo_erp_variacao
        codigo_erp = product.codigo_erp
        codigo_erp_variacao = product.preco_estoque[0].codigo_erp_atributo

        key = (codigo_erp, codigo_erp_variacao)

        if key in photos:

            length_photos = len(photos[key])

            if contains_photo(photos[key], product.imagem_base64):
                continue
            else:
                order_photo = length_photos + 1
                photo_sku = PhotosSku(product.imagem_base64, codigo_erp, f'{codigo_erp}_{order_photo}', order_photo,
                                      False)
                photos[key].append(photo_sku)

        else:
            # Mount photo
            photo_sku = PhotosSku(product.imagem_base64, codigo_erp, f'{codigo_erp}_{1}', 1,
                                  True)

            photos[key] = [photo_sku]

    return photos


def remove_repeat_products(products: List[Product]):
    product_keys = {}
    result_products = []

    for product in products:
        # Grouping by codigo_erp and codigo_erp_variacao
        codigo_erp = product.codigo_erp
        codigo_erp_variacao = product.preco_estoque[0].codigo_erp_atributo

        key = (codigo_erp, codigo_erp_variacao)

        if key in product_keys:
            continue
        else:
            product_keys[key] = ""
            result_products.append(product)

    return result_products


def send_photos_products(photos_sku: dict, keys_photos_sent: dict, limit_photos_sent: int):
    count_success = 0
    list_photos = []
    for photo_key in photos_sku:

        if photo_key in keys_photos_sent:
            list_photo = photos_sku[photo_key]

            for photo in list_photo:
                if (len(list_photos) + 1) <= limit_photos_sent:
                    list_photos.append(photo)

                if len(list_photos) == limit_photos_sent:
                    success = api_okvendas.put_photos_sku(list_photos)
                    if not success:
                        return success
                    else:
                        count_success = count_success + 1
                        list_photos = []

    if 0 < len(list_photos) <= 50:
        return api_okvendas.put_photos_sku(list_photos)

    return count_success > 0 if True else False


def contains_photo(photos: List[PhotosSku], imagem_base64: str):
    for photo in photos:
        if photo.base64_foto == imagem_base64:
            return True
    return False


def job_product_tax(job_config_dict: dict):
    with lock:
        """
        Job para inserir o imposto do produto com as listas de imposto no banco semáforo
        Args:
            job_config_dict: Configuração do job
        """
        logger.info(job_config_dict.get('job_name') + f' | Executando na Thread {threading.current_thread()}')
        db_config = utils.get_database_config(job_config_dict)
        if db_config.sql is None:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Comando sql para inserir a relação de imposto de produtos no semaforo nao encontrado', 'warning', 'IMPOSTO')
            return

        try:
            db_product_tax = query_list_products_tax(job_config_dict, db_config)
            if not insert_update_semaphore_product_tax(job_config_dict, db_config, db_product_tax):
                send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True, f'Nao foi possivel inserir os impostos de produtos no banco semaforo', 'error', 'IMPOSTO')
                return

            api_productstax = []
            for prod in db_product_tax:
                api_productstax.append(ImpostoProduto(
                    prod.sku_code
                    , prod.ncm
                    , prod.taxation_group
                    , prod.customer_group
                    , prod.origin_uf
                    , prod.destination_uf
                    , prod.mva_iva
                    , prod.intrastate_icms
                    , prod.interstate_icms
                    , prod.percentage_reduction_base_calculation
                    , prod.identifier
                ))

            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Enviando impostos via api okvendas', 'info', 'IMPOSTO')
            total = len(api_productstax)
            page = 100
            limit = 100 if total > 100 else total
            offset = 0

            partial_taxes = api_productstax[offset:limit]
            while limit <= total:
                response = api_okvendas.post_product_tax(partial_taxes)

                for res in response:
                    identificador = [i.identificador for i in api_productstax if i.identificador == res.identifiers[0]][0]
                    if res.status == 1:
                        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,f'Imposto Cadastrado/Atualizado com sucesso - Identificador: {identificador}','warning', 'IMPOSTO')
                        if protocol_semaphore_product_tax(job_config_dict, db_config, identificador):
                            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Imposto de Produtos {identificador} protocolado no banco semaforo', 'info', 'IMPOSTO')
                        else:
                            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Falha ao protocolar o imposto do produto {identificador}', 'warning', 'IMPOSTO')

                limit = limit + page
                offset = offset + page
                partial_taxes = api_productstax[offset:limit]

        except Exception as ex:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True, f'Erro {str(ex)}', 'error', 'IMPOSTO')

def job_product_tax_full(job_config_dict: dict):
    with lock:
        """
        Job para inserir os impostos dos produtos em lote no banco semáforo
        Args:
            job_config_dict: Configuração do job
        """
        logger.info(job_config_dict.get('job_name') + f' | Executando na Thread {threading.current_thread()}')
        db_config = utils.get_database_config(job_config_dict)
        if db_config.sql is None:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Comando sql para inserir a relação de impostos dos produtos em lote no semaforo nao encontrado', 'warning', 'IMPOSTO_LOTE')
            return

        try:
            db_product_tax = query_list_products_tax(job_config_dict, db_config)
            if not insert_update_semaphore_product_tax(job_config_dict, db_config, db_product_tax):
                send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True, f'Nao foi possivel inserir os impostos dos produtos em lote no banco semaforo', 'error', 'IMPOSTO_LOTE')
                return

            # Define a lista de dicionários para construir o DataFrame
            data = []
            for product_tax in db_product_tax:
                data.append({
                    'codigo_sku': product_tax.sku_code,
                    'ncm': product_tax.ncm,
                    'grupo_tributacao': product_tax.taxation_group,
                    'grupo_cliente': product_tax.customer_group,
                    'uf_origem': product_tax.origin_uf,
                    'uf_destino': product_tax.destination_uf,
                    'mva_iva': None if product_tax.mva_iva is None else round(product_tax.mva_iva, 2), #arredonda para 2 casas decimais
                    'icms_intraestadual': None if product_tax.intrastate_icms is None else round(product_tax.intrastate_icms, 2), #arredonda para 2 casas decimais
                    'icms_interestadual': product_tax.interstate_icms,
                    'percentual_reducao_base_calculo': None if product_tax.percentage_reduction_base_calculation is None else round(product_tax.percentage_reduction_base_calculation, 2) #arredonda para 4 casas decimais
                    # arredonda para 4 casas decimais
                })

            # Cria um DataFrame a partir da lista de dicionários
            df = pd.DataFrame(data)

            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Enviando impostos em lote via api okvendas', 'info', 'IMPOSTO_LOTE')
            response = api_okvendas.post_product_full_tax(df)

            if response['Status'] == 1:
                send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,f'Impostos em lote Cadastrados/Atualizados com sucesso na Api OkVendas','warning', 'IMPOSTO_LOTE')
                if protocol_semaphore_product_tax_full(job_config_dict, db_config, db_product_tax):
                    send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Impostos em lote protocolados com sucesso no banco semaforo', 'info', 'IMPOSTO_LOTE')
                else:
                    send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Falha ao protocolar os impostos dos produtos em lote no banco semaforo', 'warning', 'IMPOSTO_LOTE')
            else:
                send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False,
                         f'Falha ao Cadastrar/Atualizar os Impostos dos produtos em lote na Api OkVendas', 'warning', 'IMPOSTO_LOTE')

        except Exception as ex:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True, f'Erro {str(ex)}', 'error', 'IMPOSTO_LOTE')

def query_list_products_tax(job_config_dict: dict, db_config: DatabaseConfig) -> List[ProductTax]:
    """
        Consultar no banco semáforo a lista de produtos relacionados a lista de preço

        Args:
            job_config_dict: Configuração do job
            db_config: Configuração do banco de dados

        Returns:
        Lista de produtos relacionados ao imposto informada
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
            lists = [ProductTax(**p) for p in results]
            return lists

    except Exception as ex:
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f' Erro ao consultar imposto do produto no banco semaforo: {str(ex)}', 'error', 'IMPOSTO')

    return []


def insert_update_semaphore_product_tax(job_config_dict: dict, db_config: DatabaseConfig, lists: List[ProductTax]) -> bool:
    """
    Insere os imposts no banco semáforo
    Args:
        job_config_dict: Configuração do job
        db_config: Configuracao do banco de dados
        lists: Lista de impostos dos produtos

    Returns:
        Boleano indicando se foram inseridos 1 ou mais registros
    """
    params = [(li.identifier, ' ', IntegrationType.IMPOSTO.value) for li in lists]

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
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f' Erro ao consultar listas de impostos no banco semaforo: {str(ex)}', 'error', 'IMPOSTO')

    return False

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
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f' Erro ao protocolar item no banco semaforo: {str(ex)}', 'error', 'IMPOSTO')


def protocol_semaphore_product_tax(job_config_dict: dict, db_config: DatabaseConfig, identifier: str) -> bool:
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
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f' Erro ao protocolar imposto do produto no banco semaforo: {str(ex)}', 'error', 'IMPOSTO')

def protocol_semaphore_product_tax_full(job_config_dict: dict, db_config: DatabaseConfig, lists: List[ProductTax]) -> bool:
    """
    protocola os impostos em lote no banco semáforo
    Args:
        job_config_dict: Configuração do job
        db_config: Configuracao do banco de dados
        lists: Lista de impostos dos produtos

    Returns:
        Boleano indicando se foram inseridos 1 ou mais registros
    """
    params = [(li.identifier, IntegrationType.IMPOSTO.value) for li in lists]

    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()
    try:
        for p in params:
            cursor.execute(queries.get_protocol_semaphore_id3_command(db_config.db_type), queries.get_command_parameter(db_config.db_type, list(p)))
        cursor.close()
        conn.commit()
        conn.close()
        return cursor.rowcount > 0

    except Exception as ex:
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f' Erro ao protocolar as listas de impostos em lote no banco semaforo: {str(ex)}', 'error', 'IMPOSTO_LOTE')

    return False

# job_product_tax
