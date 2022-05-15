from dotenv import load_dotenv

load_dotenv()

# Statement for enabling the development environment
DEBUG = False

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  

# Define the database - we are working with
# SQLite for this example
if 'POSTGRES_DB' in os.environ:
    SECRET_KEY = os.environ['SECRET_KEY']
    SQLALCHEMY_DATABASE_URI = 'mysql://{}:{}@{}:{}/{}'.format(
        os.environ['POSTGRES_USER'],
        os.environ['POSTGRES_PASSWORD'],
        os.environ['POSTGRES_HOST'],
        os.environ['POSTGRES_PORT'],
        os.environ['POSTGRES_DB'],
    )
else:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'mysql://{}:{}@{}:{}/{}'.format(
        os.getenv('POSTGRES_USER'),
        os.getenv('POSTGRES_PASSWORD'),
        os.getenv('POSTGRES_HOST'),
        os.getenv('POSTGRES_PORT'),
        os.getenv('POSTGRES_DB'),
    )
    
SQLALCHEMY_TRACK_MODIFICATIONS = False
#
# # Application threads. A common general assumption is
# # using 2 per available processor cores - to handle
# # incoming requests using one and performing background
# # operations using the other.
# THREADS_PER_PAGE = 2
#
# # Enable protection agains *Cross-site Request Forgery (CSRF)*
# CSRF_ENABLED = True
#
# # Use a secure, unique and absolutely secret key for
# # signing the data.
# CSRF_SESSION_KEY = "secret"

# Secret key for signing cookies
#SECRET_KEY = os.getenv('SECRET_KEY')
