import config #наш конфиг
import os
import re
import psycopg2
from data_sender import read_data, data_patterns, init_connection, pull_data
import datetime
def create_query(answer:[str]) -> str:
    '''функция для динамического формирования запроса'''
    answer = answer.split(' ')
    date_pattern = re.compile(r'\d{4}(-\d{2}){2}') #прогоняем паттерн перед началом работы
    dates = []
    columns = ''
    trash_mods = [] #список для сбора неопознанной информации
    for mod in answer:
        if date_pattern.match(mod) and len(dates) < 2: #проверяем на дату, после второй перестаем считывать и отправлем в trash_mods
            dates.append(mod)
        elif mod in ['log_ip', 'server_ip', 'date_time', 'log_query', 'response', 'weight'] and mod not in columns:
            # проверяем на соответствие одному из столбцов бд, если столбец уже использовался - отправляем в trash_mods
            if columns == '':
                columns += mod
            else:
                columns += ', ' + mod
        elif mod != 'select_logs': #все остальное фиксируем в trash_mods
            trash_mods.append(mod)
    if columns == '':
        columns = '* ' #если не передали столбцов - выбираем все
    query = 'select ' + columns + ' from logs'
    where_query = ''
    if len(dates) == 1:
        #если передали 1 дату - формируем условие
        date1 = list(map(int, dates[0].split('-')))
        where_query = f' where date_time > TO_DATE(\'{date1[0]}/{date1[1]}/{date1[2]}\', \'YYYY/MM/DD\') and date_time < CURRENT_DATE' #от переданной до тякущей
    elif len(dates) == 2:
        # если передали 2 даты - находим наибольшую
        date1 = list(map(int, dates[0].split('-')))
        date2 = list(map(int, dates[1].split('-')))
        #создаем условие в зависимости от наибольшой из дат
        if datetime.date(date1[0], date1[1], date1[2]) < datetime.date(date2[0], date2[1], date2[2]):
            where_query = f' where date_time > TO_DATE(\'{date1[0]}/{date1[1]}/{date1[2]}\', \'YYYY/MM/DD\') and date_time < TO_DATE(\'{date2[0]}/{date2[1]}/{date2[2]}\', \'YYYY/MM/DD\')'
        else:
            where_query = f' where date_time > TO_DATE(\'{date2[0]}/{date2[1]}/{date2[2]}\', \'YYYY/MM/DD\') and date_time < TO_DATE(\'{date1[0]}/{date1[1]}/{date1[2]}\', \'YYYY/MM/DD\')'
    query += where_query
    query += ';'
    if len(trash_mods) > 0:
        #показываем пользователю неопознанные команды
        print(f'неопознанные команды: {trash_mods}')
    return query, columns #возвращаем столбцы для корректного формирования вывода выборки


def fetch_data_from_db(answer, connection) -> list[dict[str, str]]:
    '''функция для отправки запроса на бд'''
    query, columns = create_query(answer)
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    json_result = []
    # Если columns является строкой со значением '*', преобразуем ее в список всех столбцов
    if columns.strip() == '*':
        columns = ['log_ip', 'server_ip', 'date_time', 'log_query', 'response', 'weight']
    else:
        # Если columns является строкой, преобразуем ее в список
        columns = [col.strip() for col in columns.split(',')]

    for log in result:
        json_format = {}
        # Проверяем, что количество столбцов соответствует количеству элементов в log
        if len(log) != len(columns):
            print(columns, log)
            raise ValueError("Количество столбцов и элементов в результате не совпадает")
        for i, column in enumerate(columns):
            # Создаем словарь в формате 'столбец':'значение'
            json_format[column] = str(log[i])
        json_result.append(json_format)

    return json_result



try:
    connection = init_connection(config.db_info)
    if connection is None:
        raise Exception
    while True:
        answer = input('>>> ')
        if 'init_export' in answer:
            #отправляем данные в бд
            logs = read_data(config.file_paths, data_patterns)
            logs = list(map(tuple, logs))
            pull_data(connection, logs)
        elif 'select_logs' in answer:
            #селектим данные из бд
            logs = fetch_data_from_db(answer, connection)
            for log in logs:
                print(log)
        else:
            print('Неопознанная команда')
except KeyboardInterrupt:
    print('Сессия завершина')




