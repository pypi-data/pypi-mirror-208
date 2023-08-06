from typing import List
from typing import Union


class BaseMachine(object):
    def __init__(self, idx, name, available_ops: List[Union[str, int]] = None, unit_times=None):
        """

        :param machine_id:
        :param available_ops:
        """
        self.id = idx
        self.name = name
        self.unit_times = {} if unit_times is None else unit_times  # {('product_id','process_id'):单个的节拍 }
        self.available_ops = [] if available_ops is None else available_ops
        self.scheduled_ops = []
