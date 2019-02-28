import logging

import mongoengine


def global_init():
    mongoengine.register_connection(alias="core", name='Zamirynth')
    logging.info("MongoDB connected")
