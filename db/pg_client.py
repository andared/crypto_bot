from psycopg2 import connect, sql
from settings import Settings, logger


class PGClient:
    def __init__(self) -> None:
        self.conn = connect(
            host=Settings.HOST,
            port=Settings.PORT,
            database=Settings.POSTGRES_DB,
            user=Settings.POSTGRES_USER,
            password=Settings.POSTGRES_PASSWORD,
        )
        self.cursor = self.conn.cursor()

    def create_table(self, table: str):
        sql_create_table = sql.SQL("""
            CREATE TABLE IF NOT EXISTS {} (
                id BIGSERIAL PRIMARY KEY,
                username VARCHAR(255) NULL,
                currency VARCHAR(255) NULL,
                subscription_system JSONB,
                alarm_system JSONB,
                last_message VARCHAR(255) NULL
            );
        """).format(sql.Identifier(table))
        self.cursor.execute(sql_create_table)
        self.conn.commit()
        logger.info(f"Table {table} created")

    def insert_into_table(
            self,
            table: str,
            chat_id: int,
            username: str = "",
            last_message: str = "",
            subscription_system: str | None = None,
            alarm_system: str | None = None,
            currency: str = "usd",
    ):
        update_fields = []

        if username:
            update_fields.append("username")
        if subscription_system:
            update_fields.append("subscription_system")
        if alarm_system:
            update_fields.append("alarm_system")
        if last_message:
            update_fields.append("last_message")
        if currency:
            update_fields.append("currency")

        updates_sql = sql.SQL(",\n  ").join(
            sql.SQL("{} = EXCLUDED.{}").format(sql.Identifier(field), sql.Identifier(field))
            for field in update_fields
        )

        sql_insert = sql.SQL(
            """INSERT INTO {table} (id, username, subscription_system, alarm_system, last_message, currency)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id)
            DO UPDATE SET 
            {updates}
            ;"""
        ).format(
            table=sql.Identifier(table),
            updates=updates_sql
        )

        self.cursor.execute(sql_insert, (chat_id, username, subscription_system, alarm_system, last_message, currency))
        self.conn.commit()

    def select_from_table(self, table: str):
        sql_select = sql.SQL("SELECT * FROM {}").format(sql.Identifier(table))
        self.cursor.execute(sql_select)
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.conn.close()


pg_client = PGClient()
