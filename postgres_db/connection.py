import psycopg2
from sshtunnel import SSHTunnelForwarder
import yaml
from pathlib import Path
from dotenv import load_dotenv
from configparser import ConfigParser


config_dir = Path(__file__).parent.parent.resolve() / 'config'

with open(config_dir / 'config.yml', 'r') as f:
    config_yaml = yaml.safe_load(f)

Host = config_yaml['Hostname']
User = config_yaml['User']
Path_to_ssh_key = config_yaml['Path_to_ssh_key']
Db_port = config_yaml['Db_port']

load_dotenv()

BASE_DIR = Path(__file__).parents[1]
DB_INIT_FILE = BASE_DIR / 'config/database.ini'


def db_config(filename: Path = DB_INIT_FILE, section: str = 'postgresql'):
    parser = ConfigParser()
    parser.read(filename)
    if parser.has_section(section):
        params = parser.items(section)
        db = {param[0]: param[1] for param in params}
    else:
        raise Exception(f'Section {section} not found in the {filename} file')
    return db


def create_db_ssh_connection():
    tunnel = SSHTunnelForwarder(
        (Host, 22),
        ssh_username=User,
        ssh_private_key=Path_to_ssh_key,
        remote_bind_address=('0.0.0.0', Db_port)
    )
    tunnel.start()

    try:
        params = db_config()
        conn = psycopg2.connect(**params)
        return tunnel, conn
    except (Exception, psycopg2.Error) as error:
        print('Error while connecting', error)
    return None


def create_db_connection():
    params = db_config()
    try:
        conn = psycopg2.connect(**params)
        return conn
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting", error)
    return None


if __name__ == '__main__':
    tunnel, conn = create_db_connection()
    conn.close()
    tunnel.stop()
