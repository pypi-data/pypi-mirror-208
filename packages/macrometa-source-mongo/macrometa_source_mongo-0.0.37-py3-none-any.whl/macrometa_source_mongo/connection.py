import singer
import uuid

from typing import Dict, List
from pathlib import Path
from pymongo import MongoClient
from pymongo.database import Database
from urllib import parse

LOGGER = singer.get_logger('macrometa_source_mongo')

INTERNAL_DB = ['system', 'local', 'config']
NO_READ_PRIVILEGES = {
    'dbAdmin',
    'userAdmin',
    'clusterAdmin',
    'clusterManager',
    'clusterMonitor',
    'hostManager',
    'restore'
}
READ_PRIVILEGES = {
    'read',
    'readWrite',
    'readAnyDatabase',
    'readWriteAnyDatabase',
    'dbOwner',
    'backup',
    'root'
}
ALL_DB_READ_PRIVILEGES = {
    'readAnyDatabase',
    'readWriteAnyDatabase',
    'root'
}

def get_user_info(database: Database, db_user: str) -> Dict:
    user_info = database.command({'usersInfo': db_user})
    users = [u for u in user_info.get('users') if u.get('user') == db_user]
    return None if len(users) != 1 else users[0]

def get_sub_roles(database: Database, role_name: str) -> List[Dict]:
    role_info_list = database.command({'rolesInfo': {'role': role_name, 'db': database.name}})
    role_info = [r for r in role_info_list.get('roles', []) if r['role'] == role_name]

    return [] if len(role_info) != 1 else role_info[0].get('roles', [])

def get_user_roles_with_find_privs(database: Database, user: Dict) -> List[Dict]:
    roles = []

    for role in user.get('roles', []):
        if role.get('role') in NO_READ_PRIVILEGES:
            continue

        role_name = role['role']

        if role_name in READ_PRIVILEGES and role.get('db'):
            roles.append(role)
        else:
            sub_roles = get_sub_roles(database, role_name)
            roles.extend([sub_role for sub_role in sub_roles
                          if sub_role.get('role') in READ_PRIVILEGES and sub_role.get('db')])

    return roles

def get_user_roles(database: Database, db_user: str) -> List[Dict]:
    user = get_user_info(database, db_user)

    return [] if user is None else get_user_roles_with_find_privs(database, user)

def get_user_databases(client: MongoClient, config: Dict) -> List[str]:
    roles = get_user_roles(client[config['auth_database']], config['user'])

    can_read_all = len([role for role in roles if role['role'] in ALL_DB_READ_PRIVILEGES]) > 0
    return (
        [d for d in client.list_database_names() if d not in INTERNAL_DB]
        if can_read_all
        else [role['db'] for role in roles if role['db'] not in INTERNAL_DB]
    )

def create_certficate_files(config: Dict) -> Dict:
    path_uuid = uuid.uuid4().hex
    try:
        if config.get('tls_ca_file'):
            path = f"/opt/mongo/{path_uuid}/ca.pem"
            ca_cert = Path(path)
            ca_cert.parent.mkdir(exist_ok=True, parents=True)
            ca_cert.write_text(create_ssl_string(config['tls_ca_file']))
            config['tls_ca_file'] = path
            LOGGER.info(f"CA certificate file created at: {path}")

        if config.get('tls_certificate_key_file'):
            path = f"/opt/mongo/{path_uuid}/client.pem"
            client_cert = Path(path)
            client_cert.parent.mkdir(exist_ok=True, parents=True)
            client_cert.write_text(create_ssl_string(config['tls_certificate_key_file']))
            config['tls_certificate_key_file'] = path
            LOGGER.info(f"Client certificate file created at: {path}")
    except Exception as e:
        LOGGER.warn(f"Failed to create certificate: /opt/mongo/{path_uuid}/. {e}")
    return config

def delete_certficate_files(config: Dict) -> None:
    try:
        cert = None
        if config.get('tls_ca_file'):
            path = config['tls_ca_file']
            cert = Path(path)
            config['tls_ca_file'] = cert.read_text()
            cert.unlink()
            LOGGER.info(f"CA certificate file deleted from: {path}")

        if config.get('tls_certificate_key_file'):
            path = config['tls_certificate_key_file']
            cert = Path(path)
            config['tls_certificate_key_file'] = cert.read_text()
            cert.unlink()
            LOGGER.info(f"Client certificate file deleted from: {path}")

        if cert is not None:
            cert.parent.rmdir()
    except Exception as e:
        LOGGER.warn(f"Failed to delete certificate: {e}")

def create_ssl_string(ssl_string: str) -> str:
    tls_certificate_key_list = []
    split_string = ssl_string.split("-----")
    if len(split_string) < 4:
        raise Exception("Invalid PEM format for certificate.")
    for i in range(len(split_string)):
        if ((i % 2) == 1):
            tls_certificate_key_list.extend(("-----", split_string[i], "-----"))
        else:
            tls_certificate_key_list.append(split_string[i].replace(' ', '\n'))

    return ''.join(tls_certificate_key_list)

def get_connection_string(config: Dict):
    """
    Constructs a MongoClient connection string based on the provided configuration.
    Args:
        config (Dict): A dictionary containing database configuration parameters.

    Returns:
        str: A MongoClient connection string.
    """
    srv = config.get('srv', False)

    verify_mode = config.get('verify_mode', True)
    use_ssl = config.get('ssl')
    direct_connection = config.get('direct_connection', False)

    connection_query = {
        'readPreference': 'secondaryPreferred',
        'authSource': config['auth_database'],
    }

    if config.get('replica_set'):
        connection_query['replicaSet'] = config['replica_set']

    if use_ssl:
        connection_query['tls'] = 'true'
        if config.get('tls_ca_file'):
            connection_query['tlsCAFile'] = config['tls_ca_file']
        if config.get('tls_certificate_key_file'):
            connection_query['tlsCertificateKeyFile'] = config['tls_certificate_key_file']
            if config.get('tls_certificate_key_file_password'):
                connection_query['tlsCertificateKeyFilePassword'] = config['tls_certificate_key_file_password']

    if direct_connection:
        connection_query['directConnection'] = 'true'

    # tlsAllowInvalidCertificates to be used only if tls is true.
    if not verify_mode and use_ssl:
        connection_query['tlsAllowInvalidCertificates'] = 'true'

    query_string = parse.urlencode(connection_query)

    port = "" if srv else f":{int(config['port'])}"

    return f'{"mongodb+srv" if srv else "mongodb"}://{parse.quote(config["user"])}:{parse.quote(config["password"])}@{config["host"]}{port}/{config["database"]}?{query_string}'
