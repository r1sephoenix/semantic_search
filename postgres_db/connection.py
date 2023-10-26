import psycopg2
from sshtunnel import SSHTunnelForwarder
import yaml

with open('postgres_db/config.yml', 'r') as f:
    config_yaml = yaml.safe_load(f)

Host = config_yaml['Host']
User = config_yaml['User']
Path_to_ssh_key = config_yaml['Path_to_ssh_key']
Db_name = config_yaml['vectordb']
Db_user = config_yaml['testuser']
Db_password = config_yaml['testpwd']
Db_port = config_yaml['Db_port']

def create_db_connection():
    tunnel = SSHTunnelForwarder(
        (Host, 22),
        ssh_username=User,
        ssh_private_key=Path_to_ssh_key,
        remote_bind_address=('localhost', Db_port),
        local_bind_address=('localhost', 6543)
    )
    tunnel.start()
    try:
        conn = psycopg2.connect(
            database=Db_name,
            user=Db_user,
            password=Db_password
        )
        return tunnel, conn
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting", error)
    return None

# conn.close()
# tunnel.stop()

