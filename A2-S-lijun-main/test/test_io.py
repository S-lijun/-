from pathlib import Path

import pandas as pd

from mec import io


def test_csv_paths(tmpdir, faker):
    paths = [Path(tmpdir) / Path(faker.file_name(extension="csv")) for _ in range(2)]
    [path.touch() for path in paths]

    assert set(io.csv_paths(Path(tmpdir))) == set(paths)


def test_read_single_csv(tmpdir):
    pd.DataFrame({"CD1_A ID": [1], "Date": ["1/1/2023 12:00:00 AM"]}).to_csv(
        tmpdir / "1.csv",
    )
    contributions = io.read_single_csv(tmpdir / "1.csv")
    assert contributions.index.name == "CD1_A ID"


def test_load_contributions(tmpdir):
    tmpdir = Path(tmpdir)
    pd.DataFrame(
        {"Date": ["1/1/2023 12:00:00 AM"]},
        index=pd.Index([1], name="CD1_A ID"),
    ).to_csv(tmpdir / "1.csv")
    pd.DataFrame(
        {"Date": ["1/1/2023 12:00:00 AM"]},
        index=pd.Index([2], name="CD1_A ID"),
    ).to_csv(tmpdir / "2.csv")
    combined = io.load_contributions(tmpdir)

    pd.testing.assert_frame_equal(
        combined.sort_index(),
        pd.DataFrame(
            {
                "Date": [
                    pd.Timestamp("2023-01-01 00:00:00"),
                    pd.Timestamp("2023-01-01 00:00:00"),
                ],
            },
            index=pd.Index([1, 2], name="CD1_A ID"),
        ),
    )
