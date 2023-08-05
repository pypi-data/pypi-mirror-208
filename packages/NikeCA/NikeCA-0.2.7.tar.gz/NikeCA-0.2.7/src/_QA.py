

class QA:

    def column_gap_analysis(self, df1,  df2, ds1_nm='Source #1', ds2_nm='Source #2', case_sens=True,
                            print_analysis=True, check_match_by=None, breakdown_grain=None):

        import time # timer package
        import pandas as pd
        import itertools

        # ERROR CHECKING #
        if (len(df1) == 0) | (len(df2) == 0):
            raise ValueError(f'''
            ERROR: one of the input data sources contains 0 rows of data
                Source #1: {len(df1)}
                Source #2: {len(df2)}
            ''')

        # other 'NULL' values to check for
        null_val_criteria = ['', ' ', '  ', '   ', 'N/A', 'NA', '*UNK*', 'UNKNOWN INTENDED USE', 'UNKNOWN DIMENSION',
                             '* DO NOT USE - TEST AFLSWNS SL', '*NUK*', 'UNKNOWN', None, '[]']

        # start timer
        tic = time.perf_counter()
        # --> uppercase all column names if case-sensitive flag is False
        if not case_sens:
            df1.columns = df1.columns.str.upper()
            df2.columns = df2.columns.str.upper()

        # data source 1 - # cols
        df1_cols = len(list(df1.columns))

        # data source 2 - # cols
        df2_cols = len(list(df2.columns))

        # matching cols
        match_cols = sorted([x for x in list(df1.columns) if x in (list(df2.columns))])

        # non-matching cols
        df1_non_matches = sorted([x for x in list(df1.columns) if x not in (list(df2.columns))])

        # non-matching cols
        df2_non_matches = sorted([x for x in list(df2.columns) if x not in (list(df1.columns))])

        # % of matching columns
        pct_match = 1 - ((len(df1_non_matches) + len(df2_non_matches)) / (df1_cols + df2_cols))

        # MATCHING COLUMNS ONLY --> determine coverage %
        results_df = pd.DataFrame(itertools.zip_longest(match_cols, df1_non_matches, df2_non_matches), columns=[
            'COL_MATCHES', f'{ds1_nm}_NON_MATCHES', f'{ds2_nm}_NON_MATCHES'])

        if len(match_cols) > 0:

            # --> perform analysis:

            # --> function: format dataframes for check_match_by flag = True analysis
            def format_df(inp_df, col_x):
                # drop any NA row
                f_df = inp_df[[col_x, check_match_by]].copy().dropna().reset_index(drop=True)

                # remove other NULL value rows
                f_df = f_df.loc[~(f_df[col_x].isin(null_val_criteria))].copy().reset_index(drop=True)

                # remove other NULL value rows
                f_df = f_df.loc[~(f_df[check_match_by].isin(null_val_criteria))].copy().reset_index(drop=True)

                # drop extra unneeded column
                f_df.drop(columns=[check_match_by], inplace=True)

                # drop duplicate records & reset index
                f_df = f_df.drop_duplicates().reset_index(drop=True)

                return f_df

            # --> function: compare
            def check_coverage(temp_df1, temp_df2, col_x, grain_brkdwn=None):

                # get ALL unique values in the matching columns
                if (col_x == check_match_by) | (check_match_by is None):

                    # total values in dataframe-column, excluding NA values
                    # ds1 unique values
                    ds1_uniq_val = pd.DataFrame(temp_df1.loc[~temp_df1[col_x].isna(),
                                                             col_x].copy()).drop_duplicates().reset_index(drop=True)

                    # ds2 unique values
                    ds2_uniq_val = pd.DataFrame(temp_df2.loc[~temp_df2[col_x].isna(),
                                                             col_x].copy()).drop_duplicates().reset_index(drop=True)

                # get ALL unique values in columns where the check_match_by column IS ALSO NOT NULL
                else:
                    ds1_uniq_val = format_df(temp_df1, col_x) # format dfs
                    ds2_uniq_val = format_df(temp_df2, col_x)

                try:
                    # ds1 values also in ds2
                    coverage_vals1 = ds1_uniq_val.merge(ds2_uniq_val, how='inner', on=x)

                    # ds2 values also in ds1
                    coverage_vals2 = ds2_uniq_val.merge(ds1_uniq_val, how='inner', on=x)
                except:
                    print(f'Dtype mismatch for {col_x}')
                    try: # --> attempt to convert datatypes & merge again

                        # ds1 values also in ds2
                        coverage_vals1 = ds1_uniq_val.merge(ds2_uniq_val.astype(ds1_uniq_val.dtypes[0]),
                                                            how='inner', on=x)

                        # ds2 values also in ds1
                        coverage_vals2 = ds2_uniq_val.merge(ds1_uniq_val.astype(ds2_uniq_val.dtypes[0]), how='inner',
                                                            on=x)
                    except:
                        raise ValueError \
                            (f'Could not fix Dtype mismatch on {col_x}: {ds1_uniq_val.dtypes[0]} vs '
                             f'{ds2_uniq_val.dtypes[0]} - fix formatting before running again')

                # calculate % of ds1 values covered by ds2
                # ds1 denominator
                ds1_den = len(ds1_uniq_val)

                # ds2 numerator
                ds2_num = len(coverage_vals1)

                # calculate % of ds2 values covered by ds1
                ds2_den = len(ds2_uniq_val) # ds1 denominator
                ds1_num = len(coverage_vals2) # ds2 numerator

                if grain_brkdwn is None:
                    try:

                        # append values to final list
                        val_holder.append([ds1_nm, ds2_nm, col_x, ds1_den, ds2_num, "{:.2%}".format(ds2_num / ds1_den)])
                        val_holder.append([ds2_nm, ds1_nm, col_x, ds2_den, ds1_num, "{:.2%}".format(ds1_num / ds2_den)])
                    except:
                        val_holder.append([ds1_nm, ds2_nm, col_x, ds1_den, ds2_num, "No pct"]) # append values to final list
                        val_holder.append([ds2_nm, ds1_nm, col_x, ds2_den, ds1_num, "No pct"])
                else:
                    try:
                        val_holder.append([ds1_nm, ds2_nm, col_x, grain_brkdwn, ds1_den, ds2_num, "{:.2%}".format(ds2_num / ds1_den)]) # append values to final list
                        val_holder.append \
                            ([ds2_nm, ds1_nm, col_x, grain_brkdwn, ds2_den, ds1_num, "{:.2%}".format(ds1_num / ds2_den)])
                    except:
                        val_holder.append([ds1_nm, ds2_nm, col_x, grain_brkdwn, ds1_den, ds2_num, "No pct"]) # append values to final list
                        val_holder.append([ds2_nm, ds1_nm, col_x, grain_brkdwn, ds2_den, ds1_num, "No pct"])


            val_holder = [] # data container
            for x in list(results_df.loc[~results_df['COL_MATCHES'].isna(), 'COL_MATCHES']):

                if breakdown_grain != None: # compare values by other grain
                    for val in (val for val in [*set(list(df1[breakdown_grain].unique()) + list(df2[breakdown_grain].unique()))] if val != None): # get all values from both lists
                        grain_df1 = df1.loc[df1[breakdown_grain] == val].copy().reset_index(drop=True)
                        grain_df2 = df2.loc[df2[breakdown_grain] == val].copy().reset_index(drop=True)
                        check_coverage(grain_df1, grain_df2, x, val)
                else:
                    check_coverage(df1, df2, x)

        # --> print analysis statement if specified
        if print_analysis == True:
            print(f'''
    ========================================================= DATA SOURCES ==========================================================
    Data Source #1: {ds1_nm}
    Data Source #2: {ds2_nm}
    ==================================================== DATAFRAME DESCRIPTIONS =====================================================
    (# rows, # cols)
    
    {ds1_nm} shape = {df1.shape}
    {ds1_nm} size = {df1.size}
    {ds2_nm} shape = {df2.shape}
    {ds2_nm} size = {df2.size}
    ======================================================== COLUMN MATCHES =========================================================
    
    Case sensitive? {case_sens}
    {len(match_cols)} matching column(s): {match_cols}
    {ds1_nm} non-matching column(s): {df1_non_matches}
    {ds2_nm} non-matching column(s): {df2_non_matches}
    ====================================================== PERCENTAGE MATCHING ======================================================
    Overall % column matches: {"{:.2%}".format(pct_match)} ({len(match_cols) * 2}/{(df1_cols + df2_cols)})
    {ds1_nm} % columns in {ds2_nm}:     {"{:.2%}".format(1 - (len(df1_non_matches) / df1_cols))} ({df1_cols - len(df1_non_matches)}/{df1_cols})
    {ds2_nm} % columns in {ds1_nm}:     {"{:.2%}".format(1 - (len(df2_non_matches) / df2_cols))} ({df2_cols - len(df2_non_matches)}/{df2_cols})
    Analysis time: {time.perf_counter() - tic:0.4f} seconds ({(time.perf_counter() - tic) / 60:0.4f} minutes)
            ''')

        try: # return column-value comparison if we have matching columns
            fin_cols = ['DS1_NAME', 'DS2_NAME', 'COLUMN', 'DS1_UNIQ_COL_VALS', 'DS2_MATCHING_VALS', 'DS2_COVERAGE_PCT'] if breakdown_grain == None else ['DS1_NAME', 'DS2_NAME', 'COLUMN', f'{breakdown_grain}_VALUE', 'DS1_UNIQ_COL_VALS', 'DS2_MATCHING_VALS', 'DS2_COVERAGE_PCT']
            return pd.DataFrame(data=val_holder, columns=fin_cols).sort_values(by=['DS1_NAME', 'COLUMN'], ascending=True).reset_index(drop=True)
        except: # return matching column results otherwise
            return results_df

    def data_prfl_analysis(self, df, ds_name='Data Source', sample_vals=5, print_analysis=True,
                           show_pct_fmt=True):  # --> sample values to take from each col

        import time  # timer package
        import pandas as pd
        import numpy as np
        from datetime import datetime

        if len(df) == 0:
            return pd.DataFrame(data=[],
                                columns=['DATA_SOURCE', 'COLUMN', 'COL_DATA_TYPE', 'TOTAL_ROWS', 'ROW_DTYPE_CT',
                                         'PRIMARY_DTYPE_PCT', 'COVERAGE_PCT', 'NULL_PCT',
                                         'DTYPE_ERROR_FLAG', 'NON_NULL_ROWS', 'NULL_VALUES', 'UNIQUE_VALUES',
                                         'COL_VALUE_SAMPLE', 'NULL_VALUE_SAMPLE'])

        print(f'Started data profiling query: {datetime.now().strftime("%H:%M:%S")}')
        tic = time.perf_counter()  # start timer
        analysis_keys = []  # --> stores information about columns in a data source
        null_val_criteria = ['', ' ', '  ', '   ', 'N/A', 'NA', '*UNK*', 'UNKNOWN INTENDED USE', 'UNKNOWN DIMENSION',
                             '* DO NOT USE - TEST AFLSWNS SL', '*NUK*', 'UNKNOWN', None,
                             '[]']  # other 'NULL' values to check for
        map_df = df.applymap(lambda x: type(x).__name__, na_action='ignore')  # dataframe data type mapping

        for col in list(df.columns):  # loop through each column in data source & get:
            total_col_vals = len(df[col].values)  # total rows in the column
            null_col_vals = len(
                df.loc[(df[col].isna()) | (df[col].isin(null_val_criteria))][col].values)  # NULL/unknown values only
            uniq_col_vals = len(np.unique(df.loc[~((df[col].isna()) | (df[col].isin(null_val_criteria)))][
                                              col].values))  # unique values, excluding NULL values
            row_dtypes = map_df[col].value_counts(
                sort=True).to_dict()  # --> check that row value data types match column data type
            max_dtype_val = max(row_dtypes.values()) if len(row_dtypes) > 0 else 0  # max values of 1 data type
            row_dtypes['NULL'] = null_col_vals  # add NULL values into dictionary
            dtype_error_flag = True if (null_col_vals + max_dtype_val) != total_col_vals else False
            null_list = list(df.loc[(df[col].isna()) | (df[col].isin(null_val_criteria))][col].unique())

            # add: column name, data type, # total rows, row datatypes, % primary dtype, % null values, # null rows,
            # unique values, unique value list, NULL value list
            analysis_keys.append([ds_name, col, df[col].dtype, total_col_vals, row_dtypes,
                                  "{:.2%}".format(max_dtype_val / total_col_vals) if show_pct_fmt else (
                                              max_dtype_val / total_col_vals),
                                  "{:.2%}".format(1 - (null_col_vals / total_col_vals)) if show_pct_fmt else (
                                              1 - (null_col_vals / total_col_vals)),
                                  "{:.2%}".format(null_col_vals / total_col_vals) if show_pct_fmt else (
                                              null_col_vals / total_col_vals),
                                  dtype_error_flag, total_col_vals - null_col_vals,
                                  null_col_vals, uniq_col_vals,
                                  sorted(list(np.unique(df.loc[~df[col].isna()][col].values))[:sample_vals]),
                                  'No NULLs' if len(null_list) == 0 else null_list])

        # return results dataframe analysis
        # --> COL_VALUE_SAMPLE includes 5 sample values (or more if specified) from the column
        results_df = pd.DataFrame(data=analysis_keys,
                                  columns=['DATA_SOURCE', 'COLUMN', 'COL_DATA_TYPE', 'TOTAL_ROWS', 'ROW_DTYPE_CT',
                                           'PRIMARY_DTYPE_PCT', 'COVERAGE_PCT', 'NULL_PCT',
                                           'DTYPE_ERROR_FLAG', 'NON_NULL_ROWS', 'NULL_VALUES', 'UNIQUE_VALUES',
                                           'COL_VALUE_SAMPLE', 'NULL_VALUE_SAMPLE'])
        dtype_counts = df.dtypes.value_counts()  # count of column datatypes
        dtype_statement = ''  # placeholder
        for i in list(dtype_counts.index):  # add a count for each datatype in the df
            dtype_statement += f'''({str(i)}: {str(dtype_counts[i])}); '''

        # --> function: get the # of columns with a % of NULL values >= input %
        def get_null_cols(pct):
            return len(results_df.loc[(results_df['NULL_VALUES'] / results_df['TOTAL_ROWS']) >= pct])

        analysis_statement = (f'''    
    * Finished data profiling for:      {ds_name}
    ============================================================================================================================================
    Total columns:                      {len(list(df.columns))}
    Sampled rows:                       {len(df)}
    ============================================================================================================================================
    Total 100% NULL value columns:      {get_null_cols(1)} ({"{:.2%}".format(get_null_cols(1) / len(list(df.columns)))} of columns)
        >=90% NULL value columns:       {get_null_cols(.9)} ({"{:.2%}".format(get_null_cols(.9) / len(list(df.columns)))} of columns)
        >=75% NULL value columns:       {get_null_cols(.75)} ({"{:.2%}".format(get_null_cols(.75) / len(list(df.columns)))} of columns)
        >=50% NULL value columns:       {get_null_cols(.5)} ({"{:.2%}".format(get_null_cols(.5) / len(list(df.columns)))} of columns)
        >=25% NULL value columns:       {get_null_cols(.25)} ({"{:.2%}".format(get_null_cols(.25) / len(list(df.columns)))} of columns)
        >=10% NULL value columns:       {get_null_cols(.1)} ({"{:.2%}".format(get_null_cols(.1) / len(list(df.columns)))} of columns)  
    Total >0% NULL value columns:       {get_null_cols(.00001)} ({"{:.2%}".format(get_null_cols(.00001) / len(list(df.columns)))} of columns)
    ============================================================================================================================================
    Column Data Types: {dtype_statement}
    ============================================================================================================================================ 
    # columns w/ non-matching dtype values:   {len(results_df.loc[results_df['DTYPE_ERROR_FLAG'] == True])} ({"{:.2%}".format(len(results_df.loc[results_df['DTYPE_ERROR_FLAG'] == True]) / len(list(df.columns)))} of columns)

        columns: {list(results_df.loc[results_df['DTYPE_ERROR_FLAG'] == True]['COLUMN'].unique())}     
    ''')  # --> final analysis

        print(f'''
    ============================================================================================================================================    
    Analysis time: {time.perf_counter() - tic:0.4f} seconds ({(time.perf_counter() - tic) / 60:0.4f} minutes)
    ============================================================================================================================================   
    ''')
        if print_analysis:
            print(analysis_statement)  # print analysis of results

        return results_df.sort_values(['COLUMN', 'UNIQUE_VALUES'], ascending=[True, False])

