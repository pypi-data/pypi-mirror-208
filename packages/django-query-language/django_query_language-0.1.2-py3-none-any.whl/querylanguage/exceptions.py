class FieldDoesNotExist(Exception):
    def __init__(self, field):
        self.field = field
        super().__init__("Field '%s' does not exist" % field)

class InvalidQuery(Exception):
    def __init__(self):
        super().__init__("Invalid query")

class InvalidLiteral(Exception):
    def __init__(self):
        super().__init__("Invalid Literal")