import numpy as np
import pandas as pd
from typing import Callable

CurveReducer = Callable[[np.ndarray], float]

def tail_mean(m: np.ndarray):
    l = int(m.shape[0] * 0.1)
    return float(np.mean(m[l:]))

def getCurveReducer(reducer: str | CurveReducer) -> CurveReducer:
    if reducer == 'auc':
        return np.mean

    if reducer == 'end':
        return tail_mean

    if isinstance(reducer, str):
        raise Exception("Unknown reducer type")

    return reducer

def reduceCurve(df: pd.DataFrame, col: str, reducer: str | CurveReducer):
    cr = getCurveReducer(reducer)
    d = df[col].apply(cr)
    return np.asarray(d)

def getBest(data: np.ndarray, prefer: str):
    if prefer == 'big':
        return data.argmax()

    elif prefer == 'small':
        return data.argmin()

    raise Exception('Unknown getBest preference')
