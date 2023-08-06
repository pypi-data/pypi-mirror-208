import tensorflow as tf
import numpy as np


def create_config():
    with open("TriModelSystem.conf", 'w') as conf:
        conf.write("#Hyperparameters - Model A\n"
                   "modelA_units = 512\n"
                   "modelA_dropout_percent = 0.3\n"
                   "modelA_learning_rate = 0.000001\n"
                   "modelA_regularization = 0.001\n\n"
                   "#Hyperparameters - Model B\n"
                   "modelB_units = 1024\n"
                   "modelB_dropout_percent = 0.2\n"
                   "modelB_learning_rate = 0.00001\n"
                   "modelB_regularization = 0.001\n\n"
                   "#Hyperparameters - Model C\n"
                   "modelC_units = 128\n"
                   "modelC_dropout_percent = 0.3\n"
                   "modelC_learning_rate = 0.00001\n"
                   "modelC_regularization = 0.0001\n\n"
                   "batch_size = 256\n"
                   "epochs = 1000")
    conf.close()


def load_config():
    try:
        with open("TriModelSystem.conf", 'r') as conf:
            config_data = conf.readlines()
            updated_config_data = []
            for data in config_data:
                if not data.startswith("#Hyperparameters"):
                    updated_config_data.append(data.replace('\n', ''))
            return [line for line in updated_config_data if line.strip()]
    except Exception:
        print("Config file not found. You can create a config file with 'create_config()'")
        exit()


def get_model_data(mode='A'):
    config_data = load_config()
    model_data = []
    mode_mapping = {
        'A': [0, 1, 2, 3],
        'B': [4, 5, 6, 7],
        'C': [8, 9, 10, 11]
    }
    mapped_data = [config_data[index] for index in mode_mapping.get(mode, [])]
    for data in mapped_data:
        model_data.append(float(data.split(' ')[-1]))
    return model_data
