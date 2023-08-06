

class SnowflakePull:

    import pandas

    def snowflake_pull(self, query: str | dict | None, un: str, wh: str, db: str, role: str, schema=None, table=None,
                       sample_table: bool = False, sample_val: bool = False, table_sample: dict = None,
                       dtypes_conv=None, separate_dataframes: bool = True, polars: bool = False): # -> pandas.DataFrame:

        """
        function: pulls snowflake data

        dependencies: [
            pandas,
            snowflake.connector,
            time,
            datetime.datetime
        ]

        :param polars:
        :param separate_dataframes:
        :param table:
        :param schema:
        :param query: str | dict
            SQL query to run on Snowflake
                    E.G. query = "SELECT * FROM  NGP_DA_PROD.POS.TO_DATE_AGG_CHANNEL_CY"
            Can also be multiple queries in the form of a dictionary
                    E.G. query = {"df1": "SELECT * FROM  NGP_DA_PROD.POS.TO_DATE_AGG_CHANNEL_CY", "df "SELECT TOP 2 * \
                    FROM  NGP_DA_PROD.POS.TO_DATE_AGG_CHANNEL_CY"}

        :param un: str
            Nike Snowflake Username
                "USERNAME"

        :param db: str, default 'NA'
            Name of the Database

        :param wh: str
            Name of the Wharehouse
            e.g. "DA_DSM_SCANALYTICS_REPORTING_PROD"

        :param role: str
            Name of the role under which you are running Snowflake
                "DF_######"

        :param sample_table: bool, default: False

        :param sample_val: bool, default: False

        :param table_sample: dict, default: None
            later
                if table_sample = None
                    table_sample = {'db': None, 'schema': None, 'table': None, 'col': None}

        :param dtypes_conv: default: None

        :return: pandas.DataFrame
        """

        # snowflake connection packages:
        import pandas as pd
        import polars as pl
        import snowflake.connector
        import time

        if table_sample is not None:
            table_sample = {'db': None, 'schema': None, 'table': None, 'col': None}

        # --> take a random sample from a table in snowflake
        query = f'''SELECT * FROM {table_sample['db']}.{table_sample['schema']}.{table_sample['table']} LIMIT 100''' \
            if sample_table else query

        # --> take a random sample of a column from a table in snowflake
        query = f'''SELECT DISTINCT 
                {table_sample['col']} 
            FROM 
                {table_sample['db']}.{table_sample['schema']}.{table_sample['table']} 
            ORDER BY 1 LIMIT 10''' \
            if sample_val else query

        recs = False

        df = pd.DataFrame()

        if type(query) == dict:

            df = pd.DataFrame([query]).T
            df_index = df.index
            print(df_index)

            df2 = pl.from_pandas(df)
            print(df2)

            df_return = pd.DataFrame(index=df.index)
            df_return['sfqid'] = ''

            queries = len(df)
            print('Pulling ' + str(queries) + ' queries')

            query_list = []
            db_list = []
            complete = []

            for item in range(queries):
                query_list.append(item)
                db_list.append(item)
                complete.append(0)

            print('opening snowflake connection...')

            try:
                cnn = snowflake.connector.connect(
                    user=un,
                    account='nike',
                    authenticator='externalbrowser',
                    role=role,
                    warehouse='POS_REPORT_PROD'
                )

                cs = cnn.cursor()
                process_complete = 0
                process_pass = 0
                counter = 0

                for k, v in df.iterrows():
                    sql = v[0]
                    cs.execute_async(sql)
                    query_list[counter] = cs.sfqid
                    df_return['sfqid'][k] = cs.sfqid
                    counter += 1
                dfs = {}
                while process_complete == 0:
                    item = -1
                    process_pass += 1
                    if sum(complete) == queries or process_pass == 10:
                        process_complete = 1
                    for result in query_list:
                        item += 1
                        if complete[item] == 0:
                            status = cnn.get_query_status_throw_if_error(result)
                            print('the status for ' + df_return[df_return['sfqid'] == result].index[0] + ' is ' +
                                  str(status))
                            if str(status) == 'QueryStatus.SUCCESS':
                                complete[item] = 1
                                cs.get_results_from_sfqid(result)
                                if separate_dataframes:

                                    recs = True
                                    dfs[df_return[df_return['sfqid'] == result].index[0]] = cs.fetch_pandas_all()

                                else:
                                    df = pd.concat([df, cs.fetch_pandas_all()])
                            else:
                                time.sleep(.25)
            except Exception as e:
                print(e)
            finally:
                cnn.close()
                print('process complete')
        else:
            # connection settings
            from snowflake.connector.converter_null import SnowflakeNoConverterToPython
            conn = snowflake.connector.connect(
                user=str(un),
                account='nike',

                # opens separate browser window to confirm authentication
                authenticator='externalbrowser',
                warehouse=str(wh),
                database=str(db),
                role=str(role),
                converter_class=SnowflakeNoConverterToPython
            )

            # connect to snowflake using conn variables
            cur = conn.cursor()

            try:
                cur.execute(query)  # execute sql, store into-->

            # final data pull --> allows datatype-memory optimization
                df = pl.DataFrame
                if polars:
                    df = cur.fetch_arrow_all()

                else:
                    df = cur.fetch_pandas_all()
                print(df)

            except snowflake.connector.errors.ProgrammingError:
                print(f'Could not retrieve:\n\t {query}')

            except TypeError:
                print(f"""Could not retrieve:\n\t{query}\n\nbecause TypeError: NoneType""")

            # --> allows metadata querying
            except Exception as e:
                print(e)
                temp_df = cur.fetchall()  # return data
                cols = [x.name for x in cur.description]  # get column names
                df = pd.DataFrame(temp_df, columns=cols)  # create dataset

            conn.close()
            cur.close()
        if recs:
            return [dfs[k] for k in df_index]

        return df


