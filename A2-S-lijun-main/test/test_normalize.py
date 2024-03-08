import pandas as pd
from mec import normalize


def test_split_recipients():
    contributions = pd.DataFrame.from_records(
        [
            {
                "MECID": "C12345",
                "Committee Name": "Committee A",
                "Date": pd.Timestamp("2019-01-01"),
                "Amount": 100,
            },
            {
                "MECID": "C12345",
                "Committee Name": "Committee A's New Committee Name",
                "Date": pd.Timestamp("2020-01-01"),
                "Amount": 200,
            },
            {
                "MECID": "C56789",
                "Committee Name": "Committee B",
                "Date": pd.Timestamp("2019-01-01"),
                "Amount": 200,
            },
        ],
    )
    pd.testing.assert_frame_equal(
        normalize.split_recipients(contributions),
        pd.DataFrame(
            {
                "Committee Name": ["Committee A's New Committee Name", "Committee B"],
            },
            index=pd.Index(["C12345", "C56789"], name="MECID"),
        ),
    )


def test_split_contributors():
    contributions = pd.DataFrame(
        {
            "First Name": ["JOHN", "JOHN", None, None],
            "Last Name": ["DOE", "DOE", None, None],
            "Committee": [None, None, "COMMITTEE A", None],
            "Company": [None, None, None, "COMPANY Z"],
            "Employer": ["RETIRED", "RETIRED", None, None],
            "Occupation": ["RETIRED", "RETIRED", None, None],
        },
        index=pd.Index(["1", "2", "3", "4"], name="CD1_A ID"),
    )
    contributors = normalize.split_contributors(contributions)
    pd.testing.assert_frame_equal(
        contributors["Individual"],
        pd.DataFrame(
            {
                "First Name": ["JOHN"],
                "Last Name": ["DOE"],
                "Employer": ["RETIRED"],
                "Occupation": ["RETIRED"],
            },
        ),
    )
    pd.testing.assert_frame_equal(
        contributors["Companies"],
        pd.DataFrame({"Name": ["COMPANY Z"]}),
    )
    pd.testing.assert_frame_equal(
        contributors["Committees"],
        pd.DataFrame({"Name": ["COMMITTEE A"]}),
    )


def test_split_addresses():
    contributions = pd.DataFrame.from_records(
        [
            {
                "Address 1": "1 BROOKINGS DR",
                "Address 2": "",
                "City": "ST LOUIS",
                "State": "MO",
                "Zip": "63118",
                "Amount": 100,
            },
            {
                "Address 1": "1 BROOKINGS DR",
                "Address 2": "",
                "City": "ST LOUIS",
                "State": "MO",
                "Zip": "63118",
                "Amount": 100,
            },
            {
                "Address 1": "1 BROOKINGS DR",
                "Address 2": "",
                "City": "KANSAS CITY",
                "State": "MO",
                "Zip": "64030",
                "Amount": 100,
            },
            {
                "Address 1": "1 BROOKINGS DR",
                "Address 2": "",
                "City": "CLAYTON",
                "State": "MO",
                "Zip": "63118",
                "Amount": 100,
            },
        ],
    )
    index = pd.MultiIndex.from_frame(
        pd.DataFrame(
            {
                "Street Address": ["1 BROOKINGS DR", "1 BROOKINGS DR"],
                "Zip": ["63118", "64030"],
            },
        ),
    )
    pd.testing.assert_frame_equal(
        normalize.split_addresses(contributions),
        pd.DataFrame(
            {
                "City": ["ST LOUIS", "KANSAS CITY"],
                "State": ["MO", "MO"],
            },
            index=index,
        ),
    )


