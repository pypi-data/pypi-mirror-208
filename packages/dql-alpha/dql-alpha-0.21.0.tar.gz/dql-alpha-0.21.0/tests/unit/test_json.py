import json

import pytest
from jmespath.exceptions import JMESPathTypeError

from dql.jmes_sql.transpiler import Transpiler

# pylint: disable=unused-argument,redefined-outer-name

cat1 = {
    "class": "cat",
    "id": "1",
    "num_annotators": 5,
    "inference": {"class": "cat", "confidence": 0.45},
}

cat10 = {
    "class": "cat",
    "id": "10",
    "num_annotators": 8,
    "inference": {"class": "dog", "confidence": 0.86},
}

open_image1 = {
    "classifications": [
        {
            "Confidence": 1,
            "LabelName": "/m/0b_rs",
            "Source": "verification",
            "some_score": 0.72,
        },
        {
            "Confidence": 1,
            "LabelName": "/m/0bt9lr",
            "Source": "crowdsource-verification",
            "some_score": 0.38,
        },
        {
            "Confidence": 0,
            "LabelName": "/m/015p6",
            "Source": "verification",
            "some_score": 0.934,
        },
        {
            "Confidence": 1,
            "LabelName": "/m/01lrl",
            "Source": "verification",
            "some_score": 0.394,
        },
        {
            "Confidence": 0,
            "LabelName": "/m/02_n6y",
            "Source": "verification",
            "some_score": 0.38,
        },
    ],
    "detections": [
        {
            "Confidence": 1,
            "IsDepiction": 0,
            "IsGroupOf": 0,
            "IsInside": 0,
            "IsOccluded": 1,
            "IsTruncated": 1,
            "LabelName": "/m/0b_rs",
            "Source": "xclick",
            "XClick1X": 0.0,
            "XClick1Y": 0.998333,
            "XClick2X": 0.99875,
            "XClick2Y": 0.0,
            "XClick3X": 0.99875,
            "XClick3Y": 0.0,
            "XClick4X": 0.99875,
            "XClick4Y": 0.0,
            "XMax": 0.99875,
            "XMin": 0.0,
            "YMax": 0.998333,
            "YMin": 0.0,
        },
        {
            "Confidence": 1,
            "IsDepiction": 0,
            "IsGroupOf": 0,
            "IsInside": 0,
            "IsOccluded": 1,
            "IsTruncated": 1,
            "LabelName": "/m/0bt9lr",
            "Source": "xclick",
            "XClick1X": 0.63625,
            "XClick1Y": 0.268333,
            "XClick2X": 0.90375,
            "XClick2Y": 0.506667,
            "XClick3X": 0.74875,
            "XClick3Y": 0.998333,
            "XClick4X": 0.165,
            "XClick4Y": 0.661667,
            "XMax": 0.90375,
            "XMin": 0.165,
            "YMax": 0.998333,
            "YMin": 0.268333,
        },
    ],
    "id": "0000b9fcba019d36",
    "image_ids": {
        "Author": "O. G.",
        "AuthorProfileURL": "https://www.flickr.com/people/ezlens/",
        "License": "https://creativecommons.org/licenses/by/2.0/",
        "OriginalLandingURL": "https://www.flickr.com/photos/ezlens/50621395",
        "OriginalMD5": "3d9qBaSrX7fN2mag/qpk5w==",
        "OriginalSize": 73392,
        "OriginalURL": "https://farm7.staticflickr.com/29/50621395_874fb9f3ee_o.jpg",  # noqa: E501
        "Rotation": None,
        "Subset": "train",
        "Thumbnail300KURL": "https://c7.staticflickr.com/1/29/50621395_2c80281034_z.jpg?zz=1",  # noqa: E501
        "Title": "DSCN8023",
    },
    "segmentations": [
        {
            "BoxID": "99ba1430",
            "BoxXMax": 0.90375,
            "BoxXMin": 0.165,
            "BoxYMax": 0.998333,
            "BoxYMin": 0.268333,
            "Clicks": "0.64587 0.27696 1;0.36091 0.83590 0;0.76364 0.98524 1;0.85670 0.65910 0;0.31044 0.85548 1;0.69804 0.29354 1;0.76067 0.38381 0;0.87069 0.60723 1;0.70049 0.83122 1;0.75876 0.32617 1;0.49428 0.61008 1",  # noqa: E501
            "LabelName": "/m/0bt9lr",
            "MaskPath": "0000b9fcba019d36_m0bt9lr_99ba1430.png",
            "PredictedIoU": 0.74734,
        }
    ],
    "split": "train",
}


