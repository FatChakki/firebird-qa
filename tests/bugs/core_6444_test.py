#coding:utf-8

"""
ID:          issue-6677
ISSUE:       6677
TITLE:       Ability to query Firebird configuration using SQL
DESCRIPTION:
JIRA:        CORE-6444
FBTEST:      bugs.core_6444
NOTES:
    [20.02.2023] pzotov
    Currently test only checks ability to query virtual table RDB$CONFIG and obtain ID, NAME and DEFAULT columns from it.
    We have to use substitusions because default value for security database is returned as full pathj + filename, thus
    its [disk+] path must be ignored.

    Checked on 4.0.3.2903, 5.0.0.957 (both SS and CS).
"""
import os
import pytest
from firebird.qa import *

substitutions = [ ('[ \t]+', ' '), ('RDB\\$CONFIG_DEFAULT .*security\\d+.fdb', 'RDB$CONFIG_DEFAULT security.fdb') ]

db = db_factory()

test_script = """
    set list on;
    set count on;
    select rdb$config_id,rdb$config_name,rdb$config_default
    from rdb$config
    order by 1;
"""
act = isql_act('db', test_script, substitutions = substitutions)

if os.name == 'nt':
    AuthClient_DEFAULT = 'Srp256, Srp, Win_Sspi, Legacy_Auth'
    IpcName_DEFAULT = 'FIREBIRD'
    MaxUnflushedWrites_DEFAULT = 100
    MaxUnflushedWriteTime_DEFAULT = 5
    OutputRedirectionFile_DEFAULT = 'nul'
else:
    AuthClient_DEFAULT = 'Srp256, Srp, Legacy_Auth'
    IpcName_DEFAULT = 'FirebirdIPI'
    MaxUnflushedWrites_DEFAULT = -1
    MaxUnflushedWriteTime_DEFAULT = -1
    OutputRedirectionFile_DEFAULT = '/dev/null'


