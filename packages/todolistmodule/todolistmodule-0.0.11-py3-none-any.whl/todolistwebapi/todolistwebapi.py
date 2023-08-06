import strings.routes

from flask import Flask
from todolistmodule.todolistdao import ToDoListDAO


app = Flask(__name__)


@app.get("/")
async def example():
    return {"message": "It's me, Mario!"}


@app.route(strings.routes.CREATE, methods=['POST'])
def create(task_descript, task_type):
    task_id = ToDoListDAO().create(
        text_task=task_descript, text_type=task_type)
    return {"message": f"create -> task_id: {task_id} \
            - task_type: {task_type} - task_descript: {task_descript}"}


@app.route(strings.routes.READ, methods=['POST'])
def read(task_id):
    msg = ""
    for result in ToDoListDAO().read(id=task_id):
        msg += f"\n - task_id: {result[0]} \
            - task_type: {result[1]} - task_descript: {result[2]}"
    return {"message": f"read -> { msg }"}


@app.route(strings.routes.UPDATE, methods=['POST'])
def update(task_id, task_descript, task_type):
    flg_returned = ToDoListDAO().update(
        id=task_id, text_task=task_descript, text_type=task_type)
    return {
            "message": f"update -> task_id: {task_id} \
            - task_description: {task_descript} \
            - task_type: {task_type} \
            - bool_return: {flg_returned}"
            }


@app.route(strings.routes.DELETE, methods=['POST'])
def delete(task_id):
    flg_returned = ToDoListDAO().delete(id=1)
    return {"message": f"delete -> task_id: {task_id} \
             - bool_return: {flg_returned}"}


if __name__ == "__main__":
    app.run()
