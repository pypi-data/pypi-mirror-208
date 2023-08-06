from typing import Any
from typing import Dict
from typing import Optional
from typing import Set
from typing import Type

import numpy as np
import torch

from enot_lite.backend import Backend
from enot_lite.backend import BackendFactory
from enot_lite.backend.ort_cuda import OrtCudaBackend
from enot_lite.backend.ort_tensorrt import OrtTensorrtBackend
from enot_lite.backend.tensorrt import TensorrtBackend
from enot_lite.benchmark.backend_runner import BackendRunner
from enot_lite.benchmark.backend_runner import EnotBackendRunner
from enot_lite.benchmark.backend_runner import TorchCpuRunner
from enot_lite.benchmark.backend_runner import TorchCudaRunner
from enot_lite.type import BackendType
from enot_lite.type import ModelType

__all__ = [
    'OrtCpuBackendRunnerBuilder',
    'OrtOpenvinoBackendRunnerBuilder',
    'OpenvinoBackendRunnerBuilder',
    'OrtCudaBackendRunnerBuilder',
    'OrtTensorrtBackendRunnerBuilder',
    'OrtTensorrtFp16BackendRunnerBuilder',
    'TensorrtBackendRunnerBuilder',
    'TensorrtFp16BackendRunnerBuilder',
    'AutoCpuBackendRunnerBuilder',
    'AutoGpuBackendRunnerBuilder',
    'TorchCpuBackendRunnerBuilder',
    'TorchCudaBackendRunnerBuilder',
]


def _print_data_transfer_notes(no_data_transfer: bool) -> None:
    if no_data_transfer:
        print(
            'no_data_transfer is True. Final result will not include transfer time of input/output data.',
            flush=True,
            end=' ',
        )
    else:
        print(
            'no_data_transfer is False. Final result will include transfer '
            'time of input data from host to device and output data from '
            'device to host.',
            flush=True,
            end=' ',
        )


class CommonEnotBackendRunnerBuilder:  # pylint: disable=missing-class-docstring
    def __init__(self, backend_type: BackendType, kwargs_key_filter: Optional[Set[str]] = None):
        self._backend_type = backend_type
        self._kwargs_key_filter = kwargs_key_filter

    def __call__(
        self,
        onnx_model,
        onnx_input: Dict[str, Any],
        model_type: ModelType,
        enot_backend_runner: Type[EnotBackendRunner],
        no_data_transfer: bool = False,
        **kwargs,
    ) -> BackendRunner:
        if self._kwargs_key_filter is not None:
            kwargs = {key: kwargs[key] for key in self._kwargs_key_filter if key in kwargs}

        backend = BackendFactory().create(
            model=onnx_model,
            backend_type=self._backend_type,
            model_type=model_type,
            input_example=onnx_input,
            **kwargs,
        )

        if self._is_gpu_backend(backend):
            _print_data_transfer_notes(no_data_transfer)
            if no_data_transfer:
                gpu_onnx_input = {}
                for k, v in onnx_input.items():
                    if isinstance(v, np.ndarray):
                        gpu_onnx_input[k] = torch.from_numpy(v).cuda()
                    elif isinstance(v, torch.Tensor):
                        gpu_onnx_input[k] = v.cuda()
                    else:
                        gpu_onnx_input[k] = v

                onnx_input = gpu_onnx_input

        return enot_backend_runner(backend, onnx_input)

    @staticmethod
    def _is_gpu_backend(backend: Backend) -> bool:
        return isinstance(backend, (OrtCudaBackend, OrtTensorrtBackend, TensorrtBackend))


class OrtCpuBackendRunnerBuilder(CommonEnotBackendRunnerBuilder):  # pylint: disable=missing-class-docstring
    def __init__(self):
        kwargs_key_filter = {'inter_op_num_threads', 'intra_op_num_threads'}
        super().__init__(BackendType.ORT_CPU, kwargs_key_filter=kwargs_key_filter)


class OrtOpenvinoBackendRunnerBuilder(CommonEnotBackendRunnerBuilder):  # pylint: disable=missing-class-docstring
    def __init__(self):
        kwargs_key_filter = {'inter_op_num_threads', 'intra_op_num_threads', 'openvino_num_threads'}
        super().__init__(BackendType.ORT_OPENVINO, kwargs_key_filter=kwargs_key_filter)


class OpenvinoBackendRunnerBuilder(CommonEnotBackendRunnerBuilder):  # pylint: disable=missing-class-docstring
    def __init__(self):
        super().__init__(BackendType.OPENVINO, kwargs_key_filter=set())


class OrtCudaBackendRunnerBuilder(CommonEnotBackendRunnerBuilder):  # pylint: disable=missing-class-docstring
    def __init__(self):
        super().__init__(BackendType.ORT_CUDA, kwargs_key_filter=set())


class OrtTensorrtBackendRunnerBuilder(CommonEnotBackendRunnerBuilder):  # pylint: disable=missing-class-docstring
    def __init__(self):
        super().__init__(BackendType.ORT_TENSORRT, kwargs_key_filter=set())


class OrtTensorrtFp16BackendRunnerBuilder(CommonEnotBackendRunnerBuilder):  # pylint: disable=missing-class-docstring
    def __init__(self):
        super().__init__(BackendType.ORT_TENSORRT_FP16, kwargs_key_filter=set())


class TensorrtBackendRunnerBuilder(CommonEnotBackendRunnerBuilder):  # pylint: disable=missing-class-docstring
    def __init__(self):
        super().__init__(BackendType.TENSORRT, kwargs_key_filter=set())


class TensorrtFp16BackendRunnerBuilder(CommonEnotBackendRunnerBuilder):  # pylint: disable=missing-class-docstring
    def __init__(self):
        super().__init__(BackendType.TENSORRT_FP16, kwargs_key_filter=set())


class AutoCpuBackendRunnerBuilder(CommonEnotBackendRunnerBuilder):  # pylint: disable=missing-class-docstring
    def __init__(self):
        super().__init__(BackendType.AUTO_CPU, kwargs_key_filter=set())


class AutoGpuBackendRunnerBuilder(CommonEnotBackendRunnerBuilder):  # pylint: disable=missing-class-docstring
    def __init__(self):
        super().__init__(BackendType.AUTO_GPU, kwargs_key_filter=set())


class TorchCpuBackendRunnerBuilder:  # pylint: disable=missing-class-docstring
    def __call__(
        self,
        torch_model,
        torch_input,
        torch_cpu_runner: Type[TorchCpuRunner],
        **_ignored,
    ) -> BackendRunner:
        return torch_cpu_runner(torch_model=torch_model, torch_input=torch_input)


class TorchCudaBackendRunnerBuilder:  # pylint: disable=missing-class-docstring
    def __call__(
        self,
        torch_model,
        torch_input,
        torch_cuda_runner: Type[TorchCudaRunner],
        no_data_transfer: bool = False,
        **_ignored,
    ) -> BackendRunner:
        _print_data_transfer_notes(no_data_transfer)
        return torch_cuda_runner(torch_model=torch_model, torch_input=torch_input, no_data_transfer=no_data_transfer)
