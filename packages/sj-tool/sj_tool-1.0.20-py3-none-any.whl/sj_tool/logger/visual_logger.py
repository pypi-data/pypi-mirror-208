import wave

import loguru
import numpy as np

from typing import List, Union
from visualdl import LogWriter
from tensorboardX import SummaryWriter


class VisualLogger(object):
    def __init__(self, logdir=None, comment="", use_visualdl=True, text_logger: loguru.logger = None):
        self.writer = LogWriter(logdir, comment) if use_visualdl else SummaryWriter(logdir, comment)
        self.text_logger = text_logger

    def add_scalar(self, tag: str, value: Union[str, int, float], step: int):
        self.writer.add_scalar(tag, value, step)

    def add_image(self, tag: str, img: np.ndarray, step: int):
        self.writer.add_image(tag=tag, img=img, step=step)

    def add_audio(self, tag: str, audio_path: str, step: int):
        _, audio_data = self._read_audio_data(audio_path)
        self.writer.add_audio(tag=tag, audio_array=audio_data, step=step, sample_rate=8000)

    def add_histogram(self, tag: str, values: Union[np.ndarray, List], step: int):
        self.writer.add_histogram(tag=tag, values=values, step=step, buckets=10)

    def add_pr_curve(
        self,
        tag: str,
        labels: Union[np.ndarray, List],
        predictions: Union[np.ndarray, List],
        step: int,
        num_thresholds,
    ):
        self.writer.add_pr_curve(
            tag=tag, labels=labels, predictions=predictions, step=step, num_thresholds=num_thresholds
        )

    def add_hyper_params(self, hparams_dict, metrics_list):
        if not isinstance(self.writer, LogWriter):
            if self.text_logger is not None:
                self.text_logger.error(
                    "Func add_hyper_params is not available when you are not using visualdl.LogWriter"
                )
            return
        self.writer.add_hparams(hparams_dict=hparams_dict, metrics_list=metrics_list)

    def add_hyper_param_value(self, metric, value, step):
        if not isinstance(self.writer, LogWriter):
            if self.text_logger is not None:
                self.text_logger.error(
                    "Func add_hyper_params is not available when you are not using visualdl.LogWriter"
                )
            return
        self.writer.add_scalar(metric, value, step)

    @staticmethod
    def _read_audio_data(audio_path):
        """
        Get audio data.
        """
        CHUNK = 4096
        f = wave.open(audio_path, "rb")
        wavdata = []
        chunk = f.readframes(CHUNK)
        while chunk:
            data = np.frombuffer(chunk, dtype="uint8")
            wavdata.extend(data)
            chunk = f.readframes(CHUNK)
        # 8k sample rate, 16bit frame, 1 channel
        shape = [8000, 2, 1]
        return shape, wavdata
