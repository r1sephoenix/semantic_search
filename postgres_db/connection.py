import psycopg2
from sshtunnel import SSHTunnelForwarder
import yaml

from pathlib import Path

config_dir = Path(__file__).parent.parent.resolve() / 'config'

with open(config_dir / 'config.yml', 'r') as f:
    config_yaml = yaml.safe_load(f)

Host = config_yaml['Hostname']
User = config_yaml['User']
Path_to_ssh_key = config_yaml['Path_to_ssh_key']
Db_name = config_yaml['Db_name']
Db_user = config_yaml['Db_user']
Db_password = config_yaml['Db_password']
Db_port = config_yaml['Db_port']


def create_db_connection():
    tunnel = SSHTunnelForwarder(
        (Host, 22),
        ssh_username=User,
        ssh_private_key=Path_to_ssh_key,
        remote_bind_address=('localhost', Db_port),
        #local_bind_address=('localhost', 6543)
    )
    tunnel.start()
    try:
        conn = psycopg2.connect(
            database=Db_name,
            user=Db_user,
            password=Db_password,
            port=Db_port
        )
        return tunnel, conn
    except (Exception, psycopg2.Error) as error:
        print('Error while connecting', error)
    return None


if __name__ == '__main__':
    tunnel, conn = create_db_connection()
    conn.close()
    tunnel.stop()