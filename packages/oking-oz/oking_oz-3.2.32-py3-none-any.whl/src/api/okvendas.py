import csv
import json
import logging
from io import StringIO
from typing import Optional, List
import jsonpickle
import pandas as pd
import requests
import src
from src.api.entities.cliente import Cliente
from src.api.entities.cliente_aprovado import ApprovedClientResponse
from src.api.entities.cliente_erp_code import ClienteErpCode
from src.api.entities.imposto_produto import ImpostoProduto
from src.api.entities.lista_preco import ListaPreco, ListaPrecoResponse
from src.database.entities.product_tax import ProductTax
from src.entities.invoice import Invoice
from src.entities.log import Log
from src.entities.order import Queue, Order
from src.entities.orderb2b import OrderB2B
from src.entities.orderb2c import OrderB2C
from src.entities.price import Price
from src.entities.response import CatalogoResponse, PriceResponse, InvoiceResponse, TrackingResponse, StockResponse, \
    ClientResponse, ProductTaxResponse, ClientPaymentPlanResponse
from src.entities.tracking import Tracking
from src.entities.photos_sku import PhotosSku
from src.api.entities.representante import Representante, RegiaoVenda
from src.database.entities.representative import Representative
from src.api.entities.plano_pagamento_cliente import PlanoPagamentoCliente
from src.database.entities.client_payment_plan import ClientPaymentPlan


logger = logging.getLogger()


def obj_dict(obj):
    return obj.__dict__


def object_list_to_dict(obj_list: list):
    lista = []
    for obj in obj_list:
        lista.append(obj.toJSON())
    return lista


def post_produtos(produtos: list):
    try:
        url = f'{src.client_data.get("url_api")}/catalogo/produtos'

        json_produtos = jsonpickle.encode(produtos, unpicklable=False)
        if src.print_payloads:
            print(json_produtos)
        response = requests.post(url, json=json.loads(json_produtos), headers={
            'Content-type': 'application/json',
            'Accept': 'text/html',
            'access-token': src.client_data.get('token_api')})

        obj = jsonpickle.decode(response.content)
        result = []
        if 200 <= response.status_code <= 299:
            for res in obj:
                result.append(CatalogoResponse(**res))
        else:
            if type(obj) is list:
                for res in obj:
                    result.append(CatalogoResponse(**res))
            else:
                result.append(CatalogoResponse(**obj))

        return result
    except Exception as e:
        logger.error(f'Erro ao enviar produto para api okvendas {e}', exc_info=True)


def send_stocks(url, body, token):
    logger.debug("POST: {}".format(url))
    try:
        # auth = HTTPBasicAuth('teste@example.com', 'real_password')
        headers = {'Content-type': 'application/json',
                   'Accept': 'text/html',
                   'access-token': token}

        json_stock = jsonpickle.encode(body, unpicklable=False)
        if src.print_payloads:
            print(json_stock)
        response = requests.put(url, json=json.loads(json_stock), headers=headers)

        if response.ok:
            return response.json(), response.status_code
        else:
            if response.content is not None and response.content != '':
                return response.json(), response.status_code

    except Exception as ex:
        logger.error(str(ex))
        return None, response.status_code


def send_stocks_ud(url, body, token) -> List[StockResponse]:
    logger.debug(f"POST: {url}")
    try:
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'access-token': token
        }

        json_stock = jsonpickle.encode(body, unpicklable=False)
        if src.print_payloads:
            print(json_stock)
        response = requests.post(url, json=json.loads(json_stock), headers=headers)
        return [StockResponse(**c) for c in jsonpickle.decode(response.content)]

    except Exception as e:
        return [StockResponse([body[0].codigo_erp], "-1", str(e), None)]


def post_prices(url, price: Price, token) -> PriceResponse:
    try:
        headers = {'Content-type': 'application/json',
                   'Accept': 'text/html',
                   'access-token': token}

        json_prices = jsonpickle.encode(price, unpicklable=False)
        if src.print_payloads:
            print(json_prices)
        response = requests.put(url, json=json.loads(json_prices), headers=headers)

        obj = jsonpickle.decode(response.content)
        return PriceResponse(**obj)

    except Exception as ex:
        logger.error(str(ex))
        return PriceResponse([price.codigo_erp], 3, str(ex), '', '')


