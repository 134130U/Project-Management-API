class Storage:
    def upload(self, file):
        raise NotImplementedError
    def get_url(self, key):
        raise NotImplementedError