class BoolStore:
    """
    Stores a boolean value, to be accessed globally
    """

    def __init__(self):
        self.state = False

    def __bool__(self):
        return self.state

    def __repr__(self):
        return str(self.state)


Quiet = BoolStore()