def get_order_queue(url: str, token: str, status: str, limit: int) -> List[Queue]:
    queue = []
    try:
        response = requests.get(url.format(status), headers={'Accept': 'application/json', 'access-token': token},
                                params={'limit': limit})
        if response.ok:
            obj = jsonpickle.decode(response.content)
            for o in obj['fila']:
                queue.append(Queue(**o))
        else:
            logger.warning(f'Retorno sem sucesso {response.status_code} - {response.url}')
    except Exception as ex:
        logger.error(f'Erro ao realizar GET na api okvendas {url}' + str(ex), exc_info=True)

    return queue


def get_order(url: str, token: str, order_id: int) -> Order:
    order = None
    try:
        response = requests.get(url.format(order_id), headers={'Accept': 'application/json', 'access-token': token})
        if response.ok:
            obj = jsonpickle.decode(response.content)
            order = Order(**obj)
        else:
            logger.warning(f'Retorno sem sucesso {response.status_code} - {response.url}')
    except Exception as ex:
        logger.error(f'Erro ao realizar GET na api okvendas {url} - {str(ex)}')
        raise

    return order


def get_order_b2c(url: str, token: str, order_id: int) -> OrderB2C:
    order = None
    try:
        response = requests.get(url.format(order_id), headers={'Accept': 'application/json', 'access-token': token})
        if response.ok:
            obj = jsonpickle.decode(response.content)
            order = OrderB2C(**obj)
        else:
            logger.warning(f'Retorno sem sucesso {response.status_code} - {response.url}')
    except Exception as ex:
        logger.error(f'Erro ao realizar GET na api okvendas {url} - {str(ex)}')
        raise

    return order


def get_order_b2b(url: str, token: str, order_id: int) -> OrderB2B:
    order = None
    try:
        response = requests.get(url.format(order_id), headers={'Accept': 'application/json', 'access-token': token})
        if response.ok:
            obj = jsonpickle.decode(response.content)
            order = OrderB2B(**obj)
        else:
            logger.warning(f'Retorno sem sucesso {response.status_code} - {response.url}')
    except Exception as ex:
        logger.error(f'Erro ao realizar GET na api okvendas {url} - {str(ex)}')
        raise

    return order


def put_order_erp_code(url: str, token: str, order_id: int, order_erp_id: str) -> bool:
    try:
        response = requests.put(url, headers={'Accept': 'application/json', 'access-token': token},
                                params={'id': order_id, 'codigo_erp': order_erp_id})
        if response.ok:
            return True
        else:
            logger.warning(f'Retorno sem sucesso {response.status_code} - {response.url}')
            return False
    except Exception as ex:
        logger.error(f'Erro ao realizar GET na api okvendas {url}' + str(ex), exc_info=True)
        return False


def put_client_erp_code(body: ClienteErpCode) -> bool:
    try:
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'access-token': src.client_data.get('token_api')
        }

        json_client_erp_code = jsonpickle.encode(body, unpicklable=False)
        if src.print_payloads:
            print(json_client_erp_code)

        response = requests.put(src.client_data.get('url_api') + '/cliente/codigo',
                                headers=headers,
                                json=json.loads(json_client_erp_code))

        if response.ok:
            return True
        else:
            logger.warning(f'Retorno sem sucesso {response.status_code} - {response.url}')
            return False
    except Exception as ex:
        logger.error(f'Erro ao realizar GET na api okvendas {src.client_data.get("url_api")}/cliente/codigo' + str(ex), exc_info=True)
        return False


def put_protocol_orders(protocolos: List[str]) -> bool:
    url = src.client_data.get('url_api') + f'/pedido/fila'
    try:
        json_protocolos = jsonpickle.encode(protocolos)
        if src.print_payloads:
            print(json_protocolos)
        response = requests.put(url, json=json.loads(json_protocolos), headers={'Accept': 'application/json',
                                                                                'access-token': src.client_data.get(
                                                                                    'token_api')})
        if response.ok:
            return True
        else:
            logger.warning(f'Retorno sem sucesso {response.status_code} - {response.url}')
            return False
    except Exception as ex:
        logger.error(f'Erro ao protocolar pedidos na api okvendas {url}' + str(ex), exc_info=True)
        return False


