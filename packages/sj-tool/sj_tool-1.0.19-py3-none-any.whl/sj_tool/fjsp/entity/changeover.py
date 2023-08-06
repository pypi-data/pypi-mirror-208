from typing import Dict


class Changeover(object):
    def __init__(self):
        self.info = {}

    def add(self, pre_model, pre_op_type, post_model, cur_op_type, machine, time_length):
        self.info[(pre_model, pre_op_type, post_model, cur_op_type, machine)] = time_length

    def get(self, pre_model, pre_op_type, post_model, cur_op_type, machine):
        if (pre_model, pre_op_type, post_model, cur_op_type, machine) not in self.info:
            return 0
        return self.info[(pre_model, pre_op_type, post_model, cur_op_type, machine)]
