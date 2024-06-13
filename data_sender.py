import config #наш конфиг
import os
import re
import psycopg2
import schedule
from datetime import datetime, date
class Log:
    '''клаасс для хранения инфы о логах'''
    def __init__(self):
        self.__server_ip = 'Нет данных'
        self.__date = date.today()
        self.__query = 'Нет данных'
        self.__response = 'Нет данных'
        self.__weight = 'Нет данных'
    def __repr__(self):
       return f'ip: {self.__server_ip}, date: {self.__date}, query: {self.__query}, response: {self.__response}, weight: {self.__weight}'


    def __iter__(self):
        #прописываем итерацию для формирования кортежей
        for attr in (self.__server_ip,self.__date,self.__query,self.__response,self.__weight):
            yield attr

    @property
    def server_ip(self):
        return self.__server_ip
    @server_ip.setter
    def server_ip(self, value):
        self.__server_ip = value

    @property
    def date(self):
        return self.__date
    @date.setter
    def date(self, value):
        self.__date = value

    @property
    def query(self):
        return self.__query

    @query.setter
    def query(self, value):
        self.__query = value

    @property
    def response(self):
        return self.__response

    @response.setter
    def response(self, value):
        self.__response = value

    @property
    def weight(self):
        return self.__weight

    @weight.setter
    def weight(self, value):
        self.__weight = value


data_patterns = {
    '%h': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
    '%t': r'(\d{2}\/[A-Za-z]{3,5}\/\d{4}:\d{2}:\d{2}:\d{2})',
    '%r': r'"(.*?)"',
    '%>s': r'\b\d{3}\b',
    '%b': r'\b\d+\b'
}
#словарь в формате 'модификатор' : 'паттерн'

def read_data(file_paths, data_patterns) -> [Log]:
    '''функция для чтения логов из файла'''
    logs = []
    for file_path, file_pattern in file_paths: #проходимся по всем файлам
        if not os.path.exists(file_path): #проверяем наличие файла
            print(f'Данный файл не найден: {file_path}')
            continue

        file_patterns = file_pattern.split(',')
        file_patterns = list(filter(lambda pattern: pattern in data_patterns, file_patterns)) #фильтруем паттерны
        if not file_patterns: #проверяем паттерны файла
            print(f'некоректный или пустой паттерн: {file_pattern}')
            continue
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                line = line.strip()
                log = create_log(line, data_patterns, file_patterns)
                logs.append(log)
    print(logs) #необязятельно, просто выводим логи для наглядности программы
    return logs

def create_log(line: str, data_patterns: {str:str}, file_patterns: str) -> Log:
    '''функция для создания логов из строки с помошью паттернов'''
    log = Log()
    for file_pattern in file_patterns:
        match = re.search(data_patterns[file_pattern], line) #применяем паттерн
        if match is None: #проверка результата
            continue
        match file_pattern: #в зависимости от модификатора записываем значение в поле лога
            case '%h':
                log.server_ip = match.group()
            case '%t':
                date_str = match.group(1)
                date_object = datetime.strptime(date_str, '%d/%b/%Y:%H:%M:%S')
                formatted_date = date_object.strftime('%Y-%m-%d') #немного меняем дату для sql
                log.date = formatted_date
            case '%r':
                log.query = match.group(1)
            case '%>s':
                log.response = match.group()
            case '%b':
                log.weight = match.group()

    return log
def init_connection(db_info: {str:str}):
    '''функция для инициализации подключения к бд'''
    connection = None
    try:
        connection = psycopg2.connect(
            database = db_info['database'],
            user = db_info['user'],
            password = db_info['password'],
            host = db_info['host'],
            port = db_info['port'],
        )
    except:
        print(f"Невозможно подключиться к бд")
    return connection

def pull_data(connection, logs: Log) -> None:
    '''функция для отправки информации на бд'''
    try:
        logs_records = ", ".join(["%s"] * len(logs)) #создаем плейсхолдеры
        insert_query = (
            f"INSERT INTO logs (server_ip, date_time, log_query, response, weight) VALUES {logs_records}" #формируем запрос
        )
        connection.autocommit = True
        cursor = connection.cursor()
        cursor.execute(insert_query, logs) #отправляем логи
        print('Данные отправлены успешно')
    except:
        print('Некоректный запрос или ошибка сервера')

def main():
    global data_patterns
    connection = init_connection(config.db_info)
    logs = read_data(config.file_paths, data_patterns)
    logs = list(map(tuple, logs))
    #pull_data(connection, logs) #строка для отправки информации
if __name__ == '__main__':
    schedule.every(5).seconds.do(main) #строка для автамотического запуска
    try:
        while True:
            schedule.run_pending()
    except KeyboardInterrupt:
        print('сборщик прекратил работу')
    except:
        print('возникла неприятность...')