def post_invoices(url: str, invoice: Invoice, token) -> Optional[InvoiceResponse]:
    """
    Enviar NF de um pedido para api okvendas
    Args:
        url: Url da api okvendas
        invoice: Objeto com os dados da NF
        token: Token de acesso da api okvendas

    Returns:
    None se o envio for sucesso. Caso falhe, um objeto contendo status e descrição do erro
    """
    try:
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json',
                   'access-token': token}

        json_invoice = jsonpickle.encode(invoice, unpicklable=False)
        if src.print_payloads:
            print(json_invoice)
        response = requests.post(url, json=json.loads(json_invoice), headers=headers)
        if response.ok:
            return None
        else:
            err = jsonpickle.decode(str(response.text))
            invoice_response = InvoiceResponse(**err)
            if '_okvendas' in invoice_response.message or '_openkuget' in invoice_response.message:
                invoice_response.message = 'Erro interno no servidor. Entre em contato com o suporte'
            return invoice_response

    except Exception as ex:
        return InvoiceResponse(3, str(ex))


def post_tracking(url: str, tracking: Tracking, token) -> Optional[TrackingResponse]:
    """
    Enviar rastreio de um pedido para api okvendas
    Args:
        url: Url da api okvendas
        tracking: Objeto com os dados do rastreio
        token: Token de acesso da api okvendas

    Returns:
    None se o envio for sucesso. Caso falhe, um objeto contendo status e descrição do erro
    """
    try:
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json',
                   'access-token': token}

        json_tracking = jsonpickle.encode(tracking, unpicklable=False)
        if src.print_payloads:
            print(json_tracking)
        response = requests.post(url, json=json.loads(json_tracking), headers=headers)
        if response.ok:
            return None
        else:
            err = jsonpickle.decode(str(response.text))
            tracking_response = TrackingResponse(**err)
            if '_okvendas' in tracking_response.message or '_openkuget' in tracking_response.message:
                tracking_response.message = 'Erro interno no servidor. Entre em contato com o suporte'
            return tracking_response

    except Exception as ex:
        return TrackingResponse(3, str(ex))


def post_log(log: Log) -> bool:
    try:
        if not src.is_dev:
            url = f'{src.client_data.get("url_api")}/log/logIntegracao'
            headers = {
                'Content-type': 'application/json',
                'Accept': 'application/json',
                'access-token': src.client_data.get('token_api')
            }

            json_log = jsonpickle.encode([log], unpicklable=False)
            if src.print_payloads:
                print(json_log)
            response = requests.post(url, json=json.loads(json_log), headers=headers)
            if response.ok:
                return True

            return False
        else:
            return True
    except Exception:
        return False


def post_clients(clients: List[Cliente]) -> List[ClientResponse]:
    url = f'{src.client_data.get("url_api")}/cliente/clientes'
    headers = {
        'Content-type': 'application/json',
        'Accept': 'application/json',
        'access-token': src.client_data.get('token_api')
    }

    try:
        payload = jsonpickle.encode(clients, unpicklable=False)
        if src.print_payloads:
            print(payload)
        response = requests.put(url, json=json.loads(payload), headers=headers)
        results = jsonpickle.decode(response.text)
        return [ClientResponse(**r) for r in results]

    except Exception as e:
        return [ClientResponse([c.cpf or c.cnpj for c in clients], 3, str(e))]


def put_photos_sku(body: List[PhotosSku]):
    """
        Cadastra Fotos do SKU
        Podem ser enviadas até 50 fotos por vez.
        Args:
            url: Url da api okvendas
            token: Token de acesso da api okvendas
            photosProduto: Objeto com os dados das Fotos
        Returns:
        True se foi atualizado com Sucesso. False se não foi atualizado
    """
    try:
        url = f'{src.client_data.get("url_api")}/v2/catalogo/fotos/sku'

        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json',
                   'access-token': src.client_data.get('token_api')}

        json_photos = jsonpickle.encode(body, unpicklable=False)
        logger.info(f'{url} - {json_photos}')
        if src.print_payloads:
            print(json_photos)
        response = requests.put(url,
                                headers=headers,
                                json=json.loads(json_photos))
        if response.ok:
            return True
        else:
            logger.warning(f'Retorno sem sucesso {response.status_code} - {response.url}')
            return False
    except Exception as ex:
        logger.error(f'Erro ao realizar PUT /v2/catalogo/fotos/sku na api okvendas {url}' + str(ex), exc_info=True)
        return False


