# Vuvuzela client

class Client:
    def __init__(self, ETC): # TODO: args
        self.id = None
        self.key = self.generate_key(1) # [ ( public, secret ) ]
        self.partner = self.get_partner()
        self.partnet = None # TODO: tcp socket to server?


    # listen-print-eval-loop
    def listen(self):
        raise NotImplementedError


    # generate pair of keys for this client
    def generate_key(self, count):
        raise NotImplementedError

    # query dispatch for its partner (may be none)
    def get_partner(self):
        raise NotImplementedError

    # query user for message to send
    def collect_message(self):
        raise NotImplementedError
    
    # instantiate round struct
    def create_round(self):
        raise NotImplementedError

    # instantiate noise message 
    def create_round_noise(self):
        raise NotImplementedError

    # send up to server
    def send_round(self):
        raise NotImplementedError

    # collect server
    def collect_round(self):
        raise NotImplementedError

    # wrappers for openssl
    def encrypt(self):
        raise NotImplementedError

    def decrypt(self):
        raise NotImplementedError


