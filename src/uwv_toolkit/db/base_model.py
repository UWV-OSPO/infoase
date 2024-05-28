from datetime import datetime
from .database import (
    Database,
)  # Assuming this is correctly importing your custom Database class


class BaseModel:
    """
    Base model class for interacting with a database table.
    """

    db: Database = None
    table_name: str = None
    fields: dict = {
        "date_created": "TEXT",
        "date_updated": "TEXT",
    }

    def __init__(self, **kwargs):
        """
        Initializes a new instance of the BaseModel class.
        """
        self._check_properties()

        # Set model fields along with default timestamps if not provided
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        for field in self.fields:
            if field in ["date_created", "date_updated"]:
                setattr(self, field, kwargs.get(field, now))
            else:
                setattr(self, field, kwargs.get(field))
        self.id = kwargs.get("id")

    @classmethod
    def _check_properties(cls):
        """
        Checks if the required properties of the model are set.
        """
        if not cls.db:
            raise ValueError("Database not set")
        if not cls.table_name:
            raise ValueError("Table name not set")
        if not cls.fields:
            raise ValueError("Fields not set")

    @classmethod
    def create_table(cls):
        """
        Creates the database table for the model.
        """
        cls._check_properties()

        # Include automatic fields in table creation
        columns = ", ".join(
            [
                f"{field_name} {properties}"
                for field_name, properties in cls.fields.items()
            ]
        )
        cls.db.execute(
            f"CREATE TABLE IF NOT EXISTS {cls.table_name} (id INTEGER PRIMARY KEY, {columns})"
        )

    @classmethod
    def all(cls):
        """
        Retrieves all records from the database table.
        """
        cls._check_properties()

        cls.db.execute(f"SELECT * FROM {cls.table_name}")
        return [
            cls(**dict(zip(cls.fields.keys(), row[1:])), id=row[0])
            for row in cls.db.fetchall()
        ]

    @classmethod
    def find(cls, id):
        """
        Retrieves a record from the database table by its ID.
        """
        cls._check_properties()

        cls.db.execute(f"SELECT * FROM {cls.table_name} WHERE id = ?", (id,))
        row = cls.db.fetchone()
        if row:
            return cls(**dict(zip(cls.fields.keys(), row[1:])), id=row[0])

    def save(self):
        """
        Saves the model instance to the database.
        """
        self._check_properties()

        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        if self.id:
            # Update existing record and set date_updated
            set_clause = ", ".join(
                [f"{field} = ?" for field in self.fields if field != "date_created"]
            )
            self.db.execute(
                f"UPDATE {self.table_name} SET {set_clause}, date_updated = ? WHERE id = ?",
                (
                    *[
                        getattr(self, field)
                        for field in self.fields
                        if field != "date_created"
                    ],
                    now,
                    self.id,
                ),
            )
        else:
            # Insert new record with current timestamp for date_created and date_updated
            columns = ", ".join(self.fields.keys())
            placeholders = ", ".join(["?" for _ in self.fields])
            values = [getattr(self, field) for field in self.fields]
            self.db.execute(
                f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})",
                values,
            )
            self.id = self.db.cursor.lastrowid
            self.date_created = now  # Set internally after insert
        self.date_updated = now  # Update internally regardless of insert or update

    def delete(self):
        """
        Deletes the model instance from the database.
        """
        self._check_properties()

        if self.id:
            self.db.execute(f"DELETE FROM {self.table_name} WHERE id = ?", (self.id,))
