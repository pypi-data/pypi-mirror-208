
import _BuildSearchQuery
import _SnowflakePull
import _SnowflakeDependencies
# from Dashboards import Dashboards


class SnowflakeData(
                    _SnowflakePull.SnowflakePull
                    , _SnowflakeDependencies.SnowflakeDependencies
                    , _BuildSearchQuery.BuildSearchQuery):

    def snowflake_pull(self, query: str | dict | None, un, wh, db, role, schema=None, table=None,
                       sample_table: bool = False, sample_val: bool = False, table_sample: dict = None,
                       dtypes_conv=None, separate_dataframes: bool = True, polars: bool = True):

        return _SnowflakePull.SnowflakePull.snowflake_pull(self, query=query, un=un, wh=wh, db=db, role=role,
                                                           schema=schema, table=table, sample_table=sample_table,
                                                           sample_val=sample_val, table_sample=table_sample,
                                                           dtypes_conv=dtypes_conv,
                                                           separate_dataframes=separate_dataframes, polars=polars)

    def search_schema(self, un, wh, db, role, sample_table: bool = False, sample_val: bool = False,
                      table_sample: dict = None, dtypes_conv=None, schema=None, table=None, column_name=None,
                      col_and_or='and', get_ex_val=False, like_flag=True):

        import pandas as pd

        # --> pull data, filter out exclusions
        results = pd.DataFrame()
        if type(db) == list:
            queries = {}

            for k in db:
                queries[k] = _BuildSearchQuery.BuildSearchQuery.build_search_query(self, inp_db=k, schema=schema,
                                                                                   table=table, column_name=column_name,
                                                                                   like_flag=like_flag,
                                                                                   col_and_or=col_and_or)
                queries[k] = queries[k][:queries[k].find("INFORMATION_SCHEMA.COLUMNS")] + k + '.' + \
                    queries[k][queries[k].find("INFORMATION_SCHEMA.COLUMNS"):]

            df = _SnowflakePull.SnowflakePull.snowflake_pull(self, queries, un=un, wh=wh, role=role, db=None,
                                                             sample_table=sample_table, sample_val=sample_val,
                                                             table_sample=table_sample, dtypes_conv=dtypes_conv,
                                                             separate_dataframes=False)

            results = pd.concat([results, df], axis=0)

        elif db is None:
            # --> check user's database access for list of dbs to check
            get_dbs = _SnowflakePull.SnowflakePull.snowflake_pull(self, query='''SHOW DATABASES''', un=un, db=db, wh=wh,
                                                                  role=role)

            # list of user's db names
            db_names = list(get_dbs['name'].values)

            print(f"No input database --> checking all of databases in user's access: {len(db_names)} total databases")
            queries = {}
            for db in db_names:
                queries[db] = _BuildSearchQuery.BuildSearchQuery.build_search_query(self, inp_db=db, schema=schema,
                                                                                    table=table,
                                                                                    column_name=column_name,
                                                                                    like_flag=like_flag,
                                                                                    col_and_or=col_and_or)
                queries[db] = queries[db][:queries[db].find("INFORMATION_SCHEMA.COLUMNS")] + db + '.' + \
                              queries[db][queries[db].find("INFORMATION_SCHEMA.COLUMNS"):]

            temp_results = _SnowflakePull.SnowflakePull.snowflake_pull(self, query=queries, un=un, wh=wh, role=role,
                                                                       db=None,
                                                                       sample_table=sample_table, sample_val=sample_val,
                                                                       table_sample=table_sample,
                                                                       dtypes_conv=dtypes_conv,
                                                                       separate_dataframes=False)

            results = pd.concat([results, temp_results], axis=0)
        else:
            results = _SnowflakePull.SnowflakePull.snowflake_pull(
                self,
                query=_BuildSearchQuery.BuildSearchQuery.build_search_query(inp_db=db, schema=schema, table=table,
                                                           column_name=column_name, like_flag=like_flag,
                                                           col_and_or=col_and_or),
                un=un, db=db, wh=wh, role=role)

        # # drop exclusion rows
        results_fin = results

        # --> print result statement
        print(f'''
            Total table-columns found: {len(results_fin)}    

            Unique column names found: {list(results_fin['COLUMN_NAME'].unique())}
            Total = {len(list(results_fin['COLUMN_NAME'].unique()))}
                ''')

        # --> flagged to retrieve a sample value for each column
        if get_ex_val:
            results_fin['EX_VALS'] = None
            # --> loop through each row & retrieve values
            for indx, row in results_fin.iterrows():
                try:
                    row_res = _SnowflakePull.SnowflakePull.snowflake_pull(self, '', un=un, db=None, wh=wh, role=role,
                                                                          sample_val=True,
                                                                          table_sample={'db': row['TABLE_CATALOG'],
                                                                                        'schema': row['TABLE_SCHEMA'],
                                                                                        'table': row['TABLE_NAME'],
                                                                                        'col': row[
                                                                                            'COLUMN_NAME']})
                    # set row example values equal to unique column value list
                    row['EX_VALS'] = list(row_res[row['COLUMN_NAME']].unique())
                except Exception as e:
                    print(f"Could not pull {row['COLUMN_NAME']} for table: {row['TABLE_NAME']}")
                    print(e)
                    continue

        return results_fin

    def snowflake_dependencies(self, tables: str | list, username: str, warehouse: str, role: str,
                               database: str | None = None, schema: str | list | None = None, save_path: str = None,
                               filter_schemas: list | None = None, recursive: bool = False):

        return _SnowflakeDependencies.SnowflakeDependencies.snowflake_dependencies(self, tables=tables,
                                                                                   username=username,
                                                                                   warehouse=warehouse, role=role,
                                                                                   database=database, schema=schema,
                                                                                   save_path=save_path,
                                                                                   filter_schemas=filter_schemas,
                                                                                   recursive=recursive)

    def optimize_tbl_mem(self, username: str, warehouse: str, role: str, database: str = None, schema: str = None,
                         table_name: str = None, pull_all_cols=True, run_debugging: bool = False,
                         query=None):

        import numpy as np
        from NikeQA import QA

        from datetime import datetime

        if query is not None:
            query = str(query) + ' LIMIT 5' if query[-1] != ';' else str(
                query[:-1]) + ' LIMIT 5'  # add limit if user inputs a query (checking for semicolon at end of query)
            print(query)

        # --> DEBUGGING CODE: Return data profile if run for debugging purposes
        if run_debugging:
            t_sample = self.snowflake_pull(query=None, un=username, wh=warehouse, role=role, db=database,
                                           sample_table=True,
                                           table_sample={'db': database, 'schema': schema, 'table': table_name}
                                           if query is None else query)

            sample_prfl = QA(t_sample).data_prfl_analysis(ds_name='Table Sample', print_analysis=False)  # --> run data profiling function to get table info
            return sample_prfl

        # ======================================================================================================
        # --> DYNAMICALLY DETERMINE HOW TO CONVERT COLUMN DATA TYPES TO OPTIMIZE PYTHON-PANDAS MEMORY
        t_sample = self.snowflake_pull(query=None, un=username, wh=warehouse, role=role, db=database, sample_table=True,
                                       table_sample={'db': database, 'schema': schema, 'table': table_name}) \
            if query is None else self.snowflake_pull(query, username, warehouse, database, role=role)  # --> input table information from function inputs & sample table

        # --> determine column datatype conversions to make:
        sample_prfl = QA(t_sample).data_prfl_analysis(ds_name='Table Sample', print_analysis=False)  # --> run data profiling function to get table info

        sample_prfl['UNIQUE_PCT'] = (sample_prfl['UNIQUE_VALUES'] / (sample_prfl['NON_NULL_ROWS'])) * 100  # --> determine 0-100 percentage of unique values in the column

        for index, row in sample_prfl.iterrows():  # --> get the min/max values for all our integer columns
            sample_prfl.loc[index, 'INT_MIN'] = min(t_sample[row['COLUMN']]) if row['COL_DATA_TYPE'] == int else None
            sample_prfl.loc[index, 'INT_MAX'] = max(t_sample[row['COLUMN']]) if row['COL_DATA_TYPE'] == int else None

        # drop unneeded columns
        sample_prfl = sample_prfl[['COLUMN', 'COL_DATA_TYPE', 'UNIQUE_PCT', 'INT_MIN', 'INT_MAX']].copy()

        # --> run conversion rules to replace data types
        #    strings/keys/anything <> int w/ a distinct record on each row (>7% for our logic) = pd.StringDtype()
        #    integers = int64 (error handling), except 'int8' = 'int8'
        #    any float or decimals = float32
        #    any string/object that is not distinct on each row = 'category'
        #    any True/False fields = bool ('category' may also work)
        sample_prfl['DTYPE_CONV'] = np.where(
            ((sample_prfl['COL_DATA_TYPE'] == object) & (sample_prfl['UNIQUE_PCT'] <= 66)) | (
                        (sample_prfl['COL_DATA_TYPE'] == object) & (sample_prfl['UNIQUE_PCT'].isna())), 'category',
            # default string/object value
            np.where((sample_prfl['COL_DATA_TYPE'] == object) & (sample_prfl['UNIQUE_PCT'] > 66), str, #, pd.StringDtype(),
                     # objects w/ a distinct record on each row (>80% for our logic) = pd.StringDtype()
                     np.where(sample_prfl['COL_DATA_TYPE'] == int, 'int64',
                              # handles dtype error (makes other INT criteria irrelevant)
                              np.where(sample_prfl['COL_DATA_TYPE'] == 'int8', 'int8',  # default for any integer value
                                       np.where(sample_prfl['COL_DATA_TYPE'] == float, 'float32',  # float columns
                                                np.where(sample_prfl['COL_DATA_TYPE'] == bool, 'bool',
                                                         'ERROR'))))))  # True/False boolean columns

        # --> QA/ERROR checking
        error_flag = sample_prfl.loc[sample_prfl['DTYPE_CONV'] == 'ERROR'].copy().reset_index(drop=True)
        if len(error_flag) > 0:
            raise ValueError(f'''ERROR: the following columns have no data type conversion rule: {
                list(error_flag['COLUMN'].unique())}''')  # raise error if we're missing any conversion rules

        sample_prfl.index = sample_prfl['COLUMN']  # reset index to column name
        sample_prfl.drop(columns=['COLUMN', 'COL_DATA_TYPE', 'UNIQUE_PCT', 'INT_MIN', 'INT_MAX'],
                         inplace=True)  # drop unneeded columns

        dtypes = sample_prfl.to_dict()['DTYPE_CONV']  # convert to dictionary --> use for final query

        # ======================================================================================================
        # --> ANALYZE MEMORY OPTIMIZATION: get sample after memory conversion
        t_test = self.snowflake_pull(None, un=username, wh=warehouse, role=role, db=database, sample_table=True,
                                     table_sample={'db': database, 'schema': schema, 'table': table_name},
                                     dtypes_conv=dtypes) if query is None else self.snowflake_pull(
            query=query, un=username, wh=warehouse, role=role, db=database, dtypes_conv=dtypes)

        before_memory = t_sample.memory_usage(deep=True).sum()  # sample table memory usage (before conversion)
        after_memory = t_test.memory_usage(deep=True).sum()  # sample table memory usage (after conversion)

        print(f'''
        Sample table memory usage -->
        Before memory conversion: {before_memory / 1000000000} GB
        After memory conversion: {after_memory / 1000000000} GB
        Memory reduction percentage: {"{:.2%}".format((before_memory - after_memory) / before_memory)}

        Finished running! {datetime.now().strftime("%H:%M:%S")}
        ''')  # convert to GB & print total memory usage before & after conversion

        return dtypes  # --> return the datatypes to convert each column in the table to


