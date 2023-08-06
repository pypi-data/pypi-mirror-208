"""Firepup650's SQL Package"""
import sqlite3, ast, pydoc


def alias(Function):
    def decorator(f):
        f.__doc__ = (
            "This method is an alias of the following method:\n\n"
            + pydoc.text.document(Function)
        )
        return f

    return decorator


__VERSION__ = "1.0.26"
__NEW__ = "Adds `remove_prefix` and `remove_suffix`, name mangles internal variables in `sql`, fixes a bug in `console.warn`, adds `__VERSION__`, `__NEW__`, and `__LICENSE__`, adds many aliases for interactive help."
__LICENSE__ = "MIT"


class sql:
    """# Class: sql
    Easy SQL manipulation"""

    def addTable(self, tableName: str) -> None:
        """# Function: sql.addTable
          Adds a table to the database
        # Inputs:
          tableName: str - The name of the table to create

        # Returns:
          None

        # Raises:
          None"""
        self.__con.execute(
            f"""CREATE TABLE IF NOT EXISTS "{tableName}"
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                value TEXT NOT NULL)"""
        )
        self.__con.commit()
        self.__table = tableName

    def __init__(self, filename: str):
        """# Function: sql.__init__
          Constructs an SQL instance
        # Inputs:
          filename: str - The name of the database file to connect to (or `:memory:`)

        # Returns:
          None

        # Raises:
          None"""
        if filename.endswith(".db") or filename == ":memory:":
            self.__db = filename
        else:
            self.__db = filename + ".db"
        self.__con = sqlite3.connect(self.__db)
        self.addTable("default")

    def setTable(self, tableName: str) -> None:
        """# Function: sql.setTable
          Sets the currently active table
        # Inputs:
          tableName: str - The name of the table to use

        # Returns:
          None

        # Raises:
          None"""
        self.__table = tableName

    def get(self, name: str) -> object or None:
        """# Function: sql.get
          Gets the value of a key
        # Inputs:
          name: str - The name of the key to retrieve

        # Returns:
          object or None - If the key exists, return it's value, otherwise, return `None`

        # Raises:
          AttributeError - If the table is unset"""
        if not self.__table:
            raise AttributeError("Attempted to read from unset table")
        cur = self.__con.execute(
            f"""SELECT value FROM "{self.__table}" WHERE name = ?""", (name,)
        )
        data = cur.fetchone()
        if data:
            try:
                return ast.literal_eval(data[0])
            except:
                return data[0]
        return None

    def set(self, name: str, value: object) -> int:
        """# Function: sql.set
          Sets the value of a key
        # Inputs:
          name: str - The name of the key to set
          value: object - The value of the key

        # Returns:
          int - `1` if the key was created, `2` if it was updated

        # Raises:
          AttributeError - If the table is unset"""
        if not self.__table:
            raise AttributeError("Attempted to write to unset table")
        if self.get(name):
            self.__con.execute(
                f"""UPDATE "{self.__table}" SET value = ? WHERE name = ?""",
                (str(value), name),
            )
            self.__con.commit()
            return 2
        else:
            self.__con.execute(
                f"""INSERT INTO "{self.__table}" (name, value) VALUES (?, ?)""",
                (name, str(value)),
            )
            self.__con.commit()
            return 1

    def delete(self, name: str) -> None:
        """# Function: sql.delete
          Deletes a key from the table
        # Inputs:
          name: str - The name of the key to delete

        # Returns:
          None

        # Raises:
          AttributeError - If the table is unset"""
        if not self.__table:
            raise AttributeError("Attempted to delete from unset table")
        if self.get(name):
            self.__con.execute(
                f"""DELETE FROM "{self.__table}" WHERE name = ?""", (name,)
            )
            self.__con.commit()

    def delete_all(self) -> None:
        """# Function: sql.delete_all
          Deletes all keys from the table
        # Inputs:
          None

        # Returns:
          None

        # Raises:
          AttributeError - If the table is unset"""
        if not self.__table:
            raise AttributeError("Attempted to delete from unset table")
        self.__con.execute(f"""DELETE FROM "{self.__table}" """)
        self.__con.commit()

    def close(self) -> None:
        """# Function: sql.close
          Closes the database connection
        # Inputs:
          None

        # Returns:
          None

        # Raises:
          None"""
        self.__con.close()
        self.__con = None
        self.__db = None
        self.__table = None
