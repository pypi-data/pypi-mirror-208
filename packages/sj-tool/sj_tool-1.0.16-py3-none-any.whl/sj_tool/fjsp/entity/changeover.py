from typing import Dict


class Changeover(object):
    def __init__(self):
        self.info = {}

    def add(self, pre_model, pre_op_type, post_model, cur_op_type, machine, processing_time):
        self.info[(pre_model, pre_op_type, post_model, cur_op_type, machine)] = processing_time

    def get(self, pre_model, pre_op_type, post_model, cur_op_type, machine):
        return self.info[(pre_model, pre_op_type, post_model, cur_op_type, machine)]
