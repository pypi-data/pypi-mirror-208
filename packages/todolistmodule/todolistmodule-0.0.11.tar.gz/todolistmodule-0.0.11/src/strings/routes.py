# flake8: noqa

CREATE = "/api/v1/task/create/task_type/<string:task_type>/task_descript/<string:task_descript>"

READ = "/api/v1/task/read/task_id/<int:task_id>"

UPDATE = "/api/v1/task/update/task_id/<int:task_id>/task_type/<string:task_type>/task_descript/<string:task_descript>"

DELETE = "/api/v1/task/delete/task_id/<int:task_id>"
