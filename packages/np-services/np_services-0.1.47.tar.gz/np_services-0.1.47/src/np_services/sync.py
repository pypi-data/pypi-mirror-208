import pathlib

import h5py
import pandas as pd
import pydantic
import tables

f = pathlib.Path('//allen/programs/mindscope/workgroups/np-exp/habituation/1253722691_661730_20230313/1253722691_661730_20230313.sync')

h = h5py.File(f, 'r')
t = tables.open_file(f, 'r')
pd.read_hdf(f.as_posix(), 'meta')




class Sync(pydantic.BaseModel):
    pass
    