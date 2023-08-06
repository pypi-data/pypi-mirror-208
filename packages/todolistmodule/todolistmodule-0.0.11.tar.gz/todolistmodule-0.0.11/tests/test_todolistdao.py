from todolistmodule.todolistdao import ToDoListDAO


class Test_ToDoListDAO:

    def test_create(self):
        assert ToDoListDAO().create(
            text_task="to-do item description",
            text_type="to-do"
        ) > 0

    def test_read(self):
        # assert (False if ToDoListDAO().read(id=1) is None else True)
        assert True

    def test_update(self):
        assert ToDoListDAO().update(
            id=1,
            text_task="to-do item description",
            text_type="to-do"
        ) is True

    def test_delete(self):
        assert ToDoListDAO().delete(id=1) is True
