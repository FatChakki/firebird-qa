#coding:utf-8

"""
ID:          optimizer.inner-join-07
TITLE:       INNER JOIN join order and VIEW
DESCRIPTION:
  With a INNER JOIN the relation with the smallest expected result should be the first one
  in process order. The next relation should be the next relation with expected smallest
  result based on previous relation and do on till last relation.
  Old/Current limitation in Firebird does stop checking order possibilties above 7 relations.
FBTEST:      functional.arno.optimizer.opt_inner_join_07
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
    CREATE TABLE Table_1 (
      ID INTEGER NOT NULL
    );

    CREATE TABLE Table_1K (
      ID INTEGER NOT NULL
    );

    CREATE TABLE Table_2K (
      ID INTEGER NOT NULL
    );

    CREATE TABLE Table_3K (
      ID INTEGER NOT NULL
    );

    CREATE TABLE Table_4K (
      ID INTEGER NOT NULL
    );

    CREATE TABLE Table_5K (
      ID INTEGER NOT NULL
    );

    CREATE TABLE Table_6K (
      ID INTEGER NOT NULL
    );

    CREATE TABLE Table_8K (
      ID INTEGER NOT NULL
    );

    CREATE TABLE Table_10K (
      ID INTEGER NOT NULL
    );

    SET TERM ^ ;
    CREATE PROCEDURE PR_FillTable_10K
    AS
    DECLARE VARIABLE FillID INTEGER;
    BEGIN
      FillID = 1;
      WHILE (FillID <= 10000) DO
      BEGIN
        INSERT INTO Table_10K (ID) VALUES (:FillID);
        FillID = FillID + 1;
      END
    END
    ^
    SET TERM ; ^
    COMMIT;

    CREATE VIEW View_A (
      ID1K,
      ID6K
    )
    AS
    SELECT
      t1K.ID,
      t6K.ID
    FROM
      Table_6K t6K
      JOIN Table_1K t1K ON (t1K.ID = t6K.ID);

    CREATE VIEW View_B (
      ID3K,
      ID10K
    )
    AS
    SELECT
      t3K.ID,
      t10K.ID
    FROM
      Table_3K t3K
      JOIN Table_10K t10K ON (t10K.ID = t3K.ID);
    COMMIT;

    INSERT INTO Table_1 (ID) VALUES (1);
    EXECUTE PROCEDURE PR_FillTable_10K;
    INSERT INTO Table_1K (ID) SELECT ID FROM Table_10K WHERE ID <= 1000;
    INSERT INTO Table_2K (ID) SELECT ID FROM Table_10K WHERE ID <= 2000;
    INSERT INTO Table_3K (ID) SELECT ID FROM Table_10K WHERE ID <= 3000;
    INSERT INTO Table_4K (ID) SELECT ID FROM Table_10K WHERE ID <= 4000;
    INSERT INTO Table_5K (ID) SELECT ID FROM Table_10K WHERE ID <= 5000;
    INSERT INTO Table_6K (ID) SELECT ID FROM Table_10K WHERE ID <= 6000;
    INSERT INTO Table_8K (ID) SELECT ID FROM Table_10K WHERE ID <= 8000;
    COMMIT;

    CREATE UNIQUE ASC INDEX PK_Table_1 ON Table_1 (ID);
    CREATE UNIQUE ASC INDEX PK_Table_1K ON Table_1K (ID);
    CREATE UNIQUE ASC INDEX PK_Table_2K ON Table_2K (ID);
    CREATE UNIQUE ASC INDEX PK_Table_3K ON Table_3K (ID);
    CREATE UNIQUE ASC INDEX PK_Table_4K ON Table_4K (ID);
    CREATE UNIQUE ASC INDEX PK_Table_5K ON Table_5K (ID);
    CREATE UNIQUE ASC INDEX PK_Table_6K ON Table_6K (ID);
    CREATE UNIQUE ASC INDEX PK_Table_8K ON Table_8K (ID);
    CREATE UNIQUE ASC INDEX PK_Table_10K ON Table_10K (ID);
    COMMIT;
"""

db = db_factory(init=init_script)

qry_list = (
    """
    SELECT
      Count(*)
    FROM
      View_B vb
    JOIN View_A va ON (va.ID1K = vb.ID10K)
    """,
)
data_list = (
    """
    COUNT : 1000
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
        ............-> Table "TABLE_1K" as "VA T1K" Full Scan
        ............-> Filter
        ................-> Table "TABLE_3K" as "VB T3K" Access By ID
        ....................-> Bitmap
        ........................-> Index "PK_TABLE_3K" Unique Scan
        ............-> Filter
        ................-> Table "TABLE_6K" as "VA T6K" Access By ID
        ....................-> Bitmap
        ........................-> Index "PK_TABLE_6K" Unique Scan
        ............-> Filter
        ................-> Table "TABLE_10K" as "VB T10K" Access By ID
        ....................-> Bitmap
        ........................-> Index "PK_TABLE_10K" Unique Scan
        {data_list[0]}
    """

    expected_out_5x = f"""
        {qry_list[0]}
        Select Expression
        ....-> Aggregate
        ........-> Nested Loop Join (inner)
        ............-> Table "TABLE_1K" as "VA T1K" Full Scan
        ............-> Filter
        ................-> Table "TABLE_3K" as "VB T3K" Access By ID
        ....................-> Bitmap
        ........................-> Index "PK_TABLE_3K" Unique Scan
        ............-> Filter
        ................-> Table "TABLE_6K" as "VA T6K" Access By ID
        ....................-> Bitmap
        ........................-> Index "PK_TABLE_6K" Unique Scan
        ............-> Filter
        ................-> Table "TABLE_10K" as "VB T10K" Access By ID
        ....................-> Bitmap
        ........................-> Index "PK_TABLE_10K" Unique Scan
        {data_list[0]}
    """

    expected_out_6x = f"""
        {qry_list[0]}
        Select Expression
        ....-> Aggregate
        ........-> Nested Loop Join (inner)
        ............-> Table "PUBLIC"."TABLE_1K" as "VA" "T1K" Full Scan
        ............-> Filter
        ................-> Table "PUBLIC"."TABLE_3K" as "VB" "T3K" Access By ID
        ....................-> Bitmap
        ........................-> Index "PUBLIC"."PK_TABLE_3K" Unique Scan
        ............-> Filter
        ................-> Table "PUBLIC"."TABLE_6K" as "VA" "T6K" Access By ID
        ....................-> Bitmap
        ........................-> Index "PUBLIC"."PK_TABLE_6K" Unique Scan
        ............-> Filter
        ................-> Table "PUBLIC"."TABLE_10K" as "VB" "T10K" Access By ID
        ....................-> Bitmap
        ........................-> Index "PUBLIC"."PK_TABLE_10K" Unique Scan
        {data_list[0]}
    """

    act.expected_stdout = expected_out_4x if act.is_version('<5') else expected_out_5x if act.is_version('<6') else expected_out_6x
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
