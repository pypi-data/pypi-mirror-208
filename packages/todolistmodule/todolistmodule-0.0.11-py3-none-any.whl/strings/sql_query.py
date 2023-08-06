CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS
todolist_table (task_id INTEGER PRIMARY KEY AUTOINCREMENT
, text_task TEXT, type_task TEXT)
"""

CREATE = "INSERT INTO todolist_table (text_task, type_task) VALUES (?, ?)"

READ_ONE = "SELECT task_id, text_task, type_task FROM todolist_table"

READ_ALL = "SELECT text_task, type_task FROM todolist_table WHERE task_id="

UPDATE = "UPDATE todolist_table SET text_task=?, type_task=? WHERE task_id=?"

DELETE = "DELETE FROM todolist_table WHERE task_id = ?"
