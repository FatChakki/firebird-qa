#coding:utf-8

"""
ID:          issue-5878
ISSUE:       5878
TITLE:       Gradual slowdown compilation (create, recreate or drop) of views
DESCRIPTION:
JIRA:        CORE-5612
FBTEST:      bugs.core_5612
NOTES:
    [25.07.2025] pzotov
    Separated expected output for check on versions prior/since 6.x.
    Checked on 6.0.0.1061; 5.0.3.1686; 4.0.6.3223.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set list on;
    set count on;
    select ri.rdb$index_id idx_id,rs.rdb$field_position pos, rs.rdb$field_name key
    from rdb$indices ri
    left join rdb$index_segments rs on ri.rdb$index_name = rs.rdb$index_name
    where ri.rdb$relation_name = upper('rdb$dependencies')
    order by 1,2;
"""

act = isql_act('db', test_script)

@pytest.mark.version('>=4.0')
def test_1(act: Action):

    expected_stdout_5x = """
        IDX_ID                          1
        POS                             0
        KEY                             RDB$DEPENDENT_NAME
        IDX_ID                          1
        POS                             1
        KEY                             RDB$DEPENDENT_TYPE
        IDX_ID                          2
        POS                             0
        KEY                             RDB$DEPENDED_ON_NAME

        IDX_ID                          2
        POS                             1
        KEY                             RDB$DEPENDED_ON_TYPE
        IDX_ID                          2
        POS                             2
        KEY                             RDB$FIELD_NAME

        Records affected: 5
    """

    expected_stdout_6x = """
        IDX_ID                          1
        POS                             0
        KEY                             RDB$DEPENDENT_SCHEMA_NAME
        IDX_ID                          1
        POS                             1
        KEY                             RDB$DEPENDENT_NAME
        IDX_ID                          1
        POS                             2
        KEY                             RDB$DEPENDENT_TYPE
        IDX_ID                          2
        POS                             0
        KEY                             RDB$DEPENDED_ON_SCHEMA_NAME
        IDX_ID                          2
        POS                             1
        KEY                             RDB$DEPENDED_ON_NAME
        IDX_ID                          2
        POS                             2
        KEY                             RDB$DEPENDED_ON_TYPE
        IDX_ID                          2
        POS                             3
        KEY                             RDB$FIELD_NAME

        Records affected: 7
    """

    act.expected_stdout = expected_stdout_5x if act.is_version('<6') else expected_stdout_6x
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
