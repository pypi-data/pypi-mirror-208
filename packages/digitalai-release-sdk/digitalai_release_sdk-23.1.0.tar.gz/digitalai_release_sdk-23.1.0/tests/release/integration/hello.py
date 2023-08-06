from digitalai.release.integration import BaseTask


class Hello(BaseTask):
    """
       The purpose of this task is to greet by the given name.
    """
    def execute(self) -> None:
        name = self.input_properties['yourName']
        if not name:
            raise ValueError("The 'name' field cannot be empty")

        greeting = f"Hello {name}"

        print(f"get_release_server_url() : {self.get_release_server_url()}")
        print(f"get_task_user() : {self.get_task_user()}")
        print(f"get_release_id() : {self.get_release_id()}")
        print(f"get_task_id() : {self.get_task_id()}")

        # Add to the comment section of the task in the UI
        self.add_comment(greeting)

        self.set_output_property('greeting', greeting)

