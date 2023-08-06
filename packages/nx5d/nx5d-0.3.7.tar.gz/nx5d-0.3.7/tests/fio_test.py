#!/usr/bin/python3

import pytest
import nx5d.h5like.petra3 as p3

@pytest.fixture
def fio_file():
    return 'tests/test_data/fioh5/m3_2507_00744.fio'

def test_fio_parser(fio_file):
    ''' Reading/parsing a FIO file '''
    
    pars, data = p3.read_fio(fio_file)

    assert data['om'].shape[0] == 61
    assert type(pars['om']) == float
    
    #print("Got FIO:", data)

    
def test_fio_loadh5(fio_file):

    fh = p3.FioH5(fio_file)

    assert "fio" in fh.keys()
    
    assert len(fh['fio'].keys()) == 2
    assert len(fh['fio/parameters']) > 10
    assert "om" in fh['fio/parameters'].keys()
    assert "om" in fh['fio/data'].keys()

    assert "lambda_00000" in fh.keys()
    
    a = fh['lambda_00000']['entry']
    b = fh['lambda_00000/entry']

    assert a.keys() == b.keys()

    data = fh['lambda_00000/entry/instrument/detector/mock_data'][()]

    # Very simple test of retrieving the data -- we know this to be the shape
    # of 'mock_data' of the test dataset. Real datasets have a different field
    # ("data") with different shapes, of course.
    assert data.shape == (61, 100, 100)

    assert data.shape[0] == fh['fio/data/om'].shape[0]
