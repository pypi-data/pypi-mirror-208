BEGIN

CREATE OR REPLACE PROCEDURE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.SETUP_CLEANROOM_COMMON(HABU_ACCOUNT VARCHAR, CUSTOMER_ACCOUNT_ID VARCHAR, SHARE_RESTRICTIONS VARCHAR)
	returns string
	language javascript
	execute as owner as
	$$

        sqlcmd = "CREATE DATABASE IF NOT EXISTS HABU_CLEAN_ROOM_COMMON COMMENT = 'HABU_" + CUSTOMER_ACCOUNT_ID + "'";
        snowflake.execute({ sqlText: sqlcmd });
        sqlcmd = "CREATE SCHEMA IF NOT EXISTS HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM COMMENT = 'HABU_" + CUSTOMER_ACCOUNT_ID + "'";
        snowflake.execute({ sqlText: sqlcmd });
        sqlcmd = "CREATE TABLE IF NOT EXISTS HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.ALLOWED_STATEMENTS " +
            "(ACCOUNT_ID VARCHAR(100), CLEAN_ROOM_ID VARCHAR(100), STATEMENT_HASH VARCHAR(100))";
        snowflake.execute({ sqlText: sqlcmd });
        sqlcmd = "CREATE TABLE IF NOT EXISTS HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CLEAN_ROOM_REQUESTS (" +
            "ID VARCHAR(40) NOT NULL," +
            "REQUEST_TYPE VARCHAR(50) NOT NULL," +
            "REQUEST_DATA VARIANT," +
            "CREATED_AT TIMESTAMP," +
            "UPDATED_AT TIMESTAMP," +
            "REQUEST_STATUS VARCHAR(50))";
        snowflake.execute({ sqlText: sqlcmd });
        sqlcmd = "ALTER TABLE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CLEAN_ROOM_REQUESTS SET CHANGE_TRACKING = TRUE;"
        snowflake.execute({ sqlText: sqlcmd });
        sqlcmd = "CREATE TABLE IF NOT EXISTS HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CLEAN_ROOM_ERRORS (" +
            "CODE NUMBER," +
            "STATE STRING," +
            "MESSAGE STRING," +
            "STACK_TRACE STRING," +
            "CREATED_AT TIMESTAMP," +
            "REQUEST_ID VARCHAR," +
            "PROC_NAME VARCHAR)";
        snowflake.execute({ sqlText: sqlcmd });
        sqlcmd = "CREATE TABLE IF NOT EXISTS HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CLEAN_ROOM_LOGS (" +
            "LOG_MESSAGE STRING," +
            "REQUEST_ID STRING," +
            "PROC_NAME STRING," +
            "CREATED_AT TIMESTAMP)";
        snowflake.execute({ sqlText: sqlcmd });
        sqlcmd = "CREATE TABLE IF NOT EXISTS HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.APP_METADATA (" +
            "ID STRING," +
            "METADATA_NAME STRING," +
            "METADATA_VALUE STRING," +
            "CREATED_AT TIMESTAMP," +
            "UPDATED_AT TIMESTAMP)";
        snowflake.execute({ sqlText: sqlcmd });
        sqlcmd = "CREATE SHARE IF NOT EXISTS HABU_CLEAN_ROOM_COMMON_SHARE";
        snowflake.execute({ sqlText: sqlcmd });
        sqlcmd = "GRANT USAGE ON DATABASE HABU_CLEAN_ROOM_COMMON TO SHARE HABU_CLEAN_ROOM_COMMON_SHARE";
        snowflake.execute({ sqlText: sqlcmd });
        sqlcmd = "GRANT USAGE ON SCHEMA HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM TO SHARE HABU_CLEAN_ROOM_COMMON_SHARE";
        snowflake.execute({ sqlText: sqlcmd });
        sqlcmd = "GRANT SELECT ON TABLE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CLEAN_ROOM_REQUESTS TO SHARE HABU_CLEAN_ROOM_COMMON_SHARE";
        snowflake.execute({ sqlText: sqlcmd });
        sqlcmd = "GRANT SELECT ON TABLE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CLEAN_ROOM_ERRORS TO SHARE HABU_CLEAN_ROOM_COMMON_SHARE";
        snowflake.execute({ sqlText: sqlcmd });
        sqlcmd = "GRANT SELECT ON TABLE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CLEAN_ROOM_LOGS TO SHARE HABU_CLEAN_ROOM_COMMON_SHARE";
        snowflake.execute({ sqlText: sqlcmd });
        sqlcmd = "GRANT SELECT ON TABLE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.APP_METADATA TO SHARE HABU_CLEAN_ROOM_COMMON_SHARE";
        snowflake.execute({ sqlText: sqlcmd });
        snowflake.execute({
            sqlText: "ALTER SHARE HABU_CLEAN_ROOM_COMMON_SHARE ADD ACCOUNTS = :1 SHARE_RESTRICTIONS = " + SHARE_RESTRICTIONS,
            binds: [HABU_ACCOUNT]
        });
        sqlcmd = "CREATE WAREHOUSE IF NOT EXISTS HABU_CLEAN_ROOM_COMMON_XLARGE_WH WAREHOUSE_SIZE = XLARGE INITIALLY_SUSPENDED = TRUE AUTO_SUSPEND = 30 COMMENT = 'HABU_" + CUSTOMER_ACCOUNT_ID + "'";
        snowflake.execute({ sqlText: sqlcmd });
        return "Setup of cleanroom common objects successful";
    $$;


end;

