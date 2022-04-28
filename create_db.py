from serve import *
import hashlib
import uuid


def init_db():
    with app.app_context():
        db.reflect()
        db.drop_all()
        db.create_all()

def createseed():
    data={
        'email': "samarpan020@gmail.com",
        'password': hashlib.sha256("test@123".encode('utf-8')).hexdigest(),
        'name' : "samarpan Dhungana",
        'public_id':str(uuid.uuid4())
    }
    users = User(**data)
    db.session.add(users)
    db.session.commit()


init_db()
createseed()
