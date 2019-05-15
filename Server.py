# vuvuzela central

class Server:
    def __init__(self, server_count, etc):
        self.server_count = server_count # number of servers to simulate
        self.keys = self.generate_keys(self.server_count) # [ ( public, secret ) ]
        self.clients = None # ports to connect to  [ ( client_id, tcp_port ) ]
        self.sockets = None # point of contact with clients
        self.deadrop = None # array based on constraing values

        self.publish()

    # generate @count pairs of keys
    def generate_keys(self, count):
        raise NotImplementedError

    # wrapper for openssl lib function
    def _decrypt(self, key, value):
        raise NotImplementedError

    # get round objects from each client
    def run_round_collect(self, ETC):
        raise NotImplementedError

    # send drops back to clients
    def run_round_distribute(self, ETC):
        raise NotImplementedError

    # placeholder for related functions
    def network_func(self, ETC):
        raise NotImplementedError

    # send 
    def publish(self):
        raise NotImplementedError

