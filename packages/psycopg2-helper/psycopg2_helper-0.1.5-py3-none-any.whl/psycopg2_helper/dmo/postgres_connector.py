#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" Connect to the Postgres instance  """


from typing import Optional

from psycopg2 import connect

from baseblock import EnvIO
from baseblock import CryptoBase
from baseblock import BaseObject


class PostgresConnector(BaseObject):
    """ Connect to the Postgres instance  """

    __decrypt_str = CryptoBase().decrypt_str

    def __init__(self,
                 user: Optional[str] = None,
                 password: Optional[str] = None,
                 host: Optional[str] = None,
                 port: Optional[str] = None,
                 database_name: Optional[str] = None):
        """ Change Log

        Created:
            16-Nov-2022
            craigtrim@gmail.com

        Args:
            user (Optional[str], optional): the user name. Defaults to None.
                Credentials MUST BE Encrypted
            password (Optional[str], optional): the user password. Defaults to None.
                Credentials MUST BE Encrypted
            host (Optional[str], optional): the host. Defaults to None.
            port (Optional[str], optional): the port. Defaults to None.
            database_name (Optional[str], optional): the database name. Defaults to None.
        """
        BaseObject.__init__(self, __name__)

        def get_user() -> str:
            if user:
                return user
            return self.__decrypt_str(EnvIO.str_or_exception('POSTGRES_USERNAME'))

        def get_password() -> str:
            if password:
                return password
            return self.__decrypt_str(EnvIO.str_or_exception('POSTGRES_PASSWORD'))

        def get_host() -> str:
            if host:
                return host
            return EnvIO.str_or_exception('POSTGRES_HOST')

        def get_port() -> str:
            if port:
                return port
            return EnvIO.int_or_default('POSTGRES_PORT', '5432')

        def get_database_name() -> Optional[str]:
            if database_name:
                return database_name
            return EnvIO.str_or_default('POSTGRES_DATABASE_NAME', None)

        self.conn = connect(
            user=get_user(),
            password=get_password(),
            host=get_host(),
            dbname=get_database_name())

    def close(self):
        self.conn.commit()
        cursor = self.conn.cursor()
        self.conn.close()
        cursor.close()
