#!/usr/bin/env python
# coding=utf-8


class Flags(object):
    # Connection opened
    MODE_INIT                           = 0
    # Read the handshake from the server and process it
    MODE_READ_HANDSHAKE                 = 1
    # Forward the handshake from the server
    MODE_SEND_HANDSHAKE                 = 2
    # Read the reply from the client and process it
    MODE_READ_AUTH                      = 3
    # Forward the reply from the client
    MODE_SEND_AUTH                      = 4
    # Read the reply from the server and process it
    MODE_READ_AUTH_RESULT               = 5
    # Forward the reply from the server
    MODE_SEND_AUTH_RESULT               = 6
    # Read the query from the client and process it
    MODE_READ_QUERY                     = 7
    # Send the query to the server
    MODE_SEND_QUERY                     = 8
    # Read the result set from the server and and process it
    MODE_READ_QUERY_RESULT              = 9
    # Send a result set to the client
    MODE_SEND_QUERY_RESULT              = 10
    # Connection closed
    MODE_CLEANUP                        = 11

    # Packet types
    COM_SLEEP                           = 0x00  # deprecated
    COM_QUIT                            = 0x01
    COM_INIT_DB                         = 0x02
    COM_QUERY                           = 0x03
    COM_FIELD_LIST                      = 0x04
    COM_CREATE_DB                       = 0x05
    COM_DROP_DB                         = 0x06
    COM_REFRESH                         = 0x07
    COM_SHUTDOWN                        = 0x08
    COM_STATISTICS                      = 0x09
    COM_PROCESS_INFO                    = 0x0a  # deprecated
    COM_CONNECT                         = 0x0b  # deprecated
    COM_PROCESS_KILL                    = 0x0c
    COM_DEBUG                           = 0x0d
    COM_PING                            = 0x0e
    COM_TIME                            = 0x0f  # deprecated
    COM_DELAYED_INSERT                  = 0x10  # deprecated
    COM_CHANGE_USER                     = 0x11
    COM_BINLOG_DUMP                     = 0x12
    COM_TABLE_DUMP                      = 0x13
    COM_CONNECT_OUT                     = 0x14
    COM_REGISTER_SLAVE                  = 0x15
    COM_STMT_PREPARE                    = 0x16
    COM_STMT_EXECUTE                    = 0x17
    COM_STMT_SEND_LONG_DATA             = 0x18
    COM_STMT_CLOSE                      = 0x19
    COM_STMT_RESET                      = 0x1a
    COM_SET_OPTION                      = 0x1b
    COM_STMT_FETCH                      = 0x1c
    COM_DAEMON                          = 0x1d  # deprecated
    COM_UNKNOWN                         = 0xff  # bad!

    OK                                  = 0x00
    ERR                                 = 0xff
    EOF                                 = 0xfe
    LOCAL_INFILE                        = 0xfb

    SERVER_STATUS_IN_TRANS              = 0x0001
    SERVER_STATUS_AUTOCOMMIT            = 0x0002
    SERVER_MORE_RESULTS_EXISTS          = 0x0008
    SERVER_STATUS_NO_GOOD_INDEX_USED    = 0x0010
    SERVER_STATUS_NO_INDEX_USED         = 0x0020
    SERVER_STATUS_CURSOR_EXISTS         = 0x0040
    SERVER_STATUS_LAST_ROW_SENT         = 0x0080
    SERVER_STATUS_DB_DROPPED            = 0x0100
    SERVER_STATUS_NO_BACKSLASH_ESCAPES  = 0x0200
    SERVER_STATUS_METADATA_CHANGED      = 0x0400
    SERVER_QUERY_WAS_SLOW               = 0x0800
    SERVER_PS_OUT_PARAMS                = 0x1000

    CLIENT_LONG_PASSWORD                = 0x0001
    CLIENT_FOUND_ROWS                   = 0x0002
    CLIENT_LONG_FLAG                    = 0x0004
    CLIENT_CONNECT_WITH_DB              = 0x0008
    CLIENT_NO_SCHEMA                    = 0x0010
    CLIENT_COMPRESS                     = 0x0020
    CLIENT_ODBC                         = 0x0040
    CLIENT_LOCAL_FILES                  = 0x0080
    CLIENT_IGNORE_SPACE                 = 0x0100
    CLIENT_PROTOCOL_41                  = 0x0200
    CLIENT_INTERACTIVE                  = 0x0400
    CLIENT_SSL                          = 0x0800
    CLIENT_IGNORE_SIGPIPE               = 0x1000
    CLIENT_TRANSACTIONS                 = 0x2000
    CLIENT_RESERVED                     = 0x4000
    CLIENT_SECURE_CONNECTION            = 0x8000
    CLIENT_MULTI_STATEMENTS             = 0x00010000
    CLIENT_MULTI_RESULTS                = 0x00020000
    CLIENT_PS_MULTI_RESULTS             = 0x00040000
    CLIENT_PLUGIN_AUTH                  = 0x00080000
    CLIENT_SSL_VERIFY_SERVER_CERT       = 0x40000000
    CLIENT_REMEMBER_OPTIONS             = 0x80000000

    MYSQL_TYPE_DECIMAL                  = 0x00
    MYSQL_TYPE_TINY                     = 0x01
    MYSQL_TYPE_SHORT                    = 0x02
    MYSQL_TYPE_LONG                     = 0x03
    MYSQL_TYPE_FLOAT                    = 0x04
    MYSQL_TYPE_DOUBLE                   = 0x05
    MYSQL_TYPE_NULL                     = 0x06
    MYSQL_TYPE_TIMESTAMP                = 0x07
    MYSQL_TYPE_LONGLONG                 = 0x08
    MYSQL_TYPE_INT24                    = 0x09
    MYSQL_TYPE_DATE                     = 0x0a
    MYSQL_TYPE_TIME                     = 0x0b
    MYSQL_TYPE_DATETIME                 = 0x0c
    MYSQL_TYPE_YEAR                     = 0x0d
    MYSQL_TYPE_NEWDATE                  = 0x0e
    MYSQL_TYPE_VARCHAR                  = 0x0f
    MYSQL_TYPE_BIT                      = 0x10
    MYSQL_TYPE_NEWDECIMAL               = 0xf6
    MYSQL_TYPE_ENUM                     = 0xf7
    MYSQL_TYPE_SET                      = 0xf8
    MYSQL_TYPE_TINY_BLOB                = 0xf9
    MYSQL_TYPE_MEDIUM_BLOB              = 0xfa
    MYSQL_TYPE_LONG_BLOB                = 0xfb
    MYSQL_TYPE_BLOB                     = 0xfc
    MYSQL_TYPE_VAR_STRING               = 0xfd
    MYSQL_TYPE_STRING                   = 0xfe
    MYSQL_TYPE_GEOMETRY                 = 0xff

    REFRESH_GRANT                       = 0x01
    REFRESH_LOG                         = 0x02
    REFRESH_TABLES                      = 0x04
    REFRESH_HOSTS                       = 0x08
    REFRESH_STATUS                      = 0x10
    REFRESH_THREADS                     = 0x20
    REFRESH_SLAVE                       = 0x40
    REFRESH_MASTER                      = 0x80

    SHUTDOWN_DEFAULT                    = 0x00
    SHUTDOWN_WAIT_CONNECTIONS           = 0x01
    SHUTDOWN_WAIT_TRANSACTIONS          = 0x02
    SHUTDOWN_WAIT_UPDATES               = 0x08
    SHUTDOWN_WAIT_ALL_BUFFERS           = 0x10
    SHUTDOWN_WAIT_CRITICAL_BUFFERS      = 0x11
    KILL_QUERY                          = 0xfe
    KILL_CONNECTION                     = 0xff

    CURSOR_TYPE_NO_CURSOR               = 0x00
    CURSOR_TYPE_READ_ONLY               = 0x01
    CURSOR_TYPE_FOR_UPDATE              = 0x02
    CURSOR_TYPE_SCROLLABLE              = 0x04

    MYSQL_OPTION_MULTI_STATEMENTS_ON    = 0
    MYSQL_OPTION_MULTI_STATEMENTS_OFF   = 1

    ROW_TYPE_TEXT                       = 0
    ROW_TYPE_BINARY                     = 1

    RS_OK                               = 0
    RS_FULL                             = 1
    RS_HALF                             = 2
    RS_COL_DEF                          = 3
    RS_DATA_FILE                        = 4

    CS_latin1_swedish_ci                = 8
    CS_utf8_general_ci                  = 33
    CS_binary                           = 63


if __name__ == "__main__":
    import doctest
    doctest.testmod()
