from geopy import Nominatim

from curiosus.models import (Device, Location, SkypeMessage, TelegramMessage,
                             WhatsAppMessage)

geolocator = Nominatim()


def get_last_chat_messages():
    telegram = TelegramMessage.query.order_by(TelegramMessage.date.desc()).limit(10).all()
    whatsapp = WhatsAppMessage.query.order_by(WhatsAppMessage.date.desc()).limit(10).all()
    skype = SkypeMessage.query.order_by(SkypeMessage.date.desc()).limit(10).all()

    messages = []
    messages += [{'device': t.device.number if t.device.number else t.device.imei, 'type': 'Telegram', 'author': t.author.fullname if t.author.fullname else t.author.external_id, 'text': t.text, 'date': t.date} for t in telegram]
    messages += [{'device': t.device.number if t.device.number else t.device.imei, 'type': 'WhatsApp', 'author': t.author.fullname if t.author.fullname else t.author.external_id, 'text': t.text, 'date': t.date} for t in whatsapp]
    messages += [{'device': t.device.number if t.device.number else t.device.imei, 'type': 'Skype', 'author': t.author.username if t.author.username else t.author.external_id, 'text': t.text, 'date': t.date} for t in skype]

    return list(reversed(sorted(messages, key=lambda k: k['date'])))[:10]


def get_last_devices_locations():
    devices = Device.query.all()

    dlist = []

    for d in devices:
        obj = {}
        obj['id'] = d.id
        obj['imei'] = d.imei
        obj['serial'] = d.serial
        obj['number'] = d.number
        obj['location'] = d.locations.order_by(Location.date.desc()).limit(1).first()
        obj['address'] = geolocator.reverse('{}, {}'.format(obj['location'].latitude, obj['location'].longitude)).address

        dlist.append(obj)

    return dlist