fb4x_expected_out = r"""
    RDB$CONFIG_ID 0
    RDB$CONFIG_NAME TempBlockSize
    RDB$CONFIG_DEFAULT 1048576
    RDB$CONFIG_ID 1
    RDB$CONFIG_NAME TempCacheLimit
    RDB$CONFIG_DEFAULT 67108864
    RDB$CONFIG_ID 2
    RDB$CONFIG_NAME RemoteFileOpenAbility
    RDB$CONFIG_DEFAULT false
    RDB$CONFIG_ID 3
    RDB$CONFIG_NAME GuardianOption
    RDB$CONFIG_DEFAULT 1
    RDB$CONFIG_ID 4
    RDB$CONFIG_NAME CpuAffinityMask
    RDB$CONFIG_DEFAULT 0
    RDB$CONFIG_ID 5
    RDB$CONFIG_NAME TcpRemoteBufferSize
    RDB$CONFIG_DEFAULT 8192
    RDB$CONFIG_ID 6
    RDB$CONFIG_NAME TcpNoNagle
    RDB$CONFIG_DEFAULT true
    RDB$CONFIG_ID 7
    RDB$CONFIG_NAME TcpLoopbackFastPath
    RDB$CONFIG_DEFAULT false
    RDB$CONFIG_ID 8
    RDB$CONFIG_NAME DefaultDbCachePages
    RDB$CONFIG_DEFAULT 2048
    RDB$CONFIG_ID 9
    RDB$CONFIG_NAME ConnectionTimeout
    RDB$CONFIG_DEFAULT 180
    RDB$CONFIG_ID 10
    RDB$CONFIG_NAME DummyPacketInterval
    RDB$CONFIG_DEFAULT 0
    RDB$CONFIG_ID 11
    RDB$CONFIG_NAME DefaultTimeZone
    RDB$CONFIG_DEFAULT <null>
    RDB$CONFIG_ID 12
    RDB$CONFIG_NAME LockMemSize
    RDB$CONFIG_DEFAULT 1048576
    RDB$CONFIG_ID 13
    RDB$CONFIG_NAME LockHashSlots
    RDB$CONFIG_DEFAULT 8191
    RDB$CONFIG_ID 14
    RDB$CONFIG_NAME LockAcquireSpins
    RDB$CONFIG_DEFAULT 0
    RDB$CONFIG_ID 15
    RDB$CONFIG_NAME EventMemSize
    RDB$CONFIG_DEFAULT 65536
    RDB$CONFIG_ID 16
    RDB$CONFIG_NAME DeadlockTimeout
    RDB$CONFIG_DEFAULT 10
    RDB$CONFIG_ID 17
    RDB$CONFIG_NAME RemoteServiceName
    RDB$CONFIG_DEFAULT gds_db
    RDB$CONFIG_ID 18
    RDB$CONFIG_NAME RemoteServicePort
    RDB$CONFIG_DEFAULT 0
    RDB$CONFIG_ID 19
    RDB$CONFIG_NAME RemotePipeName
    RDB$CONFIG_DEFAULT interbas
    RDB$CONFIG_ID 20
    RDB$CONFIG_NAME IpcName
    RDB$CONFIG_DEFAULT %(IpcName_DEFAULT)s
    RDB$CONFIG_ID 21
    RDB$CONFIG_NAME MaxUnflushedWrites
    RDB$CONFIG_DEFAULT %(MaxUnflushedWrites_DEFAULT)s
    RDB$CONFIG_ID 22
    RDB$CONFIG_NAME MaxUnflushedWriteTime
    RDB$CONFIG_DEFAULT %(MaxUnflushedWriteTime_DEFAULT)s
    RDB$CONFIG_ID 23
    RDB$CONFIG_NAME ProcessPriorityLevel
    RDB$CONFIG_DEFAULT 0
    RDB$CONFIG_ID 24
    RDB$CONFIG_NAME RemoteAuxPort
    RDB$CONFIG_DEFAULT 0
    RDB$CONFIG_ID 25
    RDB$CONFIG_NAME RemoteBindAddress
    RDB$CONFIG_DEFAULT <null>
    RDB$CONFIG_ID 26
    RDB$CONFIG_NAME ExternalFileAccess
    RDB$CONFIG_DEFAULT None
    RDB$CONFIG_ID 27
    RDB$CONFIG_NAME DatabaseAccess
    RDB$CONFIG_DEFAULT Full
    RDB$CONFIG_ID 28
    RDB$CONFIG_NAME UdfAccess
    RDB$CONFIG_DEFAULT None
    RDB$CONFIG_ID 29
    RDB$CONFIG_NAME TempDirectories
    RDB$CONFIG_DEFAULT <null>
    RDB$CONFIG_ID 30
    RDB$CONFIG_NAME BugcheckAbort
    RDB$CONFIG_DEFAULT false
    RDB$CONFIG_ID 31
    RDB$CONFIG_NAME TraceDSQL
    RDB$CONFIG_DEFAULT 0
    RDB$CONFIG_ID 32
    RDB$CONFIG_NAME LegacyHash
    RDB$CONFIG_DEFAULT true
    RDB$CONFIG_ID 33
    RDB$CONFIG_NAME GCPolicy
    RDB$CONFIG_DEFAULT combined
    RDB$CONFIG_ID 34
    RDB$CONFIG_NAME Redirection
    RDB$CONFIG_DEFAULT false
    RDB$CONFIG_ID 35
    RDB$CONFIG_NAME DatabaseGrowthIncrement
    RDB$CONFIG_DEFAULT 134217728
    RDB$CONFIG_ID 36
    RDB$CONFIG_NAME FileSystemCacheThreshold
    RDB$CONFIG_DEFAULT 65536
    RDB$CONFIG_ID 37
    RDB$CONFIG_NAME RelaxedAliasChecking
    RDB$CONFIG_DEFAULT false
    RDB$CONFIG_ID 38
    RDB$CONFIG_NAME AuditTraceConfigFile
    RDB$CONFIG_DEFAULT
    RDB$CONFIG_ID 39
    RDB$CONFIG_NAME MaxUserTraceLogSize
    RDB$CONFIG_DEFAULT 10
    RDB$CONFIG_ID 40
    RDB$CONFIG_NAME FileSystemCacheSize
    RDB$CONFIG_DEFAULT 0
    RDB$CONFIG_ID 41
    RDB$CONFIG_NAME Providers
    RDB$CONFIG_DEFAULT Remote, Engine13, Loopback
    RDB$CONFIG_ID 42
    RDB$CONFIG_NAME AuthServer
    RDB$CONFIG_DEFAULT Srp256
    RDB$CONFIG_ID 43
    RDB$CONFIG_NAME AuthClient
    RDB$CONFIG_DEFAULT %(AuthClient_DEFAULT)s
    RDB$CONFIG_ID 44
    RDB$CONFIG_NAME UserManager
    RDB$CONFIG_DEFAULT Srp
    RDB$CONFIG_ID 45
    RDB$CONFIG_NAME TracePlugin
    RDB$CONFIG_DEFAULT fbtrace
    RDB$CONFIG_ID 46
    RDB$CONFIG_NAME SecurityDatabase
    RDB$CONFIG_DEFAULT C:\FB\40SS\security4.fdb
    RDB$CONFIG_ID 47
    RDB$CONFIG_NAME ServerMode
    RDB$CONFIG_DEFAULT Super
    RDB$CONFIG_ID 48
    RDB$CONFIG_NAME WireCrypt
    RDB$CONFIG_DEFAULT Required
    RDB$CONFIG_ID 49
    RDB$CONFIG_NAME WireCryptPlugin
    RDB$CONFIG_DEFAULT ChaCha64, ChaCha, Arc4
    RDB$CONFIG_ID 50
    RDB$CONFIG_NAME KeyHolderPlugin
    RDB$CONFIG_DEFAULT
    RDB$CONFIG_ID 51
    RDB$CONFIG_NAME RemoteAccess
    RDB$CONFIG_DEFAULT true
    RDB$CONFIG_ID 52
    RDB$CONFIG_NAME IPv6V6Only
    RDB$CONFIG_DEFAULT false
    RDB$CONFIG_ID 53
    RDB$CONFIG_NAME WireCompression
    RDB$CONFIG_DEFAULT false
    RDB$CONFIG_ID 54
    RDB$CONFIG_NAME MaxIdentifierByteLength
    RDB$CONFIG_DEFAULT 252
    RDB$CONFIG_ID 55
    RDB$CONFIG_NAME MaxIdentifierCharLength
    RDB$CONFIG_DEFAULT 63
    RDB$CONFIG_ID 56
    RDB$CONFIG_NAME AllowEncryptedSecurityDatabase
    RDB$CONFIG_DEFAULT false
    RDB$CONFIG_ID 57
    RDB$CONFIG_NAME StatementTimeout
    RDB$CONFIG_DEFAULT 0
    RDB$CONFIG_ID 58
    RDB$CONFIG_NAME ConnectionIdleTimeout
    RDB$CONFIG_DEFAULT 0
    RDB$CONFIG_ID 59
    RDB$CONFIG_NAME OnDisconnectTriggerTimeout
    RDB$CONFIG_DEFAULT 180
    RDB$CONFIG_ID 60
    RDB$CONFIG_NAME ClientBatchBuffer
    RDB$CONFIG_DEFAULT 131072
    RDB$CONFIG_ID 61
    RDB$CONFIG_NAME OutputRedirectionFile
    RDB$CONFIG_DEFAULT %(OutputRedirectionFile_DEFAULT)s
    RDB$CONFIG_ID 62
    RDB$CONFIG_NAME ExtConnPoolSize
    RDB$CONFIG_DEFAULT 0
    RDB$CONFIG_ID 63
    RDB$CONFIG_NAME ExtConnPoolLifeTime
    RDB$CONFIG_DEFAULT 7200
    RDB$CONFIG_ID 64
    RDB$CONFIG_NAME SnapshotsMemSize
    RDB$CONFIG_DEFAULT 65536
    RDB$CONFIG_ID 65
    RDB$CONFIG_NAME TipCacheBlockSize
    RDB$CONFIG_DEFAULT 4194304
    RDB$CONFIG_ID 66
    RDB$CONFIG_NAME ReadConsistency
    RDB$CONFIG_DEFAULT true
    RDB$CONFIG_ID 67
    RDB$CONFIG_NAME ClearGTTAtRetaining
    RDB$CONFIG_DEFAULT false
    RDB$CONFIG_ID 68
    RDB$CONFIG_NAME DataTypeCompatibility
    RDB$CONFIG_DEFAULT <null>
    RDB$CONFIG_ID 69
    RDB$CONFIG_NAME UseFileSystemCache
    RDB$CONFIG_DEFAULT true
    RDB$CONFIG_ID 70
    RDB$CONFIG_NAME InlineSortThreshold
    RDB$CONFIG_DEFAULT 1000
    RDB$CONFIG_ID 71
    RDB$CONFIG_NAME TempTableDirectory
    RDB$CONFIG_DEFAULT
    RDB$CONFIG_ID 72
    RDB$CONFIG_NAME UseLegacyKernelObjectsNames
    RDB$CONFIG_DEFAULT false
    Records affected: 73
""" % locals()

