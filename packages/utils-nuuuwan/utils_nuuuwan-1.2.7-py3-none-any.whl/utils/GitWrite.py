from utils.Log import Log

log = Log('Git')


class GitWrite:
    @property
    def cmd_git_push(self):
        assert self.branch_name is not None
        return f'git push origin {self.branch_name}'

    def push(self):
        self.run(
            self.cmd_cd,
            self.cmd_git_push,
        )
