import os
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URI = 'sqlite:///'+os.path.join(ROOT_DIR, "database.db")