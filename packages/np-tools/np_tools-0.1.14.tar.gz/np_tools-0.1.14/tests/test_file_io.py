import pytest
import np_logging

from np_tools import *

TEST_BYTES = b'test'
EMPTY_BYTES = b''

@pytest.fixture
def src_dir(tmp_path):
    src = tmp_path / 'src'
    src.mkdir()
    return src

@pytest.fixture
def dest_dir(tmp_path):
    dest_dir = tmp_path / 'dest'
    dest_dir.mkdir()
    return dest_dir

@pytest.fixture
def src_file(src_dir):
    src_file = src_dir / 'test.txt'
    src_file.write_bytes(TEST_BYTES)
    return src_file

@pytest.fixture
def empty_dest_file(dest_dir, src_file):
    empty_dest_file = dest_dir / src_file.name
    empty_dest_file.write_bytes(EMPTY_BYTES)
    return empty_dest_file

def dest_matches_src(src, dest):
    if not src.is_dir():
        return dest.read_bytes() == src.read_bytes()
    for src_path in src.rglob('*'):
        dest_path = dest / src_path.relative_to(src)
        assert dest_path.exists()
        if src_path.is_dir():
            continue
        assert dest_path.read_bytes() == src_path.read_bytes()
    return True

def test_copy_dir_to_dir(src_file, dest_dir):
    copy(src_file.parent, dest_dir)
    assert dest_matches_src(src_file.parent, dest_dir)
    
def test_copy_file_to_dir(dest_dir, src_file):
    copy(src_file, dest_dir)
    assert dest_matches_src(src_file.parent, dest_dir)

def test_copy_file_to_file(src_file, dest_dir):
    copy(src_file, dest_dir / src_file.name)
    assert dest_matches_src(src_file.parent, dest_dir)

def test_copy_dir_to_non_existant_dir(src_file, tmp_path):
    dest = tmp_path / 'dest'
    copy(src_file, dest)
    assert dest_matches_src(src_file.parent, dest)
    
def test_copy_file_to_existing_file(src_file, empty_dest_file):
    copy(src_file, empty_dest_file.parent)
    assert dest_matches_src(src_file.parent, empty_dest_file.parent)
    
def test_move_dir(src_file, dest_dir):
    try:
        move(src_file.parent, dest_dir)
    except PermissionError:
        pass
    else:
        assert not src_file.parent.exists()
        assert (dest_dir / src_file.name).read_bytes() == TEST_BYTES
    
def test_move_file(src_file, dest_dir):
    try:
        move(src_file, dest_dir)
    except PermissionError:
        pass
    else:
        assert not src_file.exists()
        assert src_file.parent.exists()
        assert (dest_dir / src_file.name).read_bytes() == TEST_BYTES