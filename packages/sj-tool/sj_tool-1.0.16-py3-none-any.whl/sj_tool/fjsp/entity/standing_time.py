class StandingTime(object):
    def __init__(self):
        self.info = {}

    def add(self, product_id, process_id, standing_time):
        self.info[(product_id, process_id)] = standing_time

    def get(self, product_id, process_id):
        return self.info[(product_id, process_id)]