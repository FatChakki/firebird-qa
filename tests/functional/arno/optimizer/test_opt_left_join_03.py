#coding:utf-8

"""
ID:          optimizer.left-join-03
TITLE:       LEFT OUTER JOIN with full match and reference in WHERE clause
DESCRIPTION:
  TableX LEFT OUTER JOIN TableY with full match.
  ON clause contains (1 = 1) and WHERE clause contains relation between TableX and TableY.
  The WHERE comparison should be distributed to TableY. Thus TableY should use the index.
FBTEST:      functional.arno.optimizer.opt_left_join_03
NOTES:
    [31.07.2023] pzotov
    Test was excluded from execution under FB 5.x: no more sense in it for this FB version.
    Discussed with dimitr, letter 30.07.2023.
    Checked finally on 4.0.3.2966, 3.0.11.33695 -- all fine.
"""

import pytest
from firebird.qa import *

init_script = """CREATE TABLE Colors (
  ColorID INTEGER NOT NULL,
  ColorName VARCHAR(20)
);

CREATE TABLE Flowers (
  FlowerID INTEGER NOT NULL,
  FlowerName VARCHAR(30),
  ColorID INTEGER
);

COMMIT;

/* Value 0 represents -no value- */
INSERT INTO Colors (ColorID, ColorName) VALUES (0, 'Not defined');
INSERT INTO Colors (ColorID, ColorName) VALUES (1, 'Red');
INSERT INTO Colors (ColorID, ColorName) VALUES (2, 'Yellow');

/* insert some data with references */
INSERT INTO Flowers (FlowerID, FlowerName, ColorID) VALUES (1, 'Rose', 1);
INSERT INTO Flowers (FlowerID, FlowerName, ColorID) VALUES (2, 'Tulip', 2);
INSERT INTO Flowers (FlowerID, FlowerName, ColorID) VALUES (3, 'Gerbera', 0);

COMMIT;

/* Normally these indexes are created by the primary/foreign keys,
   but we don't want to rely on them for this test */
CREATE UNIQUE ASC INDEX PK_Colors ON Colors (ColorID);
CREATE UNIQUE ASC INDEX PK_Flowers ON Flowers (FlowerID);
CREATE ASC INDEX FK_Flowers_Colors ON Flowers (ColorID);

COMMIT;
"""

db = db_factory(init=init_script)

test_script = """SET PLAN ON;
/* LEFT JOIN should return a match for every Flowers record */
SELECT
  f.FlowerName,
  c.ColorName
FROM
  Flowers f
  LEFT JOIN Colors c ON (1 = 1)
WHERE
f.ColorID = c.ColorID;"""

act = isql_act('db', test_script)

expected_stdout = """PLAN JOIN (F NATURAL, C INDEX (PK_COLORS))
FLOWERNAME                     COLORNAME
============================== ====================

Rose                           Red
Tulip                          Yellow
Gerbera                        Not defined"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    if act.is_version('>=5'):
        pytest.skip("Test has no sense in FB 5.x, see notes.")

    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
