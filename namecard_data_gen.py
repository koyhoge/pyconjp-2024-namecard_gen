from io import BytesIO
from PIL import Image
import csv
import json
import os
import pycurl
import qrcode
import requests
import time

CSV_INPUT = 'event_324211_participants.csv'
CSV_INPUT_STAFF = 'event_326215_participants.csv'
CSV_OUTPUT = 'pycon2024_attendee.csv'
DIR_USER_IMG = 'user_img'
DIR_USER_QR = 'user_qr'

def  gen_qr(data, path):
    qr = qrcode.QRCode(
        version=1,  # QRコードのバージョン (1-40)
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # 誤り訂正レベル
        box_size=10,  # モジュールサイズ
        border=4,  # 境界線
    )
    qr.add_data(data)
    qr.make(fit=True)

    # QRコード画像の作成
    img = qr.make_image(fill_color="black", back_color="white")

    # 画像の保存
    img.save(path)

def get_connpass_info(user):
    urlbase = "https://connpass.com/api/v1/user/"
    url = urlbase + '?nickname=' + user
    b_obj = BytesIO()

    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEDATA, b_obj)

    c.perform()

    # レスポンスボディを取得
    body = b_obj.getvalue().decode('utf-8')
    result = json.loads(body)

    # クリーンアップ 
    c.close()

    return result['users'][0]

def get_profile_img(user):
    info = get_connpass_info(user)
    imgurl = info['user_image_url']

    if imgurl == None:
        return

    res = requests.get(imgurl)

    path = DIR_USER_IMG + '/' + user + '.png'
    with open(path, 'wb') as f:
        f.write(res.content)

def process_data(data):
        type = data['type']
        user = data['user']
        print_name = data['print_name']
        ticket_num = data['ticket_num']
        t_shirt = data['t_shirt']
        status = data['status']

        if status == '参加キャンセル':
            return

        print('processing ' + user)

        writer.writerow([type, user, print_name, ticket_num, t_shirt])

        # get profile image and save
        #    get_profile_img(user)
        # time.sleep(0.2)

        # generate QR and save
        user_url = 'https://connpass.com/user/' + user + '/'
        qr_path = DIR_USER_QR + '/' + user + '.png'
        # gen_qr(user_url, qr_path)

if __name__ == "__main__":

    input = open(CSV_INPUT, 'r')
    input2 = open(CSV_INPUT_STAFF, 'r')
    output = open(CSV_OUTPUT, 'w', newline='')

    reader = csv.reader(input)
    reader2 = csv.reader(input2)
    writer = csv.writer(output)
    writer.writerow(['参加枠名', 'ユーザー名', '名札表示名', '受付番号', 'Tシャツのサイズ'])


    headers = next(reader)
    for row in reader:
        data = {
            'type': row[0],
            'user': row[1],
            'status': row[5],
            'print_name': row[9],
            't_shirt': row[16],
            'ticket_num': row[24]
        }
        process_data(data)

    headers = next(reader2)
    for row in reader2:
        data = {
            'type': 'Staff',
            'user': row[1],
            'status': row[5],
            'print_name': row[9],
            't_shirt': row[16],
            'ticket_num': row[23]
        }
        process_data(data)

    output.close()
