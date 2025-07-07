#coding:utf-8

"""
ID:          optimizer.aggregate-distribution-02
TITLE:       Try to deliver HAVING CLAUSE conjunctions to the WHERE clause
DESCRIPTION:
  Comparisons which doesn't contain (anywhere hiding in the expression) aggregate-functions
  should be delivered to the where clause. The underlying aggregate stream could possible
  use it for a index and speed it up.
FBTEST:      functional.arno.optimizer.opt_aggregate_distribution_02
NOTES:
    [07.07.2025] pzotov
    Refactored: explained plan is used to be checked in expected_out.
    Added ability to use several queries for check - see 'qry_list' tuple.
    Separated expected output for FB major versions prior/since 6.x.
    No substitutions are used to suppress schema and quotes. Discussed with dimitr, 24.06.2025 12:39.
    Checked on 6.0.0.914; 5.0.3.1668; 4.0.6.3214; 3.0.13.33813
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
INSERT INTO Colors (ColorID, ColorName) VALUES (2, 'White');
INSERT INTO Colors (ColorID, ColorName) VALUES (3, 'Blue');
INSERT INTO Colors (ColorID, ColorName) VALUES (4, 'Yellow');
INSERT INTO Colors (ColorID, ColorName) VALUES (5, 'Black');
INSERT INTO Colors (ColorID, ColorName) VALUES (6, 'Purple');

/* insert some data with references */
INSERT INTO Flowers (FlowerID, FlowerName, ColorID) VALUES (1, 'Red Rose', 1);
INSERT INTO Flowers (FlowerID, FlowerName, ColorID) VALUES (2, 'White Rose', 2);
INSERT INTO Flowers (FlowerID, FlowerName, ColorID) VALUES (3, 'Blue Rose', 3);
INSERT INTO Flowers (FlowerID, FlowerName, ColorID) VALUES (4, 'Yellow Rose', 4);
INSERT INTO Flowers (FlowerID, FlowerName, ColorID) VALUES (5, 'Black Rose', 5);
INSERT INTO Flowers (FlowerID, FlowerName, ColorID) VALUES (6, 'Red Tulip', 1);
INSERT INTO Flowers (FlowerID, FlowerName, ColorID) VALUES (7, 'White Tulip', 2);
INSERT INTO Flowers (FlowerID, FlowerName, ColorID) VALUES (8, 'Yellow Tulip', 4);
INSERT INTO Flowers (FlowerID, FlowerName, ColorID) VALUES (9, 'Blue Gerbera', 3);
INSERT INTO Flowers (FlowerID, FlowerName, ColorID) VALUES (10, 'Purple Gerbera', 6);

COMMIT;

/* Normally these indexes are created by the primary/foreign keys,
   but we don't want to rely on them for this test */
CREATE UNIQUE ASC INDEX PK_Colors ON Colors (ColorID);
CREATE UNIQUE ASC INDEX PK_Flowers ON Flowers (FlowerID);
CREATE ASC INDEX FK_Flowers_Colors ON Flowers (ColorID);

COMMIT;
"""

db = db_factory(init=init_script)

qry_list = (
    """
    select
        f.colorid,
        c.colorname,
        count(*)
    from flowers f
    left join colors c on (c.colorid = f.colorid)
    group by
        f.colorid, c.colorname
    having
        count(*) >= 2 and
        min(f.flowerid) >= 1 and
        max(f.flowerid) >= 1 and
        avg(f.flowerid) >= 1 and
        count(distinct f.flowerid) >= 2 and
        min(distinct f.flowerid) >= 1 and
        max(distinct f.flowerid) >= 1 and
        avg(distinct f.flowerid) >= 1;
    """,
)

substitutions = [ ( r'\(record length: \d+, key length: \d+\)', 'record length: N, key length: M' ) ]
act = python_act('db', substitutions = substitutions)

#-----------------------------------------------------------

def replace_leading(source, char="."):
    stripped = source.lstrip()
    return char * (len(source) - len(stripped)) + stripped

#-----------------------------------------------------------

@pytest.mark.version('>=3.0')
def test_1(act: Action, capsys):
    with act.db.connect() as con:
        cur = con.cursor()
        for test_sql in qry_list:
            ps, rs =  None, None
            try:
                cur = con.cursor()
                ps = cur.prepare(test_sql)
                print(test_sql)
                # Print explained plan with padding eash line by dots in order to see indentations:
                print( '\n'.join([replace_leading(s) for s in ps.detailed_plan.split('\n')]) )
            except DatabaseError as e:
                print(e.__str__())
                print(e.gds_codes)
            finally:
                if rs:
                    rs.close() # <<< EXPLICITLY CLOSING CURSOR RESULTS
                if ps:
                    ps.free()

    expected_out_5x = f"""
        {qry_list[0]}
        Select Expression
        ....-> Filter
        ........-> Aggregate
        ............-> Sort (record length: 86, key length: 36)
        ................-> Nested Loop Join (outer)
        ....................-> Table "FLOWERS" as "F" Full Scan
        ....................-> Filter
        ........................-> Table "COLORS" as "C" Access By ID
        ............................-> Bitmap
        ................................-> Index "PK_COLORS" Unique Scan
    """

    expected_out_6x = f"""
        {qry_list[0]}
        Select Expression
        ....-> Filter
        ........-> Aggregate
        ............-> Sort (record length: 86, key length: 36)
        ................-> Nested Loop Join (outer)
        ....................-> Table "PUBLIC"."FLOWERS" as "F" Full Scan
        ....................-> Filter
        ........................-> Table "PUBLIC"."COLORS" as "C" Access By ID
        ............................-> Bitmap
        ................................-> Index "PUBLIC"."PK_COLORS" Unique Scan
    """

    act.expected_stdout = expected_out_5x if act.is_version('<6') else expected_out_6x
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout



'''
act = isql_act('db', test_script)

expected_stdout = """PLAN SORT (JOIN (F NATURAL, C INDEX (PK_COLORS)))

     COLORID COLORNAME                            COUNT
============ ==================== =====================
           1 Red                                      2
           2 White                                    2
           3 Blue                                     2
           4 Yellow                                   2
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
'''