def test_trim_contributions():
    contributions = pd.DataFrame(
        {
            "MECID": ["C12345"],
            "Committee Name": ["A"],
            "Committee": [None],
            "Company": [None],
            "First Name": ["JOHN"],
            "Last Name": ["DOE"],
            "Street Address": ["123 MAIN ST"],
            "City": ["ST LOUIS"],
            "State": ["MO"],
            "Zip": ["63118"],
            "Date": [pd.Timestamp("01-01-2000")],
            "Amount": [100.0],
            "Occupation": ["STUDENT"],
            "Employer": ["WUSTL"],
        },
        index=pd.Index([1], name="CD1_A ID"),
    )
    individuals = pd.DataFrame(
        {
            "ID": [0],
            "First Name": ["JOHN"],
            "Last Name": ["DOE"],
            "Occupation": ["STUDENT"],
            "Employer": ["WUSTL"],
        },
    )
    contributions = normalize.trim_contributions(contributions, individuals)
    pd.testing.assert_frame_equal(
        contributions,
        pd.DataFrame(
            {
                "MECID": ["C12345"],
                "Street Address": ["123 MAIN ST"],
                "Zip": ["63118"],
                "Date": [pd.Timestamp("01-01-2000")],
                "Amount": [100.0],
                "Contributor Type": ["Individual"],
                "Contributor ID": [0],
            },
            index=pd.Index([1], name="CD1_A ID"),
        ),
    )


def test_contributor_address_mapping():
    contributor_ids = pd.DataFrame(
        {"Type": ["Individual", "Individual", "Company"], "ID": [0, 1, 0]},
    )
    contributors = {
        "Individual": pd.DataFrame(
            {
                "First Name": ["John", "Jane"],
                "Last Name": ["Doe", "Doe"],
                "Employer": ["WUSTL"] * 2,
                "Occupation": ["Student"] * 2,
                "ID": [0, 1],
            },
        ),
        "Companies": pd.DataFrame({"Name": ["Company Z"], "ID": [0]}),
        "Committees": pd.DataFrame({"Name": [], "ID": []}),
    }
    addresses = pd.DataFrame(
        {
            "Street Address": ["123 MAIN ST", "456 1ST ST"],
            "Zip": ["12345", "12345"],
            "City": ["ST LOUIS", "ST LOUIS"],
            "State": ["MO", "MO"],
        },
    ).set_index(["Street Address", "Zip"])
    contributions = pd.DataFrame(
        {
            "First Name": ["John", "Jane", None],
            "Last Name": ["Doe", "Doe", None],
            "Company": [None, None, "Company Z"],
            "Street Address": ["123 MAIN ST", "456 1ST ST", "789 BROADWAY BLVD"],
            "Zip": ["12345", "12345", "67890"],
            "City": ["ST LOUIS", "ST LOUIS", "ST LOUIS"],
            "State": ["MO", "MO", "MO"],
            "Amount": [100, 200, 300],
        },
    )
    pd.testing.assert_frame_equal(
        normalize.contributor_address_mapping(
            contributions,
            contributors=contributors,
            addresses=addresses,
            contributor_ids=contributor_ids,
        ),
        pd.DataFrame(
            {
                "Contributor Type": [
                    "Individual",
                    "Individual",
                    "Company",
                ],
                "Contributor ID": [0, 1, 0],
                "Street Address": ["123 MAIN ST", "456 1ST ST", "789 BROADWAY BLVD"],
                "Zip": ["12345", "12345", "67890"],
            },
        ),
    )


def test_mecid_mapping():
    contributing_committees = pd.DataFrame({"Name": ["Committee A"]})
    recipients = pd.DataFrame(
        {
            "Committee Name": ["Committee A"],
        },
        index=pd.Index(["C12345"], name="MECID"),
    )
    pd.testing.assert_frame_equal(
        normalize.mecid_mapping(contributing_committees, recipients),
        pd.DataFrame(
            {
                "MECID": ["C12345"],
                "Name": ["Committee A"],
            },
        ),
    )


