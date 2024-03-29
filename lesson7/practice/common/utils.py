from json import loads, dumps
from sys import path

from common.variables import MAX_PACKAGE_LENGTH, ENCODING
from common.decors import log

path.append('../')


@log
def get_message(client):
    """
    Функция приёма сообщений от удалённых компьютеров.
    Принимает сообщения JSON, декодирует полученное сообщение
    и проверяет что получен словарь.
    :param client: сокет для передачи данных.
    :return: словарь - сообщение.
    """
    encoded_response = client.recv(MAX_PACKAGE_LENGTH)
    json_response = encoded_response.decode(ENCODING)
    response = loads(json_response)
    if isinstance(response, dict):
        return response
    else:
        raise TypeError


@log
def send_message(sock, message):
    """
    Функция отправки словарей через сокет.
    Кодирует словарь в формат JSON и отправляет через сокет.
    :param sock: сокет для передачи
    :param message: словарь для передачи
    :return: ничего не возвращает
    """
    js_message = dumps(message)
    encoded_message = js_message.encode(ENCODING)
    sock.send(encoded_message)
