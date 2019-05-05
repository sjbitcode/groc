import pytest


@pytest.fixture
def create_csvs(tmp_path):
    # Create two directories.
    csv_dir = tmp_path / "csv_files"
    csv_dir.mkdir()
    csv_dir_sub = csv_dir / "nested"
    csv_dir_sub.mkdir()

    # Create some test csv files.
    file1 = csv_dir / "foo.csv"
    file2 = csv_dir / "bar.csv"
    file3 = csv_dir_sub / "foo.csv"
    file1.touch()
    file2.touch()
    file3.touch()

    return (csv_dir, [file1, file2, file3])
