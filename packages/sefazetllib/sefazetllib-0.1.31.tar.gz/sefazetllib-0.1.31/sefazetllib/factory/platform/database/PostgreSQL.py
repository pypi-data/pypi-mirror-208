from sqlalchemy import create_engine, text

from sefazetllib.factory.platform.DatabasePlatform import DatabasePlatform


class PostgreSQL(DatabasePlatform):
    def __init__(self, name="PostgreSQL Job", configs=[]) -> None:
        self.name = name
        self.session = None
        self.conn = None
        self.transaction = None

        if configs != []:
            url_args = configs
            if not isinstance(configs, dict):
                url_args = {config[0]: config[1] for config in configs}

            self.session = create_engine(
                f"postgresql+psycopg2://"
                f'{url_args["user"]}:{url_args["password"]}@{url_args["host"]}:'
                f'{url_args["port"]}/'
                f'{url_args["instance"]}'
            )
            self.create_connection()

    def get_url(self, **kwargs):
        host = kwargs["host"]
        port = kwargs["port"]
        file_format = kwargs["file_format"]
        operator = kwargs["operator"]
        database = kwargs["database"].lower()
        instance = kwargs["instance"]
        return f"{file_format}{operator}{database}://{host}:{port}/{instance}"

    def get_table_name(self, **kwargs):
        schema = kwargs["schema"]
        table = kwargs["table"]
        return f"{schema}.{table}"

    def create_connection(self):
        self.conn = self.session.connect()
        return

    def close_connection(self):
        self.conn.close()
        return

    def begin_transaction(self):
        self.transaction = self.conn.begin()
        return

    def create_commit(self):
        if self.transaction is not None:
            self.transaction.commit()
        return

    def rollback(self):
        if self.transaction is not None:
            self.transaction.rollback()
        return

    def truncate(self, **kwargs):
        schema = kwargs["schema"].lower()
        table = kwargs["table"].lower()
        self.conn.execute(text(f"TRUNCATE TABLE {schema}.{table}"))
        return

    def drop_constraints(self, **kwargs):
        table = kwargs["table"].lower()
        dependencies = [
            row._asdict()
            for row in self.conn.execute(
                text(
                    f"""
        SELECT tc.table_schema,
            tc.constraint_name,
            tc.table_name,
            kcu.column_name,
            ccu.table_schema AS foreign_table_schema,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu ON ccu.constraint_name = tc.constraint_name
            AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
            AND (tc.table_name = '{table}' OR ccu.table_name = '{table}')
        """
                )
            ).fetchall()
        ]

        alter_queries = [
            f"""ALTER TABLE {dependencie['table_schema']}.{dependencie['table_name']} DROP CONSTRAINT {dependencie['constraint_name']};"""
            for dependencie in dependencies
        ]

        if bool(alter_queries):
            self.conn.execute(text("\n".join(alter_queries)))
        return dependencies

    def create_constraints(self, **kwargs):
        dependencies = kwargs["dependencies"]

        alter_queries = [
            f"""ALTER TABLE {dependencie['table_schema']}.{dependencie['table_name']} ADD CONSTRAINT {dependencie['constraint_name']} FOREIGN KEY ({dependencie['column_name']}) REFERENCES {dependencie['foreign_table_schema']}.{dependencie['foreign_table_name']}({dependencie['foreign_column_name']});"""
            for dependencie in dependencies
        ]
        if bool(alter_queries):
            self.conn.execute(text("\n".join(alter_queries)))
        return

    def read(self, **kwargs):
        pass

    def load(self, **kwargs):
        pass
