#! /usr/bin/env python 
from flask import Flask

from telebot import TeleBot

from flask_sqlalchemy import SQLAlchemy


from FreeKassa import FK

class Config(object):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///main.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

kassa = FK()

TOKEN = '982289200:AAEly1UbsHD6cQINuAnwF9s1QZGLHRMPvno'
bot = TeleBot(TOKEN)

admins = [865473632]

WEBHOOK_URL = f'localhost'
WEBHOOK_LISTEN = 'localhost'
WEBHOOK_PORT = '443'
