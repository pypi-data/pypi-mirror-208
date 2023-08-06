from upyog.ml.imports import *


__all__ = ["compare_state_dicts", "set_bn_eval"]


ModuleOrWeights = Union[nn.Module, OrderedDict]

def compare_state_dicts(
    m1: ModuleOrWeights, m2: ModuleOrWeights, verbose=True, name: str = "models"
) -> bool:
    mismatch_keys = []
    m1 = m1.state_dict() if isinstance(m1, nn.Module) else m1
    m2 = m2.state_dict() if isinstance(m2, nn.Module) else m2

    for (k1, m1v), (k2, m2v) in zip(m1.items(), m2.items()):
        assert k1 == k2, f"Key mismatch, looks like you're comparing different models"
        if not torch.equal(m1v.cpu(), m2v.cpu()):
            logger.error(
                f"Mismatch in <fg #0F77A9>{name}</> in layer <fg #0F77A9>{k1}</>"
            )
            mismatch_keys.append(k1)

    if not mismatch_keys == []:
        err_msg = f"Weights didn't match exactly in {len(mismatch_keys)} layers: {mismatch_keys}"
        raise RuntimeError(err_msg if verbose else "")
    logger.success(f"`state_dict`s of both <fg #0F77A9>{name} </> match!")
    return True


BN_LAYER_TYPES = (nn.BatchNorm1d, nn.BatchNorm2d, nn.BatchNorm3d)
def set_bn_eval(m: nn.Module) -> None:
    "Set bn layers in eval mode for all recursive children of `m`."
    for l in m.children():
        if isinstance(l, BN_LAYER_TYPES) and not next(l.parameters()).requires_grad:
            l.eval()
        set_bn_eval(l)
