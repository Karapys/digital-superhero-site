from app.models import *
from app.database import *


init_db()
u = User(name="admin", password="admin")
db_session.add(u)
db_session.commit()
