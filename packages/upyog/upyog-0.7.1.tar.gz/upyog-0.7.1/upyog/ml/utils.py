from upyog.ml.imports import *
from upyog.os import *


__all__ = ["to_np", "to_torch", "save_tensor_to_json"]


def get_num_gpus(gpus: Union[List[int], int]) -> Union[None, int]:
    if is_platform_macos():
        return None
    if gpus == -1:
        return torch.cuda.device_count()
    else:
        assert isinstance(gpus, list)
        return len(gpus)


def to_np(tensor: Tensor, dtype=np.float32):
    if isinstance(tensor, np.ndarray): return tensor
    return tensor.detach().cpu().numpy().astype(dtype)


def to_torch(x) -> Tensor:
    assert isinstance(x, (np.ndarray, torch.Tensor))
    return x.detach() if isinstance(x, torch.Tensor) else torch.from_numpy(x)


def save_tensor_to_json(data: Union[Tensor, np.ndarray], path: PathLike):
    "Save tensor to disk as a JSON file"
    data = to_np(data) if isinstance(data, Tensor) else data
    if not isinstance(data, (Tensor, np.ndarray)):
        raise ValueError(f"Invalid `data` type. Expected tensor/array, got {type(data)}")
    data = data.tolist()

    path = Path(path).with_suffix(".json")
    # path = Path(path)
    # filename = f"{path.stem}.json"  # Ensure extension is .json
    # path = path.parent / filename
    write_json(data, path, indent=None)
