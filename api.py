from flask import Flask, request, jsonify
import psycopg2
import psycopg2.extras
import config

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(
        database=config.db_info['database'],
        user=config.db_info['user'],
        password=config.db_info['password'],
        host=config.db_info['host'],
        port=config.db_info['port'],
        options='-c client_encoding=utf8'  # Устанавливаем кодировку клиента UTF-8
    )
    return conn

@app.route('/logs', methods=['GET'])
def get_logs():
    # Получаем параметры из запроса
    ip = request.args.get('ip', default=None)
    start_date = request.args.get('start_date', default=None)
    end_date = request.args.get('end_date', default=None)

    # Подключаемся к базе данных
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Формируем SQL запрос
    query = 'SELECT * FROM logs WHERE TRUE'
    if ip:
        query += f" AND server_ip = '{ip}'"
    if start_date:
        query += f" AND date_time >= '{start_date}'"
    if end_date:
        query += f" AND date_time <= '{end_date}'"

    cursor.execute(query)
    logs = cursor.fetchall()

    # Преобразуем результаты в JSON
    json_logs = [dict(log) for log in logs]  # Используем DictCursor для упрощения

    cursor.close()
    conn.close()

    return jsonify(json_logs)

if __name__ == '__main__':
    app.run(debug=True)
