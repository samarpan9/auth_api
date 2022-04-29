from serve import *
import hashlib
import uuid


def init_db():
    with app.app_context():
        db.reflect()
        db.drop_all()
        db.create_all()

init_db()
