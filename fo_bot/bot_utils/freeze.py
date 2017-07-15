import pickle

from fo_bot.settings import *


def save_user_data(user_data):
    """Store user data into file with dict."""
    pickle.dump(user_data, open(USER_DATA_DUMP_FILENAME, 'wb'))

def save_conversations(conversations):
    pickle.dump(conversations, open(CONVERSATION_DUMP_FILENAME, 'wb'))

def load_user_data():
    return pickle.load(open(USER_DATA_DUMP_FILENAME, 'rb'))

def load_conversations():
    return pickle.load(open(CONVERSATION_DUMP_FILENAME, 'rb'))
