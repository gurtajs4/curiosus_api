import sys

from curiosus import app, db
from curiosus.models import User


def create_user(username, password):
    user = User.query.filter_by(email=username).first()
    if not user:
        u = User(email=username)
        u.set_password(password)

        db.session.add(u)
        db.session.commit()

        print('User {} created'.format(username))
    else:
        print('User {} already exists'.format(username))


def change_password(username, password):
    user = User.query.filter_by(email=username).first()
    if not user:
        print('User {} not found'.format(username))
    else:
        user.set_password(password)

        db.session.merge(user)
        db.session.commit()

        print('User {} password changed'.format(username))

if __name__ == '__main__':
    command = sys.argv[1]

    if command == 'create':
        username = sys.argv[2]
        password = sys.argv[3]

        create_user(username, password)

    elif command == 'change_password':
        username = sys.argv[2]
        password = sys.argv[3]

        change_password(username, password)
