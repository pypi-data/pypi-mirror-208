from typing import Dict


class BaseProcess(object):
    def __init__(self, process_id: int, name: str):
        self.process_id = process_id  # 工序id
        self.name = name  # 工序名称
