import os
import pyodbc
import docker

MSSQL_DRIVER_PATH = os.getenv('MSSQL_DRIVER_PATH', '/usr/local/lib/libmsodbcsql.17.dylib')
MSSQL_SA_PASSWORD = 'Adm1nP@55w0rd'


if not os.path.exists(MSSQL_DRIVER_PATH):
    raise EnvironmentError('MSSQL_DRIVER_PATH environment variable is not correct.')


def create_docker_mssql(db_path):
    mount_path = os.path.abspath(db_path)
    if not all(file in os.listdir(mount_path) for file in ['EmptyPack_Data.mdf', 'EmptyPack_Log.ldf']):
        raise FileNotFoundError('Count not find the carto database files in the specified path.')

    mount = docker.types.Mount(target='/var/opt/mssql/data/', source=mount_path, type='bind')
    client = docker.from_env()
    container = client.containers.run('mcr.microsoft.com/mssql/server:2017-CU8-ubuntu',
                                      environment={'ACCEPT_EULA': 'Y', 'SA_PASSWORD': MSSQL_SA_PASSWORD},
                                      ports={1433: 1433},
                                      mounts=[mount],
                                      detach=True)
    return container



class Carto:
    def __init__(self, path):
        """
        Initialize the object
        :param path: the path to the MDF database file to open
        """
        self._path = os.path.abspath(path)
        connection_args = {
            'Driver': MSSQL_DRIVER_PATH,
            'Server': 'localhost,1433',
            'Database': 'TemporaryCartoDatabase',
            'AttachDbFileName': '{/var/opt/mssql/data/EmptyPack_data.mdf}',
            'Uid': 'sa',
            'Pwd': 'Adm1nP@55w0rd'
        }
        cx = pyodbc.connect(''.join([f'{k}={v};' for k, v in connection_args.items()]), autocommit=False)
        cursor = cx.cursor()

        print([row.table_name for row in cursor.tables()])

        cx.close()

