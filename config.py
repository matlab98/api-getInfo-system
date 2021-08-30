class Config(object):
    #Base configuration
    DEBUG = False
    TESTING = False
class DevelopmentConfig(Config):
    #Development configuration
    DEBUG = True
class TestingConfig(Config):
    #Testing configuration
    DEBUG = True
    TESTING = True
class ProductionConfig(Config):
    #Production configuration
    DEBUG = False