def test_normalize(mocker):
    trim_contributions_spy = mocker.spy(normalize, "trim_contributions")
    split_recipients_spy = mocker.spy(normalize, "split_recipients")
    split_contributors_spy = mocker.spy(normalize, "split_contributors")
    mecid_mapping_spy = mocker.spy(normalize, "mecid_mapping")

    contributions = pd.DataFrame.from_records(
        [
            {
                "MECID": "C12345",
                "Committee Name": "COMMITTEE A",
                "Committee": None,
                "Company": None,
                "First Name": "John",
                "Last Name": "Doe",
                "Street Address": "123 MAIN ST",
                "Address 1": "123 MAIN ST",
                "Address 2": "",
                "City": "ST LOUIS",
                "State": "MO",
                "Zip": "63118",
                "Date": "2019-01-01",
                "Amount": 100,
                "Occupation": "Student",
                "Employer": "WUSTL",
            },
            {
                "MECID": "C67890",
                "Committee Name": "COMMITTEE B",
                "Committee": "COMMITTEE A",
                "Company": None,
                "First Name": None,
                "Last Name": None,
                "Address 1": "456 1ST ST",
                "Address 2": "",
                "City": "ST LOUIS",
                "State": "MO",
                "Zip": "63118",
                "Date": "2019-01-01",
                "Amount": 100,
                "Employer": None,
                "Occupation": None,
            },
            {
                "MECID": "C12345",
                "Committee Name": "COMMITTEE A",
                "Committee": None,
                "Company": None,
                "First Name": "Jane",
                "Last Name": "Doe",
                "Street Address": "123 MAIN ST",
                "Address 1": "123 MAIN ST",
                "Address 2": "",
                "City": "ST LOUIS",
                "State": "MO",
                "Zip": "63118",
                "Date": "2019-01-01",
                "Amount": 100,
                "Employer": "WUSTL",
                "Occupation": "Student",
            },
        ],
        index=pd.Index([1, 2, 3], name="CD1_A ID"),
    )
    contributions = normalize.normalize(contributions)

    individuals = contributions["Individual"]
    pd.testing.assert_frame_equal(
        individuals,
        pd.DataFrame(
            {
                "First Name": ["John", "Jane"],
                "Last Name": ["Doe", "Doe"],
                "Employer": ["WUSTL", "WUSTL"],
                "Occupation": ["Student", "Student"],
            },
        ),
    )
    pd.testing.assert_frame_equal(
        contributions["Addresses"],
        pd.DataFrame(
            {
                "Street Address": ["123 MAIN ST", "456 1ST ST"],
                "Zip": ["63118"] * 2,
                "City": ["ST LOUIS"] * 2,
                "State": ["MO"] * 2,
            },
        ).set_index(["Street Address", "Zip"]),
    )
    pd.testing.assert_frame_equal(
        contributions["Contributions"],
        pd.DataFrame(
            {
                "MECID": ["C12345", "C67890", "C12345"],
                "Street Address": ["123 MAIN ST", "456 1ST ST", "123 MAIN ST"],
                "Zip": ["63118"] * 3,
                "Contributor Type": ["Individual", "Committee", "Individual"],
                "Contributor ID": [0, 0, 1],
                "Date": ["2019-01-01"] * 3,
                "Amount": [100] * 3,
            },
            index=pd.Index([1, 2, 3], name="CD1_A ID"),
        ),
        check_like=True,
    )
    pd.testing.assert_frame_equal(
        contributions["Committees"],
        pd.DataFrame(
            {
                "MECID": ["C12345"],
                "Name": ["COMMITTEE A"],
            },
        ),
    )
    pd.testing.assert_frame_equal(
        contributions["Companies"],
        pd.DataFrame(
            {
                "Name": [],
            },
            dtype=str,
        ),
    )
    pd.testing.assert_frame_equal(
        contributions["Recipients"],
        pd.DataFrame(
            {
                "Name": ["COMMITTEE A", "COMMITTEE B"],
            },
            index=pd.Index(["C12345", "C67890"], name="MECID"),
        ),
    )
    assert trim_contributions_spy.call_count > 0
    assert split_recipients_spy.call_count > 0
    assert split_contributors_spy.call_count > 0
    assert mecid_mapping_spy.call_count > 0
