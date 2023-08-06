import numpy as np
from emdfile import (
    Node,
    Metadata,
    Array,
    PointList,
    PointListArray
)

from os.path import join,exists
from os import remove
from numpy import array_equal

from emdfile import _TESTPATH
from emdfile import save, read

# Set paths
dirpath = _TESTPATH
testpath = join(dirpath,"test_base_classes.h5")





class TestArray():


    def test_instantiation(self):

        # Array class instances should:
        # - TODO

        shape = (3,4,5)
        d = np.arange(np.prod(shape)).reshape(shape)

        ar = Array(
            data = d
        )
        assert(isinstance(ar, Array))


    def test_Array_comple_readwrite(self):

        # make array
        d = np.exp(1j*np.linspace(0,2*np.pi)).astype(np.complex64)
        ar = Array(
            data = d
        )

        # save, read, check
        save(testpath,ar,mode='o')
        ar2 = read(testpath)
        assert(array_equal(ar.data,ar2.data))





def test_Node():

    # Root class instances should:
    # - have a name
    # - have a Tree
    # - know how to read/write to/from h5

    root = Node()
    assert(isinstance(root,Node))
    ##;passert(root.name == 'root')
    ##;passert(isinstance(root.tree, Tree))

    # h5io


def test_Metadata():

    # Metadata class instances should:
    # - TODO

    metadata = Metadata()
    assert(isinstance(metadata,Metadata))







def test_PointList():

    # PointList class instances should:
    # - TODO

    dtype = [
        ('x',int),
        ('y',float)
    ]
    data = np.zeros(10,dtype=dtype)
    pointlist = PointList(
        data=data
    )
    assert(isinstance(pointlist,PointList))

def test_PointListArray():

    # PointListArray class instance should:
    # - TODO

    dtype = [
        ('x',int),
        ('y',float)
    ]
    shape = (5,5)
    pointlistarray = PointListArray(
        dtype = dtype,
        shape = shape
    )
    assert(isinstance(pointlistarray,PointListArray))








