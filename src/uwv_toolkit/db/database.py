import sqlite3


class Database:
    def __init__(self, db_name):
        """
        Initialize a Database object.

        Args:
            db_name (str): The name of the database file.
        """
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def execute(self, query, params=()):
        """
        Execute a SQL query.

        Args:
            query (str): The SQL query to execute.
            params (tuple, optional): The parameters to substitute in the query. Defaults to ().

        Usage:
            db.execute("INSERT INTO table_name (column1, column2) VALUES (?, ?)", (value1, value2))
        """
        self.cursor.execute(query, params)
        self.conn.commit()

    def fetchall(self):
        """
        Fetch all rows from the last executed query.

        Returns:
            list: A list of tuples representing the rows.

        Usage:
            rows = db.fetchall()
        """
        return self.cursor.fetchall()

    def fetchone(self):
        """
        Fetch the next row from the last executed query.

        Returns:
            tuple: A tuple representing the row.

        Usage:
            row = db.fetchone()
        """
        return self.cursor.fetchone()

    def close(self):
        """
        Close the database connection.
        """
        self.conn.close()
