import json
import logging
import logging.handlers
import os


class Config:
    def __init__(self):
        with open('config.json', "r") as config_file:
            self._config = json.load(config_file)

    def get(self, parameter):
        # Intentar obtener de variables de entorno primero (para datos sensibles)
        env_var = f"ABONO_{parameter.upper()}"
        env_value = os.getenv(env_var)
        if env_value is not None:
            # Convertir a lista si es necesario (para gmail_recipients)
            if parameter == 'gmail_recipients' and isinstance(env_value, str):
                return [email.strip() for email in env_value.split(',')]
            # Convertir a número si es necesario
            if parameter in ['gmail_port', 'events_threshold']:
                try:
                    return float(env_value) if parameter == 'events_threshold' else int(env_value)
                except ValueError:
                    pass
            return env_value
        return self._config.get(parameter)


class Logger:
    def __init__(self):
        handler = logging.handlers.WatchedFileHandler('abonoteatro.log')
        handler.setFormatter(logging.Formatter(fmt="%(asctime)s - %(levelname)s - %(message)s",
                                               datefmt="%d/%b/%Y %H:%M:%S"))
        root = logging.getLogger()
        root.setLevel(logging.INFO)
        root.addHandler(handler)
