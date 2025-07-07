#coding:utf-8

"""
ID:          optimizer.inner-join-02
TITLE:       INNER JOIN join order
DESCRIPTION:
  With a INNER JOIN the table with the smallest expected result should be the first one in
  process order. When all tables have the same avg. recordsize (recordformat) the next table
  should be the second smallest. Note that calculation is based on page-size. Thus for tables
  which use the same nr. of data-pages, but have in reality different nr. of records
  the table N could be bigger as table N+1 in the order.
FBTEST:      functional.arno.optimizer.opt_inner_join_02
NOTES:
    [07.07.2025] pzotov
    Refactored: explained plan is used to be checked in expected_out.
    Added ability to use several queries and their datasets for check - see 'qry_list' and 'qry_data' tuples.
    Separated expected output for FB major versions prior/since 6.x.
    No substitutions are used to suppress schema and quotes. Discussed with dimitr, 24.06.2025 12:39.
    Checked on 6.0.0.914; 5.0.3.1668; 4.0.6.3214; 3.0.13.33813
"""

import pytest
from firebird.qa import *

init_script = """
    CREATE TABLE Table_10 (
      ID INTEGER NOT NULL
    );

    CREATE TABLE Table_100 (
      ID INTEGER NOT NULL
    );

    CREATE TABLE Table_3K (
      ID INTEGER NOT NULL
    );

    SET TERM ^^ ;
    CREATE PROCEDURE PR_FillTable_10
    AS
    DECLARE VARIABLE FillID INTEGER;
    BEGIN
      FillID = 1;
      WHILE (FillID <= 10) DO
      BEGIN
        INSERT INTO Table_10 (ID) VALUES (:FillID);
        FillID = FillID + 1;
      END
    END
    ^^

    CREATE PROCEDURE PR_FillTable_100
    AS
    DECLARE VARIABLE FillID INTEGER;
    BEGIN
      FillID = 1;
      WHILE (FillID <= 100) DO
      BEGIN
        INSERT INTO Table_100 (ID) VALUES (:FillID);
        FillID = FillID + 1;
      END
    END
    ^^

    CREATE PROCEDURE PR_FillTable_3K
    AS
    DECLARE VARIABLE FillID INTEGER;
    BEGIN
      FillID = 1;
      WHILE (FillID <= 3000) DO
      BEGIN
        INSERT INTO Table_3K (ID) VALUES (:FillID);
        FillID = FillID + 1;
      END
    END
    ^^
    SET TERM ; ^^

    COMMIT;

    EXECUTE PROCEDURE PR_FillTable_10;
    EXECUTE PROCEDURE PR_FillTable_100;
    EXECUTE PROCEDURE PR_FillTable_3K;

    COMMIT;

    CREATE UNIQUE ASC INDEX PK_Table_10 ON Table_10 (ID);
    CREATE UNIQUE ASC INDEX PK_Table_100 ON Table_100 (ID);
    CREATE UNIQUE ASC INDEX PK_Table_3K ON Table_3K (ID);

    COMMIT;
"""

db = db_factory(init=init_script)

qry_list = (
    """
    SELECT
      Count(*)
    FROM
      Table_3K t3K
      JOIN Table_100 t100 ON (t100.ID = t3K.ID)
    JOIN Table_10 t10 ON (t10.ID = t100.ID)
    """,
)
data_list = (
    """
    COUNT : 10
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

                # ::: NB ::: 'ps' returns data, i.e. this is SELECTABLE expression.
                # We have to store result of cur.execute(<psInstance>) in order to
                # close it explicitly.
                # Otherwise AV can occur during Python garbage collection and this
                # causes pytest to hang on its final point.
                # Explained by hvlad, email 26.10.24 17:42
                rs = cur.execute(ps)
                cur_cols = cur.description
                for r in rs:
                    for i in range(0,len(cur_cols)):
                        print( cur_cols[i][0], ':', r[i] )

            except DatabaseError as e:
                print(e.__str__())
                print(e.gds_codes)
            finally:
                if rs:
                    rs.close() # <<< EXPLICITLY CLOSING CURSOR RESULTS
                if ps:
                    ps.free()

    expected_out_4x = f"""
        {qry_list[0]}
        Select Expression
        ....-> Aggregate
        ........-> Nested Loop Join (inner)
        ............-> Table "TABLE_10" as "T10" Full Scan
        ............-> Filter
        ................-> Table "TABLE_100" as "T100" Access By ID
        ....................-> Bitmap
        ........................-> Index "PK_TABLE_100" Unique Scan
        ............-> Filter
        ................-> Table "TABLE_3K" as "T3K" Access By ID
        ....................-> Bitmap
        ........................-> Index "PK_TABLE_3K" Unique Scan
        {data_list[0]}
    """

    expected_out_5x = f"""
        {qry_list[0]}
        Select Expression
        ....-> Aggregate
        ........-> Nested Loop Join (inner)
        ............-> Table "TABLE_10" as "T10" Full Scan
        ............-> Filter
        ................-> Table "TABLE_100" as "T100" Access By ID
        ....................-> Bitmap
        ........................-> Index "PK_TABLE_100" Unique Scan
        ............-> Filter
        ................-> Table "TABLE_3K" as "T3K" Access By ID
        ....................-> Bitmap
        ........................-> Index "PK_TABLE_3K" Unique Scan
        {data_list[0]}
    """

    expected_out_6x = f"""
        {qry_list[0]}
        Select Expression
        ....-> Aggregate
        ........-> Nested Loop Join (inner)
        ............-> Table "PUBLIC"."TABLE_10" as "T10" Full Scan
        ............-> Filter
        ................-> Table "PUBLIC"."TABLE_100" as "T100" Access By ID
        ....................-> Bitmap
        ........................-> Index "PUBLIC"."PK_TABLE_100" Unique Scan
        ............-> Filter
        ................-> Table "PUBLIC"."TABLE_3K" as "T3K" Access By ID
        ....................-> Bitmap
        ........................-> Index "PUBLIC"."PK_TABLE_3K" Unique Scan
        {data_list[0]}
    """

    act.expected_stdout = expected_out_4x if act.is_version('<5') else expected_out_5x if act.is_version('<6') else expected_out_6x
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
