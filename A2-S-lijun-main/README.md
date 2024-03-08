[![Open in Codespaces](https://classroom.github.com/assets/launch-codespace-7f7980b617ed060a017424585567c406b6ee15c891e84e1186181d67ecf80aa0.svg)](https://classroom.github.com/open-in-codespaces?assignment_repo_id=13937755)
# HW2 - Data Normalization

## Missouri Campaign Donation Data

*Due: 3/1/24 5:00 PM*

> Note: This assignment introduces [pre-commit](https://pre-commit.com/) hooks, namely the [Ruff](https://docs.astral.sh/ruff/) linting and formatting hook. This is designed to help you catch errors in your code, but if you want to turn it off, run `pre-commit uninstall` (or to disable for a single commit or push, use the --no-verify flag for the git command). If you fail a check, the hook might make safe changes to your code automatically, and sometimes you may need to confirm the changes by re-adding and re-commiting those files.

### Getting started

The Missouri Ethics Commission (MEC) is responsible for collecting and distributing campaign donation information for state and municipal elections in Missouri. They provide a [download tool](https://mec.mo.gov/MEC/Campaign_Finance/CF_ContrCSV.aspx) which allows you to manually download a CSV of campaign contribution data for a given year's MEC reports, which are collected from the candidates. I have downloaded this data set for every year since 2016 and reuploaded the collection as a compressed file on WUSTL Box.

You may download and unzip the files manually [here](https://wustl.box.com/v/mec-data-2024); however I've provided a utility function `fetch_data` in the module `mec.io` to download the data set. The `fetch_data` script or your manual download should place the data in the directory `data/raw/`.

> Please note that the raw data files are not actually required to pass the automated tests, which are run against unit test case examples. However, downloading the dataset might be helpful to familiarize yourself with the dataset (e.g. in a Jupyter notebook) and familiarize yourself with the Pandas/SQL operations needed to manipulate it.

### I/O

1. Write a function `csv_paths` that returns a list of the filepaths for CSV files in a given directory.

    Use the built-in `pathlib` module and `Path.glob` pattern matching wildcards to obtain the paths for the CSV files (but not the .gitignore file).

    The test provides a temporary directory for testing, however it is a good idea to test your function on the actual data in the `data/raw` directory.

2. Write a function `read_single_csv` that reads a CSV file from a given file path into a DataFrame with the correct indexing and dtypes.

    - Use the `parse_dates` and `index_col` arguments to assign `CD1_A ID` (the ID of the contribution) as the index for the data and parse the `Date` column as a `datetime`.


3. Write a function `load_contributions` that uses the previous two functions to combine CSVs of contribution data from a given directory into a single DataFrame.

    - `pd.concat` accepts a list of DataFrames as input and concatenates them vertically.

    > Note: This data set should be manageable in-memory, however if this is not the case for your machine you may work on this assignment using a subset of the files provided -- the overall logic and code should be exactly the same and will not affect the autograder tests.

    Implement the following intermediate functions to partially normalize the MEC contributions dataset according to the provided specifications. These intermediate functions should then be fed to `normalize(contributions)` run all of the operations at once and return a dictionary containing each of the resulting tables.

### Normalization

4. Implement `split_recipients` to create a normalized table `Recipients` by selecting the relevant columns, grouping on `MECID` and using the most recent name to assign to `Committee Name`.

5. Implement `split_contributors` to return a dictionary that maps the strings `Individual`, `Companies`, and `Committees` to their corresponding (normalized) dataframes.

6. Implement `split_addresses`. Extract the relevant columns and combine `Address 1` and `Address 2` into a single field named `Street Address`. Use `Street Address` and `Zip` as an index, using the most common values to assign to `City` and `State`.

7. Implement `contributor_address_mapping` to create a junction table that links contributors to addresses according to the contribution data.

8. If a contributing committee is in the `Recipients` table, add the MECID to a new column in `Committees`.

9. Implement `trim_contributions` to select only the fields in the `Contributions` table that are relevant to the grain of the table, including all foreign key fields.

10. Implement the function `normalize` to perform the operations and normalize the entire dataset.
