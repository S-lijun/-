import pathlib
import zipfile
from pathlib import Path
import pandas as pd
import requests


def fetch_data() -> None:
    response = requests.get(
        "https://wustl.box.com/shared/static/fprbb446gvz5znowkrxf6nanze56nco6.zip"
    )
    z = zipfile.ZipFile(io.BytesIO(response.content))
    z.extractall("data/raw")


def csv_paths(csv_dir: pathlib.Path) -> list[pathlib.Path]:
    return [p for p in csv_dir.glob('*.csv') if p.name != ".gitignore"]


def read_single_csv(csv_path: pathlib.Path) -> pd.DataFrame:
    return pd.read_csv(csv_path, index_col = "CD1_A ID", parse_dates = ["Date"])


def load_contributions(csv_dir: pathlib.Path) -> pd.DataFrame:
    
    paths = csv_paths(csv_dir)
    dataframes = [read_single_csv(p) for p in paths]

    return pd.concat(dataframes)
