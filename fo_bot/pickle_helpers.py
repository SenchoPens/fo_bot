import pickle

from fo_bot.logger import logger


def load_pickle_default(filename, default):
    try:
        with open(filename, 'rb') as f:
            return pickle.load(f)
    except (FileNotFoundError, EOFError):
        logger.warning(f'Pickle file {filename} not found or is corrupted')
        return default


def dump_pickle(filename, obj):
    with open(filename, 'wb') as f:
        pickle.dump(obj, f)
