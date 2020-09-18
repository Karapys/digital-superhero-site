from app.models import *
from app import *


u = User(name="admin", password="admin")
db.session.add(u)
db.session.commit()
