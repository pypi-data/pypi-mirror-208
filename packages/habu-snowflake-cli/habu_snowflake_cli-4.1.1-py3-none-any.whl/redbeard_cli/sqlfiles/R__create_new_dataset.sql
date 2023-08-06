BEGIN

CREATE OR REPLACE PROCEDURE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.HANDLE_NEW_DATASETS()
	returns string
	language javascript
	execute as owner as
	$$
        // Installs handler for new_datasets

        try {
            var crRequestSql = "SELECT " +
                                    " id AS request_id, " +
                                    " request_data:clean_room_id AS clean_room_id, " +
                                    " request_data:source_db AS source_db, " +
                                    " request_data:view_name AS view_name, " +
                                    " request_data:view_sql AS view_sql, " +
                                    " request_data:available_values_sql AS available_values_sql, " +
                                    " request_data:source_table_name AS source_table_name, " +
                                    " request_data:source_schema_name AS source_schema_name, " +
                                    " request_data:clean_room_version AS clean_room_version " +
                                    " FROM HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CLEAN_ROOM_REQUESTS " +
                                    " WHERE request_type = :1 AND request_status = :2 ORDER BY CREATED_AT ASC";
            var stmt = snowflake.createStatement({
                sqlText: crRequestSql,
                binds: ['NEW_DATASET', 'PENDING']
            });

            var rs = stmt.execute();
            var newDatasetParams = [];
            while (rs.next()) {
                var requestID = rs.getColumnValue(1);
                var cleanRoomID = rs.getColumnValue(2);
                var sourceDB = rs.getColumnValue(3);
                var viewName = rs.getColumnValue(4);
                var viewSql = rs.getColumnValue(5);
                var availableValuesSql = rs.getColumnValue(6);
                var sourceViewOrTableName = rs.getColumnValue(7);
                var sourceSchemaName = rs.getColumnValue(8);
                var cleanRoomVersion = rs.getColumnValue(9);

                newDatasetParams.push({
                    'rID': requestID,
                    'crID': cleanRoomID,
                    'sourceDB': sourceDB,
                    'vn': viewName,
                    'vs': viewSql,
                    'avs': availableValuesSql,
                    'sourceTableName': sourceViewOrTableName,
                    'sourceSchemaName': sourceSchemaName,
                    'cleanRoomVersion': cleanRoomVersion,
                })
                snowflake.execute({
                        sqlText: "UPDATE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CLEAN_ROOM_REQUESTS SET REQUEST_STATUS = :1, UPDATED_AT = CURRENT_TIMESTAMP() WHERE ID = :2",
                        binds: ["IN_PROGRESS", requestID]
                });
            }

            for (var i = 0; i < newDatasetParams.length; i++) {
                var stmt = snowflake.createStatement({
                    sqlText: 'CALL CLEAN_ROOM.CREATE_NEW_DATASET(:1, :2, :3, :4, :5, :6, :7, :8, :9)',
                    binds: [
                        newDatasetParams[i]['rID'],
                        newDatasetParams[i]['crID'],
                        newDatasetParams[i]['sourceDB'],
                        newDatasetParams[i]['vn'],
                        newDatasetParams[i]['vs'],
                        newDatasetParams[i]['avs'],
                        newDatasetParams[i]['sourceTableName'],
                        newDatasetParams[i]['sourceSchemaName'],
                        newDatasetParams[i]['cleanRoomVersion']
                    ]
                });
                stmt.execute();
            }
            result = "SUCCESS";
        } catch (err) {
            result = "FAILED";
            var stmt = snowflake.createStatement({
                sqlText: 'CALL CLEAN_ROOM.HANDLE_ERROR(:1, :2, :3, :4, :5, :6)',
                binds: [
                    err.code, err.state, err.message, err.stackTraceTxt, "", Object.keys(this)[0]
                ]
            });
            var res = stmt.execute();
        }
        return result;
	$$;