fb5x_expected_out = r"""
    RDB$CONFIG_ID 0
    RDB$CONFIG_NAME TempBlockSize
    RDB$CONFIG_DEFAULT 1048576
    RDB$CONFIG_ID 1
    RDB$CONFIG_NAME TempCacheLimit
    RDB$CONFIG_DEFAULT 67108864
    RDB$CONFIG_ID 2
    RDB$CONFIG_NAME RemoteFileOpenAbility
    RDB$CONFIG_DEFAULT false
    RDB$CONFIG_ID 3
    RDB$CONFIG_NAME GuardianOption
    RDB$CONFIG_DEFAULT 1
    RDB$CONFIG_ID 4
    RDB$CONFIG_NAME CpuAffinityMask
    RDB$CONFIG_DEFAULT 0
    RDB$CONFIG_ID 5
    RDB$CONFIG_NAME TcpRemoteBufferSize
    RDB$CONFIG_DEFAULT 8192
    RDB$CONFIG_ID 6
    RDB$CONFIG_NAME TcpNoNagle
    RDB$CONFIG_DEFAULT true
    RDB$CONFIG_ID 7
    RDB$CONFIG_NAME DefaultDbCachePages
    RDB$CONFIG_DEFAULT 2048
    RDB$CONFIG_ID 8
    RDB$CONFIG_NAME ConnectionTimeout
    RDB$CONFIG_DEFAULT 180
    RDB$CONFIG_ID 9
    RDB$CONFIG_NAME DummyPacketInterval
    RDB$CONFIG_DEFAULT 0
    RDB$CONFIG_ID 10
    RDB$CONFIG_NAME DefaultTimeZone
    RDB$CONFIG_DEFAULT <null>
    RDB$CONFIG_ID 11
    RDB$CONFIG_NAME LockMemSize
    RDB$CONFIG_DEFAULT 1048576
    RDB$CONFIG_ID 12
    RDB$CONFIG_NAME LockHashSlots
    RDB$CONFIG_DEFAULT 8191
    RDB$CONFIG_ID 13
    RDB$CONFIG_NAME LockAcquireSpins
    RDB$CONFIG_DEFAULT 0
    RDB$CONFIG_ID 14
    RDB$CONFIG_NAME EventMemSize
    RDB$CONFIG_DEFAULT 65536
    RDB$CONFIG_ID 15
    RDB$CONFIG_NAME DeadlockTimeout
    RDB$CONFIG_DEFAULT 10
    RDB$CONFIG_ID 16
    RDB$CONFIG_NAME RemoteServiceName
    RDB$CONFIG_DEFAULT gds_db
    RDB$CONFIG_ID 17
    RDB$CONFIG_NAME RemoteServicePort
    RDB$CONFIG_DEFAULT 0
    RDB$CONFIG_ID 18
    RDB$CONFIG_NAME IpcName
    RDB$CONFIG_DEFAULT %(IpcName_DEFAULT)s
    RDB$CONFIG_ID 19
    RDB$CONFIG_NAME MaxUnflushedWrites
    RDB$CONFIG_DEFAULT %(MaxUnflushedWrites_DEFAULT)s
    RDB$CONFIG_ID 20
    RDB$CONFIG_NAME MaxUnflushedWriteTime
    RDB$CONFIG_DEFAULT %(MaxUnflushedWriteTime_DEFAULT)s
    RDB$CONFIG_ID 21
    RDB$CONFIG_NAME ProcessPriorityLevel
    RDB$CONFIG_DEFAULT 0
    RDB$CONFIG_ID 22
    RDB$CONFIG_NAME RemoteAuxPort
    RDB$CONFIG_DEFAULT 0
    RDB$CONFIG_ID 23
    RDB$CONFIG_NAME RemoteBindAddress
    RDB$CONFIG_DEFAULT <null>
    RDB$CONFIG_ID 24
    RDB$CONFIG_NAME ExternalFileAccess
    RDB$CONFIG_DEFAULT None
    RDB$CONFIG_ID 25
    RDB$CONFIG_NAME DatabaseAccess
    RDB$CONFIG_DEFAULT Full
    RDB$CONFIG_ID 26
    RDB$CONFIG_NAME UdfAccess
    RDB$CONFIG_DEFAULT None
    RDB$CONFIG_ID 27
    RDB$CONFIG_NAME TempDirectories
    RDB$CONFIG_DEFAULT <null>
    RDB$CONFIG_ID 28
    RDB$CONFIG_NAME BugcheckAbort
    RDB$CONFIG_DEFAULT false
    RDB$CONFIG_ID 29
    RDB$CONFIG_NAME TraceDSQL
    RDB$CONFIG_DEFAULT 0
    RDB$CONFIG_ID 30
    RDB$CONFIG_NAME LegacyHash
    RDB$CONFIG_DEFAULT true
    RDB$CONFIG_ID 31
    RDB$CONFIG_NAME GCPolicy
    RDB$CONFIG_DEFAULT combined
    RDB$CONFIG_ID 32
    RDB$CONFIG_NAME Redirection
    RDB$CONFIG_DEFAULT false
    RDB$CONFIG_ID 33
    RDB$CONFIG_NAME DatabaseGrowthIncrement
    RDB$CONFIG_DEFAULT 134217728
    RDB$CONFIG_ID 34
    RDB$CONFIG_NAME FileSystemCacheThreshold
    RDB$CONFIG_DEFAULT 65536
    RDB$CONFIG_ID 35
    RDB$CONFIG_NAME RelaxedAliasChecking
    RDB$CONFIG_DEFAULT false
    RDB$CONFIG_ID 36
    RDB$CONFIG_NAME AuditTraceConfigFile
    RDB$CONFIG_DEFAULT
    RDB$CONFIG_ID 37
    RDB$CONFIG_NAME MaxUserTraceLogSize
    RDB$CONFIG_DEFAULT 10
    RDB$CONFIG_ID 38
    RDB$CONFIG_NAME FileSystemCacheSize
    RDB$CONFIG_DEFAULT 0
    RDB$CONFIG_ID 39
    RDB$CONFIG_NAME Providers
    RDB$CONFIG_DEFAULT Remote, Engine13, Loopback
    RDB$CONFIG_ID 40
    RDB$CONFIG_NAME AuthServer
    RDB$CONFIG_DEFAULT Srp256
    RDB$CONFIG_ID 41
    RDB$CONFIG_NAME AuthClient
    RDB$CONFIG_DEFAULT %(AuthClient_DEFAULT)s
    RDB$CONFIG_ID 42
    RDB$CONFIG_NAME UserManager
    RDB$CONFIG_DEFAULT Srp
    RDB$CONFIG_ID 43
    RDB$CONFIG_NAME DefaultProfilerPlugin
    RDB$CONFIG_DEFAULT Default_Profiler
    RDB$CONFIG_ID 44
    RDB$CONFIG_NAME TracePlugin
    RDB$CONFIG_DEFAULT fbtrace
    RDB$CONFIG_ID 45
    RDB$CONFIG_NAME SecurityDatabase
    RDB$CONFIG_DEFAULT C:\FB\50SS\security5.fdb
    RDB$CONFIG_ID 46
    RDB$CONFIG_NAME ServerMode
    RDB$CONFIG_DEFAULT Super
    RDB$CONFIG_ID 47
    RDB$CONFIG_NAME WireCrypt
    RDB$CONFIG_DEFAULT Required
    RDB$CONFIG_ID 48
    RDB$CONFIG_NAME WireCryptPlugin
    RDB$CONFIG_DEFAULT ChaCha64, ChaCha, Arc4
    RDB$CONFIG_ID 49
    RDB$CONFIG_NAME KeyHolderPlugin
    RDB$CONFIG_DEFAULT
    RDB$CONFIG_ID 50
    RDB$CONFIG_NAME RemoteAccess
    RDB$CONFIG_DEFAULT true
    RDB$CONFIG_ID 51
    RDB$CONFIG_NAME IPv6V6Only
    RDB$CONFIG_DEFAULT false
    RDB$CONFIG_ID 52
    RDB$CONFIG_NAME WireCompression
    RDB$CONFIG_DEFAULT false
    RDB$CONFIG_ID 53
    RDB$CONFIG_NAME MaxIdentifierByteLength
    RDB$CONFIG_DEFAULT 252
    RDB$CONFIG_ID 54
    RDB$CONFIG_NAME MaxIdentifierCharLength
    RDB$CONFIG_DEFAULT 63
    RDB$CONFIG_ID 55
    RDB$CONFIG_NAME AllowEncryptedSecurityDatabase
    RDB$CONFIG_DEFAULT false
    RDB$CONFIG_ID 56
    RDB$CONFIG_NAME StatementTimeout
    RDB$CONFIG_DEFAULT 0
    RDB$CONFIG_ID 57
    RDB$CONFIG_NAME ConnectionIdleTimeout
    RDB$CONFIG_DEFAULT 0
    RDB$CONFIG_ID 58
    RDB$CONFIG_NAME OnDisconnectTriggerTimeout
    RDB$CONFIG_DEFAULT 180
    RDB$CONFIG_ID 59
    RDB$CONFIG_NAME ClientBatchBuffer
    RDB$CONFIG_DEFAULT 131072
    RDB$CONFIG_ID 60
    RDB$CONFIG_NAME OutputRedirectionFile
    RDB$CONFIG_DEFAULT %(OutputRedirectionFile_DEFAULT)s
    RDB$CONFIG_ID 61
    RDB$CONFIG_NAME ExtConnPoolSize
    RDB$CONFIG_DEFAULT 0
    RDB$CONFIG_ID 62
    RDB$CONFIG_NAME ExtConnPoolLifeTime
    RDB$CONFIG_DEFAULT 7200
    RDB$CONFIG_ID 63
    RDB$CONFIG_NAME SnapshotsMemSize
    RDB$CONFIG_DEFAULT 65536
    RDB$CONFIG_ID 64
    RDB$CONFIG_NAME TipCacheBlockSize
    RDB$CONFIG_DEFAULT 4194304
    RDB$CONFIG_ID 65
    RDB$CONFIG_NAME ReadConsistency
    RDB$CONFIG_DEFAULT true
    RDB$CONFIG_ID 66
    RDB$CONFIG_NAME ClearGTTAtRetaining
    RDB$CONFIG_DEFAULT false
    RDB$CONFIG_ID 67
    RDB$CONFIG_NAME DataTypeCompatibility
    RDB$CONFIG_DEFAULT <null>
    RDB$CONFIG_ID 68
    RDB$CONFIG_NAME UseFileSystemCache
    RDB$CONFIG_DEFAULT true
    RDB$CONFIG_ID 69
    RDB$CONFIG_NAME InlineSortThreshold
    RDB$CONFIG_DEFAULT 1000
    RDB$CONFIG_ID 70
    RDB$CONFIG_NAME TempTableDirectory
    RDB$CONFIG_DEFAULT
    RDB$CONFIG_ID 71
    RDB$CONFIG_NAME MaxStatementCacheSize
    RDB$CONFIG_DEFAULT 2097152
    RDB$CONFIG_ID 72
    RDB$CONFIG_NAME ParallelWorkers
    RDB$CONFIG_DEFAULT 1
    RDB$CONFIG_ID 73
    RDB$CONFIG_NAME MaxParallelWorkers
    RDB$CONFIG_DEFAULT 1
    RDB$CONFIG_ID 74
    RDB$CONFIG_NAME OptimizeForFirstRows
    RDB$CONFIG_DEFAULT false
    Records affected: 75
""" % locals()

@pytest.mark.version('>=4.0')
def test_1(act: Action):
    act.expected_stdout = fb4x_expected_out if act.is_version('<5') else fb5x_expected_out
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
