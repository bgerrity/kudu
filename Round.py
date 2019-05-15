# Represents a data structure sent to server every round

# consider rename

class Round:
    def __init__(self):
        # internal use
        self._round_number = None # FIXME: query server for round number?
        self._sender = None
        self._receiver = None # might not be used

        # user values
        self.deadrop_destination = None # dest address
        self.message = None
        self.deadrop_collect = None # request address
    
    # checks destination, message, and collect for validity against constraints
    def validate(self):
        # TODO: implement
        raise NotImplementedError

