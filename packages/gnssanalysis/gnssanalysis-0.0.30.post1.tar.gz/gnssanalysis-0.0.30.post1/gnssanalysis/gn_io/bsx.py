from io import BytesIO as _BytesIO

import pandas as _pd

from .. import gn_datetime as _gn_datetime
from .common import path2bytes
from .sinex import _snx_extract_blk


def read_bsx(path):
    bsx_bytes = path2bytes(path)
    bias_blk = _snx_extract_blk(snx_bytes=bsx_bytes, blk_name="BIAS/SOLUTION", remove_header=True)[0]

    bsx_df = _pd.read_fwf(
        _BytesIO(bias_blk),
        infer_nrows=None,
        colspecs=(
            (0, 5),
            (6, 10),
            (11, 14),
            (15, 24),
            (25, 29),
            (30, 34),
            (35, 49),
            (50, 64),
            (65, 69),
            (70, 91),
            (92, 103),
        ),
        header=None,
        comment='*' # COD bia has header duplicated inside the block
    )
    bsx_df.iloc[:, [6, 7]] = _gn_datetime.yydoysec2datetime(bsx_df.iloc[:, [6, 7]].values.reshape((-1))).reshape((-1, 2))

    bsx_df.columns = ["BIAS", "SVN", "PRN", "SITE", "OBS1", "OBS2", "BEGIN", "END", "UNIT", "VAL", "STD"]
    return bsx_df