def put_price_lists(body: List[ListaPreco]) -> List[ListaPrecoResponse]:
    try:
        url = f'{src.client_data.get("url_api")}/catalogo/listapreco'
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json',
                   'access-token': src.client_data.get('token_api')}
        json_body = jsonpickle.encode(body, unpicklable=False)
        if src.print_payloads:
            print(json_body)
        response = requests.put(url, headers=headers, json=json.loads(json_body))
        if response.ok:
            res = jsonpickle.decode(response.content)
            return [ListaPrecoResponse(**r) for r in res]
        else:
            raise Exception(response.content)
    except Exception as e:
        logger.error(f'Erro ao realizar PUT /catalogo/listapreco na api okvendas {str(e)}')
        return []


def put_price_lists_products(price_list_code: str, body: str) -> bool:
    try:
        url = f'{src.client_data.get("url_api")}/catalogo/listapreco/preco/lote?price_list_code={price_list_code}'
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json',
                   'access-token': src.client_data.get('token_api')}
        json_body = jsonpickle.encode(body, unpicklable=False)
        if src.print_payloads:
            print(json_body)
        response = requests.put(url, headers=headers, json=json.loads(json_body))
        return response.ok
    except Exception as e:
        logger.error(f'Erro ao realizar PUT /catalogo/listapreco/preco/lote na api okvendas {str(e)}')


def post_product_tax(body: List[ImpostoProduto]) -> List[ProductTaxResponse]:
    try:
        url = f'{src.client_data.get("url_api")}/catalogo/impostoNCM'
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json',
                   'access-token': src.client_data.get('token_api')}
        json_body = jsonpickle.encode(body, unpicklable=False)
        if src.print_payloads:
            print(json_body)
        response = requests.post(url, headers=headers, json=json.loads(json_body))
        result = [ProductTaxResponse(**t) for t in response.json()]
        return result
    except Exception as e:
        logger.error(f'Erro ao realizar POST /catalogo/impostoNCM na api okvendas {str(e)}')

def post_product_full_tax(df: pd.DataFrame):
    try:

        #Escreve o DataFrame para um arquivo CSV
        csv_string = df.to_csv(index=False)

        url = f'{src.client_data.get("url_api")}/catalogo/impostoLoteNCM'
        headers = {
            'access-token': src.client_data.get('token_api')
        }

        #Criando objeto para o envio do arquivo
        files = {'file': ('imposto_produto_lote.csv', csv_string, 'text/csv')}

        #Upload do arquivo para uma API
        response = requests.post(url, headers=headers, files=files)

        if response.ok:
            return response.json()
        else:
            if response.content is not None and response.content != '':
                return response.json()
    except Exception as e:
        logger.error(f'Erro ao realizar POST /catalogo/impostoLoteNCM na api okvendas {str(e)}')

def put_representative(body: List[Representante]) -> List[Representative]:
    try:
        url = f'{src.client_data.get("url_api")}/representante'
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json',
                   'access-token': src.client_data.get('token_api')}
        json_body = jsonpickle.encode(body, unpicklable=False)
        if src.print_payloads:
            print(json_body)
        response = requests.put(url, headers=headers, json=json.loads(json_body))
        if response.ok:
            res = jsonpickle.decode(response.content)
        result = [ProductTaxResponse(**t) for t in response.json()]
        return result
    except Exception as e:
        logger.error(f'Erro ao realizar POST /representative/representante na api okvendas {str(e)}')


def post_client_payment_plan(body: PlanoPagamentoCliente) -> (bool, dict):
    try:
        url = f'{src.client_data.get("url_api")}/client/formapagamento'
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json',
                   'access-token': src.client_data.get('token_api')}
        json_body = jsonpickle.encode(body, unpicklable=False)
        if src.print_payloads:
            print(json_body)
        response = requests.post(url, headers=headers, json=json.loads(json_body))

        if response.ok:
            return response.ok, response.status_code, response.json()
    except Exception as e:
        logger.error(f'Erro ao realizar POST /client/formapagamento na api okvendas {str(e)}')


def get_approved_clients() -> ApprovedClientResponse:
    try:
        headers = {
            'access-token': src.client_data.get('token_api')
        }

        res = requests.get(f'{src.client_data.get("url_api")}/cliente/pendente/parceiro?init=1&limit=100', headers=headers)
        if res.ok and len(res.content) > 0:
            return ApprovedClientResponse(**res.json())

        res.raise_for_status()
    except Exception as e:
        logger.error(f'Erro ao consultar clientes aprovados {str(e)}')
        return None
