from dataclasses import dataclass, field
from typing import Dict, Union
from sj_tool.fjsp.entity.job import BaseJob
from sj_tool.fjsp.entity.machine import BaseMachine
from sj_tool.fjsp.entity.operation import BaseOperation
from sj_tool.fjsp.entity.process import BaseProcess
from sj_tool.fjsp.entity.product import BaseProduct
from sj_tool.fjsp.entity.changeover import Changeover
from sj_tool.fjsp.entity.standing_time import StandingTime


@dataclass
class FjspPool:
    # 工单列表
    job_dict: Dict[Union[int, str], BaseJob] = field(default_factory=dict)
    # 工序基础信息
    process_dict: Dict[Union[int, str], BaseProcess] = field(default_factory=dict)
    # operation 列表
    op_dict: Dict[Union[int, str], BaseOperation] = field(default_factory=dict)
    # 机器列表
    machine_dict: Dict[Union[int, str], BaseMachine] = field(default_factory=dict)
    # 产品列表
    product_dict: Dict[Union[int, str], BaseProduct] = field(default_factory=dict)
    # 换型基础信息
    changeover: Changeover = None
    # 静置基础信息
    standing_time: StandingTime = None
