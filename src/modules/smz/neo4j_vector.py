from modules.headingfwd import BaseVector


class Neo4JVector(BaseVector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setup(self):
        pass
