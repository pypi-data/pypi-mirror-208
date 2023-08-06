#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" Perform Common Postgres Table Operations """


from typing import List

from psycopg2.extensions import connection

from baseblock import BaseObject


class PerformTableOperations(BaseObject):
    """ Perform Common Postgres Table Operations """

    def __init__(self,
                 conn: connection):
        """ Change Log

        Created:
            16-Nov-2022
            craigtrim@gmail.com
        Updated:
            16-May-2023
            craigtrim@gmail.com
            *   make exception handling more consistent
        """
        BaseObject.__init__(self, __name__)
        self.conn = conn

    def create_table(self,
                     create_table_ddl: str):
        """ Create a Table

        Args:
            create_table_ddl (str): Fully Qualified DDL
                Sample Input:
                    "CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);"
        Raises:
            ValueError: Create Table Failure
        """
        cur = self.conn.cursor()
        try:

            cur.execute(create_table_ddl)

        except Exception as e:
            self.logger.error(e)
            raise ValueError('Create Table Failure')

        self.conn.commit()

    def delete_table(self,
                     name: str,
                     schema: str) -> None:
        """ Delete (Drop) a Table

        Args:
            name (str): Table Name
            name (str): Schema Name

        Returns:
            str: status message

        Raises:
            ValueError: Delete Table Failure
        """
        sql = f'DROP TABLE IF EXISTS {schema}.{name} CASCADE;'

        try:

            with self.conn.cursor() as cursor:
                cursor.execute(sql)
                self.conn.commit()

        except Exception as e:
            self.conn.rollback()
            self.logger.error(e)
            raise ValueError(sql)

    def create_schema(self,
                      name: str) -> None:
        """ Create a Schema

        Args:
            name (str): Schema Name

        Raises:
            ValueError: Create Schema Failure
        """
        sql = f'CREATE SCHEMA IF NOT EXISTS {name}'

        try:

            with self.conn.cursor() as cursor:
                cursor.execute(sql)
                self.conn.commit()

        except Exception as e:
            self.conn.rollback()
            self.logger.error(e)
            raise ValueError(sql)

    def delete_schema(self,
                      name: str) -> None:
        """ Delete a Schema

        Args:
            name (str): Schema Name

        Raises:
            ValueError: Delete Schema Failure
        """
        sql = f'DROP SCHEMA IF EXISTS {name}'

        try:

            with self.conn.cursor() as cursor:
                cursor.execute(sql)
                self.conn.commit()

        except Exception as e:
            self.conn.rollback()
            self.logger.error(e)
            raise ValueError(sql)

    def get_table_names(self,
                        schema: str) -> List[str]:
        """ Get Table Names

        Args:
            name (str): Schema Name

        Raises:
            ValueError: Table Name Retrieval Failure
        """
        sql = f"SELECT table_name FROM information_schema.tables WHERE table_schema='{schema}'"

        values = []
        try:
            with self.conn.cursor() as cursor:

                cursor.execute(sql)
                rows = cursor.fetchall()
                for tup in rows:
                    values += [tup[0]]

        except Exception as e:
            self.conn.rollback()
            self.logger.error(e)
            raise ValueError(sql)

        return sorted(set(values), key=len, reverse=True)
