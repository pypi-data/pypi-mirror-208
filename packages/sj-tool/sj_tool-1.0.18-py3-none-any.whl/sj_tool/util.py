import os
import random
import importlib

import numpy as np


def package_exists(package_name):
    """
    检查是否存在某个包
    :param package_name: 包名
    :return:
    """
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False


def set_random_seed(seed: int):
    """
    Setup all possible random seeds so results can be reproduced
    """
    os.environ["PYTHONHASHSEED"] = str(seed)
    # tf.set_random_seed(random_seed) # if you use tensorflow
    random.seed(seed)
    np.random.seed(seed)

    if package_exists("torch"):
        import torch

        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
        torch.manual_seed(seed)

        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
            torch.cuda.manual_seed(seed)
