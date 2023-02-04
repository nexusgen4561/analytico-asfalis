import os

class Config(object):

    basedir = os.path.abspath(os.path.dirname(__file__))

    # Set up the App SECRET_KEY
    # SECRET_KEY = config('SECRET_KEY'  , default='S#perS3crEt_007')
    SECRET_KEY = os.getenv('SECRET_KEY', 'S#perS3crEt_007')

    # This will create a file in <app> FOLDER
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:analytico@localhost/asfalisdb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False 

    SQLALCHEMY_ENGINE_OPTIONS = {
    "max_overflow": 30,
    "pool_pre_ping": True,
    "pool_recycle": 60 * 60,
    "pool_size": 60,
    }
    
    # Assets Management
    ASSETS_ROOT = os.getenv('ASSETS_ROOT', '/static/assets')    
    
class ProductionConfig(Config):
    DEBUG = False

    # Security
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600

    # PostgreSQL database
    SQLALCHEMY_DATABASE_URI = 'postgresql://mbvjwnkuqiwgpe:805a5e28197a2e61c2851574da8212c857e5016a2750af0bbb79710466a08e7e@ec2-35-173-91-114.compute-1.amazonaws.com:5432/dm8nvu4mj2uq0'
    

class DebugConfig(Config):
    DEBUG = True


# Load all possible configurations
config_dict = {
    'Production': ProductionConfig,
    'Debug'     : DebugConfig
}
