from typing import List
from typing import Union


class BaseMachine(object):
    def __init__(
        self, idx, name, available_ops: List[Union[str, int]] = [], unit_times={}
    ):
        """

        :param machine_id:
        :param available_ops:
        """
        self.id = idx
        self.name = name
        self.unit_times = unit_times  # {('product_id','process_id'):单个的节拍 }
        self.available_ops = available_ops
        self.scheduled_ops = []
