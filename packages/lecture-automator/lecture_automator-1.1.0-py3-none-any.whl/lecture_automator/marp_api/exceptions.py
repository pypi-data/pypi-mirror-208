class MarpError(Exception):
    def __init__(self, stdout, stderr, *args: object) -> None:
        super().__init__(*args)
        self.stdout = stdout
        self.stderr = stderr