@pytest.fixture
def con(data_storage):
    conn = data_storage.db  # pylint:disable=protected-access

    # These tests re-use the same database for better performance
    result = conn.execute(
        """
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='meta'
        """
    ).fetchall()

    if len(result):
        return conn

    conn.execute(
        """
        CREATE TABLE meta (
            name    VARCHAR,
            data    JSON
        )
        """
    )

    conn.execute(
        "INSERT INTO meta VALUES (?, ?), (?, ?), (?, ?)",
        [
            "cat1",
            json.dumps(cat1),
            "cat10",
            json.dumps(cat10),
            "oi_dog",
            json.dumps(open_image1),
        ],
    )
    conn.commit()
    return conn


def test_basic(con):
    res = con.execute("SELECT COUNT() FROM meta").fetchall()[0][0]
    assert res == 3


def test_confident_cat(con):
    res = con.execute(
        """
        SELECT name
        FROM meta
        WHERE data -> 'inference' ->> 'confidence' > 0.5
    """
    ).fetchall()

    assert len(res) == 1
    assert res[0][0] == "cat10"


def test_func_contains_string_match(con):
    query = "contains(`foobar`, `foo`)"
    cursor = Transpiler.execute_query(con, query, "meta", "data", ["name", "data"])
    res = cursor.fetchall()
    assert len(res) == 3


def test_func_contains_string_missmatch(con):
    query = "contains(`foobar`, `omg`)"
    cursor = Transpiler.execute_query(con, query, "meta", "data", ["name", "data"])
    res = cursor.fetchall()
    assert len(res) == 0


def test_func_contains_string_error(con):
    query = "contains(`false`, `omg`)"
    with pytest.raises(JMESPathTypeError):
        ts = Transpiler("meta", "data", ["name", "data"])
        ts.translate(query)


def test_func_contains_field(con):
    query = "contains(class, `at`)"
    cursor = Transpiler.execute_query(con, query, "meta", "data", ["name", "data"])
    res = cursor.fetchall()

    assert len(res) == 2
    assert {res[0][0], res[1][0]} == {"cat1", "cat10"}


def test_func_contains_field_subexpression(con):
    query = "contains(inference.class, `at`)"
    cursor = Transpiler.execute_query(con, query, "meta", "data", ["name", "data"])
    res = cursor.fetchall()

    assert len(res) == 1
    assert res[0][0] == "cat1"


def test_subexpression_equals_to_string(con):
    query = "inference.class == `dog`"
    cursor = Transpiler.execute_query(con, query, "meta", "data", ["name", "data"])
    res = cursor.fetchall()

    assert len(res) == 1
    assert res[0][0] == "cat10"


def test_subexpression_equals_to_subexpression(con):
    query = "class == inference.class"
    cursor = Transpiler.execute_query(con, query, "meta", "data", ["name", "data"])
    res = cursor.fetchall()

    assert len(res) == 1
    assert res[0][0] == "cat1"


def test_larger_than_a_number(con):
    query = "num_annotators > `6`"
    cursor = Transpiler.execute_query(con, query, "meta", "data", ["name", "data"])
    res = cursor.fetchall()

    assert len(res) == 1
    assert res[0][0] == "cat10"


def test_not_sql_number_larger(con):
    query = "`872` > `539`"
    cursor = Transpiler.execute_query(con, query, "meta", "data", ["name", "data"])
    res = cursor.fetchall()
    assert len(res) == 3


def test_not_sql_number_equal(con):
    query = "`4546` == `4546`"
    cursor = Transpiler.execute_query(con, query, "meta", "data", ["name", "data"])
    res = cursor.fetchall()
    assert len(res) == 3


def test_not_sql_number_larger_error(con):
    query = "`34` > `834`"
    cursor = Transpiler.execute_query(con, query, "meta", "data", ["name", "data"])
    res = cursor.fetchall()
    assert len(res) == 0


def test_func_contains_array(con):
    query = "detections[1].LabelName == `/m/0bt9lr`"
    cursor = Transpiler.execute_query(con, query, "meta", "data", ["name", "data"])
    res = cursor.fetchall()

    assert len(res) == 1
    assert res[0][0] == "oi_dog"


def test_func_contains_array_error(con):
    query = "detections[1].LabelName == `/m/0b_rs`"
    cursor = Transpiler.execute_query(con, query, "meta", "data", ["name", "data"])
    res = cursor.fetchall()
    assert len(res) == 0


def test_jmes_contains_with_projection(con):
    # -- DuckDB solution:
    # SELECT
    #     list_contains(
    #         list_transform(from_json(data -> > 'detections', '["json"]'),
    #                 x -> json_extract_string(json(x), 'LabelName') ),
    #         '/m/0bt9lr')
    # FROM meta

    query = "contains(detections[*].LabelName, `/m/0bt9lr`)"
    cursor = Transpiler.execute_query(con, query, "meta", "data", ["name", "data"])
    res = cursor.fetchall()

    assert len(res) == 1
    assert res[0][0] == "oi_dog"


def test_two_tables():
    # TODO: complete test
    # query = (
    #    "contains(detections[*].LabelName,"
    #    "max_by(classifications, &some_score).LabelName)"
    # )
    pass