CREATE OR REPLACE PROCEDURE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CREATE_NEW_DATASET(REQUEST_ID VARCHAR, CLEAN_ROOM_ID VARCHAR, SOURCE_DB VARCHAR, VIEW_NAME VARCHAR, VIEW_SQL VARCHAR, AVAILABLE_VALUES_SQL VARCHAR, SOURCE_TABLE_NAME VARCHAR, SOURCE_SCHEMA_NAME VARCHAR, CLEAN_ROOM_VERSION VARCHAR)
	returns string
	language javascript
	execute as owner as
	$$
        // Handles new data set command

        try {

            var sf_clean_room_id = CLEAN_ROOM_ID.replace(/-/g, '').toUpperCase();

            var habuShareDb = "HABU_CR_" + sf_clean_room_id + "_HABU_SHARE"
            var partnerShareDb = "HABU_CR_" + sf_clean_room_id + "_PARTNER_SHARE"

            snowflake.execute({
                sqlText: "GRANT REFERENCE_USAGE ON DATABASE " + SOURCE_DB + " TO SHARE " + habuShareDb
            })

            snowflake.execute({
                sqlText: "GRANT REFERENCE_USAGE ON DATABASE " + SOURCE_DB + " TO SHARE " + partnerShareDb
            })

            snowflake.execute({
                sqlText: "GRANT REFERENCE_USAGE ON DATABASE HABU_DATA_CONNECTIONS  TO SHARE " + habuShareDb
            })

            snowflake.execute({sqlText: VIEW_SQL});

            if (AVAILABLE_VALUES_SQL !== "NONE") {
                snowflake.execute({sqlText: AVAILABLE_VALUES_SQL});

                snowflake.execute({
                    sqlText: "GRANT SELECT ON VIEW HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM." + VIEW_NAME + "_AVAILABLE_VALUES TO SHARE " + habuShareDb
                });
            }

            var policySql = "CREATE OR REPLACE ROW ACCESS POLICY HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM." + VIEW_NAME + "_POLICY AS (query_clean_room_id VARCHAR) " +
            "RETURNS BOOLEAN -> " +
            "CASE " +
            " WHEN EXISTS (SELECT 1 FROM HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM.V_ALLOWED_STATEMENTS WHERE " +
            " account_id = CURRENT_ACCOUNT() AND statement_hash = SHA2(CURRENT_STATEMENT()) " +
            " AND clean_room_id = QUERY_CLEAN_ROOM_ID) " +
            " THEN TRUE END;";

            var policyStmt = snowflake.createStatement({sqlText: policySql});
            policyStmt.execute();

            snowflake.execute({
                sqlText: "ALTER VIEW HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM." + VIEW_NAME + " ADD ROW ACCESS POLICY HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM." + VIEW_NAME + "_POLICY ON (clean_room_id)"
            });

            var stmt = snowflake.createStatement({
                sqlText: "SELECT REFERENCED_DATABASE, REFERENCED_SCHEMA, REFERENCED_OBJECT_NAME FROM SNOWFLAKE.ACCOUNT_USAGE.OBJECT_DEPENDENCIES" +
                        " WHERE REFERENCING_DATABASE = :1  AND REFERENCING_SCHEMA = :2 AND REFERENCING_OBJECT_NAME = :3",
                binds: [SOURCE_DB, SOURCE_SCHEMA_NAME, SOURCE_TABLE_NAME]
            });
            var rs = stmt.execute();
            while (rs.next()) {
                var referencedDatabase = rs.getColumnValue(1);

                var msg = "Running grant reference_usage on " + referencedDatabase + " to " + partnerShareDb + " share";
                snowflake.createStatement({
                    sqlText: 'CALL CLEAN_ROOM.SP_LOGGER(:1, :2, :3)',
                    binds:[msg, REQUEST_ID, Object.keys(this)[0]]
                }).execute();

                snowflake.execute({
                    sqlText: "GRANT REFERENCE_USAGE ON DATABASE " + referencedDatabase + " TO SHARE " + partnerShareDb
                })
            }

            snowflake.execute({
                sqlText: "GRANT SELECT ON VIEW HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM." + VIEW_NAME + " TO SHARE " + partnerShareDb
            });

            /*
                    if cleanroom v2
                    2 main things to be achieve
                        1. add new view to shared_schema (partner logic)
                            allow access to shared_schema.view to app
                        2. allow access on the view to TO_APP_ROLE (owner logic)
             */
            if (CLEAN_ROOM_VERSION != null && CLEAN_ROOM_VERSION.trim().length != 0 && CLEAN_ROOM_VERSION === "2") {
                var sharedSchemaViewSql = VIEW_SQL.replace(".CLEAN_ROOM."+VIEW_NAME, ".SHARED_SCHEMA."+VIEW_NAME)
                snowflake.execute({sqlText: sharedSchemaViewSql});

                snowflake.execute({
                    sqlText: `GRANT SELECT ON VIEW HABU_CLEAN_ROOM_${sf_clean_room_id}.SHARED_SCHEMA.${VIEW_NAME} TO SHARE ${partnerShareDb}`
                });

                // grant view access to owner (partner logic)
                snowflake.execute({
                    sqlText: `grant select on view HABU_CLEAN_ROOM_${sf_clean_room_id}.CLEAN_ROOM.${VIEW_NAME} to DATABASE ROLE HABU_CLEAN_ROOM_${sf_clean_room_id}.habu_db_role_app_${sf_clean_room_id};`
                });

                // grant usage appRole (owner logic)
                var appRole = `HABU_CR_${sf_clean_room_id}_APP_ROLE`;

                snowflake.execute({
                    sqlText: `grant usage on database HABU_CLEAN_ROOM_${sf_clean_room_id} to role ${appRole}`
                });

                snowflake.execute({
                    sqlText: `grant usage on schema HABU_CLEAN_ROOM_${sf_clean_room_id}.SHARED_SCHEMA to role ${appRole}`
                });

                snowflake.execute({
                    sqlText: `grant select on view HABU_CLEAN_ROOM_${sf_clean_room_id}.SHARED_SCHEMA.${VIEW_NAME} to role ${appRole}`
                });

            }
            result = "COMPLETE";
            msg = "Dataset created successfully"
        } catch (err) {

            result = "FAILED";
            var stmt = snowflake.createStatement({
                sqlText: 'CALL CLEAN_ROOM.HANDLE_ERROR(:1, :2, :3, :4, :5, :6)',
                binds: [
                    err.code, err.state, err.message, err.stackTraceTxt, REQUEST_ID, Object.keys(this)[0]
                ]
            });
            msg = err.message
            var res = stmt.execute();
        } finally {
            snowflake.execute({
                sqlText: "UPDATE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CLEAN_ROOM_REQUESTS SET REQUEST_STATUS = :1, UPDATED_AT = CURRENT_TIMESTAMP() WHERE ID = :2",
                binds: [result, REQUEST_ID]
            });


            opMsg = Object.keys(this)[0] + " - OPERATION STATUS - " + result + " - Detail: " + msg
            snowflake.createStatement({
                sqlText: 'CALL CLEAN_ROOM.SP_LOGGER(:1, :2, :3)',
                binds:[opMsg, REQUEST_ID, Object.keys(this)[0]]
            }).execute();
        }
        return result;
	$$;


end;

