from typing import List, Tuple, Dict, Union


class BaseOperation:
    def __init__(
            self,
            idx: Union[int, str],
            job_id: Union[int, str],
            product_id: Union[int, str],
            demand: Union[int, float],
            process_id: Union[int, str],
            machine_times: Dict,
            pre_ops: List = None,
            next_ops: List = None,
    ):
        """

        :param idx: 工序id
        :param job_id: 工单id

        """
        self.id = idx
        self.job_id = job_id
        self.process_id = process_id
        self.product_id = product_id

        self.pre_ops = [] if pre_ops is None else pre_ops
        self.next_ops = [] if next_ops is None else next_ops
        self.machine_times = machine_times  # 设备处理单位数量所需时间 {"machine_id":float/int}
        self.available_machines = list(machine_times.keys())
        self.demand = demand

        self.op_start = None
        self.op_end = None
