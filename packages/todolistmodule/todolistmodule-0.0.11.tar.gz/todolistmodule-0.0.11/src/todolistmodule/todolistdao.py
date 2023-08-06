import sqlite3
import strings.sql_query


class ToDoListDAO:

    """Todo list - Task management"""

    def __init__(self):
        """Todo operations init"""
        self.conn = None
        self.cursor = None
        self.create_table()

    def open_connection(self):
        """Open connection on database"""
        self.conn = sqlite3.connect('todolist.db')
        self.cursor = self.conn.cursor()

    def create_table(self):
        """Create table on database"""
        try:
            self.open_connection()
            self.cursor.execute(strings.sql_query.CREATE_TABLE)
            self.conn.commit()
        except sqlite3.Error as e:
            print("Erro ao inserir registro:", e)
            self.conn.rollback()
        finally:
            self.conn.close()

    def create(self, text_task: str = '', text_type: str = ''):
        """Create some task for todo"""
        try:
            self.open_connection()
            self.cursor.execute(
                strings.sql_query.CREATE,
                (text_task, text_type)
            )
            self.conn.commit()
            inserted_id = self.cursor.lastrowid
            return inserted_id
        except sqlite3.Error as e:
            print("Erro ao inserir registro:", e)
            self.conn.rollback()
        finally:
            self.conn.close()

    def read(self, id: int = 0):
        """Read some task item for todo"""
        try:
            self.open_connection()
            if id == 0:
                self.cursor.execute(strings.sql_query.READ_ALL)
            elif id > 0:
                self.cursor.execute(strings.sql_query.READ_ONE, (id,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print("Erro ao inserir registro:", e)
            self.conn.rollback()
        finally:
            self.conn.close()

    def update(self, id: int, text_task: str, text_type: str):
        """Update a task item in todo"""
        try:
            self.open_connection()
            self.cursor.execute(
                strings.sql_query.UPDATE,
                (text_task, text_type, id)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print("Erro ao atualizar registro:", e)
            self.conn.rollback()
            return False
        finally:
            self.conn.close()

    def delete(self, id: int = 0):
        """Delete some task for todo"""
        try:
            self.open_connection()
            self.cursor.execute(strings.sql_query.DELETE, (id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print("Erro ao inserir registro:", e)
            self.conn.rollback()
            return False
        finally:
            self.conn.close()
