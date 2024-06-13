file_paths = [('C:/Users/User/PycharmProjects/log_parser/.venv/Scripts/logs1.txt','%h,%t,%r,%>s,%b'),
              ('C:/Users/User/PycharmProjects/log_parser/.venv/Scripts/logs2.txt','%r,%>s')]
db_info = {
            'database': 'logs_db',
            'user': 'postgres',
            'password': '46919',
            'host': '127.0.0.1',
            'port': '5432'
}
'''
%h - IP-адрес клиента (например, 192.168.2.20 и 127.0.0.1).
%t - Время запроса в формате [день/месяц/год:час:минута:секунда часовой_пояс]
%r - Первая строка запроса
%>s - Статус ответа сервера
%b - Размер ответа в байтах

Примеры работы api
http://127.0.0.1:5000/logs
http://127.0.0.1:5000/logs
http://127.0.0.1:5000/logs?ip=192.168.1.1
http://127.0.0.1:5000/logs?start_date=2024-06-01&end_date=2024-06-13
http://127.0.0.1:5000/logs?ip=192.168.1.1&start_date=2024-06-01&end_date=2024-06-13

примеры работы выборки из бд
select_logs
select_logs date_time weight
select_logs date_time weight
select_logs 2006.01.01
select_logs 2006.01.01 2010.01.01
select_logs date_time 2006.01.01 weight 2010.01.01
select_logs date_time 2006.01.01 
'''


