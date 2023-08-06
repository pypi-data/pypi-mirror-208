import json
from typing import Optional

from deci_common.abstractions.base_model import Schema


class InferencerBenchmarkResult(Schema):
    batch_size: Optional[int] = None
    batch_inf_time: Optional[float] = None
    batch_inf_time_variance: Optional[float] = None

    memory: Optional[float] = None

    pre_inference_memory_used: Optional[float] = None
    post_inference_memory_used: Optional[float] = None
    total_memory_size: Optional[float] = None
    throughput: Optional[float] = None
    sample_inf_time: Optional[float] = None
    include_io: Optional[bool] = None
    framework_type: Optional[str] = None
    framework_version: Optional[str] = None
    inference_hardware: Optional[str] = None
    infery_version: Optional[str] = None
    date: Optional[str] = None
    ctime: Optional[int] = None
    h_to_d_mean: Optional[float] = None
    d_to_h_mean: Optional[float] = None
    h_to_d_variance: Optional[float] = None
    d_to_h_variance: Optional[float] = None

    def __str__(self) -> str:
        benchmarks_dict = self.dict()

        # Adding ms and fps to __repr__ output.
        results_benchmarks_dict = dict()
        for k, v in benchmarks_dict.items():
            if isinstance(v, float):
                if k == "throughput":
                    results_benchmarks_dict[k] = f"{v:.2f} fps"
                elif "memory" in k:
                    results_benchmarks_dict[k] = f"{v:.2f} mb"
                else:
                    results_benchmarks_dict[k] = f"{v:.2f} ms"
            else:
                results_benchmarks_dict[k] = v

        return f"<ModelBenchmarks: {json.dumps(results_benchmarks_dict, indent=4)}>"

    def __repr__(self) -> str:
        return str(self)
