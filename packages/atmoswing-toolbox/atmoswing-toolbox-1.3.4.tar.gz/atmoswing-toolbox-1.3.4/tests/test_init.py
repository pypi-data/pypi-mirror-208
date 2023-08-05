import tempfile

from atmoswing_toolbox.datasets import GenericDataset


def test_module_import():
    with tempfile.TemporaryDirectory() as tmp_dir:
        GenericDataset(directory=tmp_dir, var_name=None, ref_data=None)
