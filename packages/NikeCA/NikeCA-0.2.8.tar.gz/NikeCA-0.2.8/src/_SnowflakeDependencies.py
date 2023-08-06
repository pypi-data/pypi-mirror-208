class SnowflakeDependencies:

    def remove_schemas(self, d_dict: dict, schema_list: list):
        """"
        checks to see if the schema for the filename is in the schema list
        :param schema_list:
        :param d_dict:dict
        """
        import json

        final_result = {}

        for k, v in d_dict.items():
            final_result[k] = {}
            for x, y in v.items():
                if str(x).split('.')[1].upper() in schema_list:
                    print(f'passed table: {x}')
                else:
                    final_result[k][x] = y
                    print(f'added table: {x}')

        return final_result

    def dict_convert_into_dataframe(self, d_dict: dict, cols: list, schema_list: list):
        """"
        checks to see if the schema is within 10 characters before the tablename, which is the key in the get_ddl
        :param d_dict:
        :param cols: list
        :param schema_list:list
        """
        import json
        import pandas as pd

        df = pd.DataFrame(columns=cols)

        for k, v in d_dict.items():
            for i, y in v.items():
                for z, f in y.items():
                    for a, b in f.items():
                        print(k, i)
                        for x in schema_list:
                            index = str(b).index(f'{k}')
                            if x in str(b)[index - 10:index]:
                                print(str(b)[index - len(x) - 1: index + len(k)])

                                df.loc[len(df)] = ([str(b)[index - len(x) - 1: index + len(k)], i, str(f)])

        print(df)
        return df

    def snowflake_dependencies_loop(self,
                                    tables: str | list,
                                    username: str,
                                    warehouse: str,
                                    role: str,
                                    database: str | None = None,
                                    schema: str | list | None = None,
                                    save_path: str | None = None,
                                    ):

        """
        Searches the snowflake database and finds instances where the table is referenced and where the reference is not
            in the actual creation of the table itself

        :param save_path: (str | None) The path to save the output.
        :param tables: (str | list): The list of tables or views to fetch DDL for.
        :param username: username for Snowflake
        :param warehouse: warehouse for Snowflake
        :param role: role for Snowflake
        :param database: database to search in must provide
        :param schema: filling this in can really help to speed up the query
        :return: pandas Dataframe

        This function is used to fetch the DDL of tables and views from Snowflake.

        Parameters:
            tables (str | list): The list of tables or views to fetch DDL for.
            username (str): The username of the Snowflake user.
            warehouse (str): The warehouse to use for the connection.
            role (str): The role of the Snowflake user.
            database (str | None): The database to use for the connection.
            schema (str | list | None): The schema to use for the connection.
            save_path (str | None): The path to save the output.

        Returns:
            dict: A dictionary containing the DDL of the tables and views.
        """

        # snowflake connection packages:
        import pandas as pd
        import polars as pl
        import snowflake.connector
        import time
        import json
        import os

        if type(tables) == str:
            tables = [tables]

        print('opening snowflake connection...')

        cnn = snowflake.connector.connect(
            user=username,
            account='nike',
            authenticator='externalbrowser',
            role=role,
            warehouse=warehouse,
        )
        cs = cnn.cursor()
        process_complete = 0
        process_pass = 0
        counter = 0

        # fetch schema and table names
        query = 'SELECT * FROM ' + database + '.INFORMATION_SCHEMA.TABLES'
        if schema is not None:
            if isinstance(schema, str):
                query += f" WHERE TABLE_SCHEMA = '{schema}'"
            elif isinstance(schema, list):
                schema = "', '".join(schema)
                query += f" WHERE TABLE_SCHEMA IN ('{schema}')"
            else:
                raise TypeError('schema must be a list or string')

        cs.execute(query)
        df_tables = cs.fetch_pandas_all()

        query_ddl = {}

        for k, i in df_tables.iterrows():
            if i['TABLE_TYPE'] == 'VIEW':
                query_ddl[i['TABLE_CATALOG'] + '.' + i['TABLE_SCHEMA'] + '.' + i['TABLE_NAME']] = \
                    "SELECT GET_DDL('" + i['TABLE_TYPE'] + "', '" + i['TABLE_CATALOG'] + '.' + i[
                        'TABLE_SCHEMA'] + '.' \
                    + i['TABLE_NAME'] + "')"
            elif i['TABLE_TYPE'] == 'BASE TABLE':
                query_ddl[i['TABLE_CATALOG'] + '.' + i['TABLE_SCHEMA'] + '.' + i['TABLE_NAME']] = \
                    "SELECT GET_DDL('TABLE', '" + i['TABLE_CATALOG'] + '.' + i['TABLE_SCHEMA'] + '.' + \
                    i['TABLE_NAME'] + "')"

        df = pd.DataFrame([query_ddl]).T

        df_index = df.index

        df_return = pd.DataFrame(index=df_index)
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

        for k, v in df.iterrows():
            sql = v[0]
            cs.execute_async(sql)
            query_list[counter] = cs.sfqid
            df_return['sfqid'][k] = cs.sfqid
            counter += 1
        counter = 1
        if save_path is not None:
            if os.path.isfile(save_path):
                with open(save_path) as f:
                    d = json.load(f)
            else:
                d = {}
        else:
            d = {}
        for table in tables:
            d[table] = {}
        while process_complete == 0:
            item = -1
            process_pass += 1
            if sum(complete) == queries or process_pass == 1000:
                process_complete = 1
            for result in query_list:
                item += 1
                if complete[item] == 0:
                    print('Running ' + df_return[df_return['sfqid'] == result].index[0])
                    try:
                        status = cnn.get_query_status_throw_if_error(result)

                    except snowflake.connector.errors.ProgrammingError:
                        print(f"""Could not retrieve:
                            {df_return[df_return['sfqid'] == result].index[0]}

                            because of snowflake.connector.errors.ProgrammingError""")
                        complete[item] = 1
                        continue

                    except TypeError:
                        print(f"""Could not retrieve:
                            {df_return[df_return['sfqid'] == result].index[0]}

                        because TypeError: NoneType""")
                        complete[item] = 1
                        continue

                    print('the status for ' + df_return[df_return['sfqid'] == result].index[0] + ' is ' +
                          str(status) + ' ' + str(counter))
                    if str(status) == 'QueryStatus.SUCCESS':
                        complete[item] = 1
                        cs.get_results_from_sfqid(result)
                        data = cs.fetch_pandas_all()
                        for table in tables:
                            try:
                                if table.upper() + ' ' in data.iloc[0, 0][data.iloc[0, 0].upper().index(
                                        table.upper()):data.iloc[0, 0].upper().index(table.upper()) + len(table) + 1] \
                                        and table.upper() not in data.iloc[0, 0][:data.iloc[0, 0].index('(')]:
                                    d[table][df_return[df_return['sfqid'] == result].index[0]] = data.to_dict('index')
                            except ValueError:
                                continue
                    else:
                        time.sleep(.01)
                counter += 1
        cnn.close()
        return d

    def snowflake_dependencies(self,
                               tables: str | list,
                               username: str,
                               warehouse: str,
                               role: str,
                               database: str | None = None,
                               schema: str | list | None = None,
                               save_path: str | None = None,
                               filter_schemas: list | None = None,
                               recursive: bool = False
                               ):

        if filter_schemas is None:
            filter_schemas = []

        d = self.snowflake_dependencies_loop(tables=tables, username=username, warehouse=warehouse, role=role,
                                             database=database, schema=schema)
        print(d)
        # filter out schemas to be divested
        d_final = self.remove_schemas(d_dict=d, schema_list=filter_schemas)

        # list column names for the new dataframe and convert the .json file to .csv if the schema name is listed
        # within 10 the previous 10 characters of the table name
        col_names = ['Table', 'Object', 'DDL']
        df_final = self.dict_convert_into_dataframe(d_dict=d_final, cols=col_names, schema_list=filter_schemas)

        final_df = df_final

        final_df.columns = col_names

        if save_path is not None:
            final_df.to_csv(save_path)

        counter = 1

        if recursive:
            while len(df_final) > 0:
                # read the new file created from the above steps to check for sub-dependencies
                df_final_tables = []

                try:
                    [df_final_tables.append(v['Object'][v['Object'].rindex('.') + 1:]) for k, v in df_final.iterrows()]
                    df_final_tables = list(set(df_final_tables))
                except KeyError:
                    continue
                # iterate through the select get_ddl() for the 3375 tables and views in the NGP_DA_PROD database and
                # look for the dependent table names from the schemas to be divested
                d = self.snowflake_dependencies_loop(
                    tables=df_final_tables
                    , role=role
                    , database=database
                    , warehouse=warehouse
                    , username=username)

                # filter out schemas not to save
                d_final = self.remove_schemas(d_dict=d, schema_list=filter_schemas)

                df_final_schemas = []

                try:

                    [df_final_schemas.append(str(v['Object']).split('.')[1]) for k, v in final_df.iterrows()]

                    df_final_schemas = list(set(df_final_schemas))

                    df_final = self.dict_convert_into_dataframe(d_dict=d_final, cols=col_names,
                                                                schema_list=df_final_schemas)

                except KeyError:
                    continue

                df_final.columns = col_names

                for i, v in final_df.iterrows():
                    for x, y in df_final.iterrows():
                        try:
                            df_final.loc[x, 'MergeCol'] = v['Object'][:str(v['Object']).index('.') + 1] + y['Table']
                        except KeyError:
                            continue
                try:
                    final_df = final_df.merge(df_final, left_on='Object', right_on='MergeCol', how='left',
                                              suffixes=(f'_Round{str(counter)}', f'_Round{str(counter + 1)}'))
                    final_df.drop(columns=['MergeCol'], inplace=True)
                except KeyError:
                    continue

                counter += 1

                if save_path is not None:
                    final_df.to_csv(save_path)

        print('process complete')

        return final_df




