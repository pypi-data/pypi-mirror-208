from typing import Union


class BaseProduct(object):
    def __init__(self, idx: Union[int, str], name: Union[int, str], model: Union[int, str]):
        self.id = idx
        self.name = name
        self.model = model  # 产品类型
        self.start_process = 0
        self.end_process = -1
        self.next_op_dict = {}  # 所需要工序 {op 编号: [下道工序 op 编号]}
        self.pre_op_dict = {}  # 所需要工序 {op 编号: [上道工序 op 编号]}
        self.operations = []
