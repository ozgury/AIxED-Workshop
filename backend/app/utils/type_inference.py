import numpy as np
from sqlalchemy import BigInteger, Boolean, Column, DateTime, Float, Text


def pandas_dtype_to_sqlalchemy(dtype, col_name: str) -> Column:
    dtype_str = str(dtype)

    if "int" in dtype_str:
        return Column(col_name, BigInteger)
    elif "float" in dtype_str:
        return Column(col_name, Float)
    elif "bool" in dtype_str:
        return Column(col_name, Boolean)
    elif "datetime" in dtype_str:
        return Column(col_name, DateTime(timezone=True))
    else:
        return Column(col_name, Text)


def clean_value(val):
    if val is None:
        return None
    if isinstance(val, float) and (np.isnan(val) or np.isinf(val)):
        return None
    if hasattr(val, "item"):
        return val.item()
    return val
