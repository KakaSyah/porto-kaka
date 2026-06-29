import os
import sys
sys.path.insert(0, '.')
from config import Config
from model import Database
print('DB_DRIVER=', Config.DB_DRIVER)
print('MySQL config=', Config.MYSQL_CONFIG)
db = Database()
print('Database connection initialized successfully')
