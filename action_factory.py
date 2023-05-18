from job_manager import JobManager


class Action_Factory():
    jm = JobManager()
    _action_factory_dict = {
        'add': jm.add_job_number,
        'remove': jm.remove_job_number,
        'unlock': jm.dc.trigger_unlock_node_job,
        'abort': jm.dc.jk.stop_job,
        'rebuild': jm.start_rebuild_job,
        'open': jm.open_chrome,
    }

    def __init__(self, action):
        self.action = self._action_factory_dict[action]

    # class function
    @classmethod
    def get_actions(cls):
        return cls._action_factory_dict.keys()

    def __call__(self, target):
        return self.action(target)
