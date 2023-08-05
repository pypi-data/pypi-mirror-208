import _QA
import pandas as pd
from _GitHub import GitHub
from _SearchFiles import SearchFiles


class QA(_QA.QA, GitHub, SearchFiles):
    """
    A class for interacting with the data and doing basic QA
    """

    def __init__(self, df: pd.DataFrame = None, df2: pd.DataFrame = None, ds1_nm: str = 'Source #1',
                 ds2_nm: str = 'Source #2', case_sens: bool = True, print_analysis: bool = True, check_match_by=None,
                 breakdown_grain=None, token: str = None, tables: list | str = None, save_path: str = None,
                 username: str | None = None, warehouse: str | None = None, role: str | None = None,
                 database: str | None = None, schema: str | None = None, git_org: str | None = None,
                 git_username: str | None = None, pat: str | None = None, filename: str | None = None,
                 org_name: str | None = None, repo_name: str | None = None, savepath: str | None = None,
                 repo_list_filename: str | None = None, repo_directory_name: str | None = None,
                 directory_path: str | None = None, search_string: str | None = None, search_save_path: str = None):

        """

        :param df:
        :param df2: DataFrame | None = None
        :param ds1_nm: str = 'Source #1'
        :param ds2_nm: str = 'Source #2'
        :param case_sens: bool = True
        :param print_analysis: bool = True
        :param check_match_by: Any = None
        :param breakdown_grain: Any = None
        :param token: str = None

        """
        self.__git_org = git_org
        self.__df = df
        self.__df2 = df2
        self.__ds1_nm = ds1_nm
        self.__ds2_nm = ds2_nm
        self.__case_sens = case_sens
        self.__print_analysis = print_analysis
        self.__check_match_by = check_match_by
        self.__breakdown_grain = breakdown_grain
        self.__token = token
        self.__tables = tables
        self.__save_path = save_path
        self.__username = username
        self.__warehouse = warehouse
        self.__role = role
        self.__database = database
        self.__schema = schema
        self.__git_username = git_username
        self.__pat = pat
        self.__filename = filename
        self.__org_name = org_name
        self.__repo_name = repo_name
        self.__savepath = savepath
        self.__repo_list_filename = repo_list_filename
        self.__repo_directory_name = repo_directory_name
        self.__directory_path = directory_path
        self.__search_string = search_string
        self.__search_save_path = search_save_path

    # Getter and Setter Methods for Instance Variables
    @property
    def df(self):
        return self.__df

    @df.setter
    def df(self, value):
        self.__df = value

    @property
    def df2(self):
        return self.__df2

    @df2.setter
    def df2(self, value):
        self.__df2 = value

    @property
    def ds1_nm(self):
        return self.__ds1_nm

    @ds1_nm.setter
    def ds1_nm(self, value):
        self.__ds1_nm = value

    @property
    def ds2_nm(self):
        return self.__ds2_nm

    @ds2_nm.setter
    def ds2_nm(self, value):
        self.__ds2_nm = value

    @property
    def case_sens(self):
        return self.__case_sens

    @case_sens.setter
    def case_sens(self, value):
        self.__case_sens = value

    @property
    def print_analysis(self):
        return self.__print_analysis

    @print_analysis.setter
    def print_analysis(self, value):
        self.__print_analysis = value

    @property
    def check_match_by(self):
        return self.__check_match_by

    @check_match_by.setter
    def check_match_by(self, value):
        self.__check_match_by = value

    @property
    def breakdown_grain(self):
        return self.__breakdown_grain

    @breakdown_grain.setter
    def breakdown_grain(self, value):
        self.__breakdown_grain = value

    @property
    def token(self):
        return self.__token

    @token.setter
    def token(self, value):
        self.__token = value

    @property
    def tables(self):
        return self.__tables

    @tables.setter
    def tables(self, value):
        self.__tables = value

    @property
    def save_path(self):
        return self.__save_path

    @save_path.setter
    def save_path(self, value):
        self.__save_path = value

    @property
    def git_org(self):
        return self.__git_org

    @git_org.setter
    def git_org(self, value):
        self.__git_org = value

    @property
    def git_username(self):
        return self.__git_username

    @git_username.setter
    def git_username(self, value):
        self.__git_username = value

    @property
    def pat(self):
        return self.__pat

    @pat.setter
    def pat(self, value):
        self.__pat = value

    @property
    def filename(self):
        return self.__filename

    @filename.setter
    def filename(self, value):
        self.__filename = value

    @property
    def org_name(self):
        return self.__org_name

    @org_name.setter
    def org_name(self, value):
        self.__org_name = value

    @property
    def repo_name(self):
        return self.__repo_name

    @repo_name.setter
    def repo_name(self, value):
        self.__repo_name = value

    @property
    def savepath(self):
        return self.__savepath

    @savepath.setter
    def savepath(self, value):
        self.__savepath = value

    @property
    def repo_list_filename(self):
        return self.__repo_name

    @savepath.setter
    def savepath(self, value):
        self.__savepath = value

    @property
    def repo_directory_name(self):
        return self.__repo_directory_name

    @repo_directory_name.setter
    def repo_directory_name(self, value):
        self.__repo_directory_name = value

    @property
    def directory_path(self):
        return self.__directory_path

    @directory_path.setter
    def directory_path(self, value):
        self.__directory_path = value

    @property
    def search_string(self):
        return self.__search_string

    @search_string.setter
    def search_string(self, value):
        self.__search_string = value

    @property
    def search_save_path(self):
        return self.__search_save_path

    @search_save_path.setter
    def search_save_path(self, value):
        self.__search_save_path = value

    def column_gap_analysis(self, df: pd.DataFrame = None, df2: pd.DataFrame = None, ds1_nm: str = 'Source #1',
                            ds2_nm: str = 'Source #2', case_sens: bool = True, print_analysis: bool = True,
                            check_match_by=None, breakdown_grain=None):

        """
        Compares 2 DataFrames and gives shape, size, matching columns, non-matching columns, coverages, and percentages

        :param df: pd.DataFrame, optional, default = None
        :param df2: pd.DataFrame, optional, default = None
        :param ds1_nm: str, optional, default = 'Source #1'
        :param ds2_nm: str, optional, default = 'Source #2'
        :param case_sens: bool, optional, default = True
        :param print_analysis: bool, optional, default = True
        :param check_match_by: any, opioonal, default = None
        :param breakdown_grain: any, optional, default
        :return DataFrame
        """

        if df is None and self.__df:
            df = self.__df
        if df2 is None and self.__df2:
            df2 = self.__df2
        if df2 is None:
            raise ValueError(f'Please insert pandas.DataFrame for df2')
        if ds1_nm == 'Source #1':
            ds1_nm = self.__ds1_nm
        if ds2_nm == 'Source #2':
            ds2_nm = self.__ds2_nm
        if check_match_by is None and self.__check_match_by:
            check_match_by = self.__check_match_by
        if breakdown_grain is None and self.__breakdown_grain:
            breakdown_grain = self.__breakdown_grain

        return _QA.QA.column_gap_analysis(self, df2=df2, ds1_nm=ds1_nm, ds2_nm=ds2_nm, case_sens=case_sens,
                                          print_analysis=print_analysis, check_match_by=check_match_by,
                                          breakdown_grain=breakdown_grain, df1=df)

    def data_prfl_analysis(self, df: pd.DataFrame = None, ds_name: str = 'Data Source', sample_vals: int = 5,
                           print_analysis: bool = True, show_pct_fmt: bool = True):

        """

        :param df: pandas.DataFrame to be analyzed
        :param ds_name: name of the data source to be included in the output
        :param sample_vals:
        :param print_analysis:
        :param show_pct_fmt:
        :return: pandas.Dataframe with the following columns ['DATA_SOURCE', 'COLUMN', 'COL_DATA_TYPE', 'TOTAL_ROWS',
        'ROW_DTYPE_CT', 'PRIMARY_DTYPE_PCT', 'COVERAGE_PCT', 'NULL_PCT', 'DTYPE_ERROR_FLAG', 'NON_NULL_ROWS',
        'NULL_VALUES', 'UNIQUE_VALUES', 'COL_VALUE_SAMPLE', 'NULL_VALUE_SAMPLE']
        """

        if df is None:
            df = self.__df

        return _QA.QA.data_prfl_analysis(self, df=df, ds_name=ds_name, sample_vals=sample_vals,
                                         print_analysis=print_analysis, show_pct_fmt=show_pct_fmt)

    def github_dependencies(self, tables: list | str = None, token: str | None = None, save_path: str = None,
                            org: str = ''):

        if token is None and self.__token is not None:
            token = self.__token
        if tables is None and self.__tables is not None:
            tables = self.__tables
        if org is None and self.__git_org is not None:
            org = self.__git_org

        return GitHub.github_dependencies(self, token=token, tables=tables, save_path=save_path, org=org)

    def get_repo_list(self, username: str = None, pat: str | None = None, org_name: str | None = None,
                      repo_list_filename: str | None = None):
        print(username, pat, org_name, 'test')
        if username is None and self.__git_username is not None:
            username = self.__git_username
        if pat is None and self.__pat is not None:
            pat = self.__pat
        if org_name is None and self.__org_name is not None:
            org_name = self.__org_name
        if repo_list_filename is None and self.__repo_list_filename is not None:
            repo_list_filename = self.__repo_list_filename
        print(username, pat, org_name, 'test')

        return GitHub.get_repo_list(self, git_username=username, pat=pat, org_name=org_name,
                                    repo_list_filename=repo_list_filename)

    def git_clone(self, username: str = None, pat: str = None, filename: str = None, org_name: str = None,
                  repo_name: str = None, repo_list_filename: str = None, repo_directory_name: str | None = None):

        if username is None:
            username = self.__git_username
        if pat is None:
            pat = self.__pat
        if filename is None:
            filename = self.__filename
        if org_name is None:
            org_name = self.__org_name
        if repo_name is None:
            repo_name = self.__repo_name
        if repo_list_filename is None:
            repo_list_filename = self.__repo_list_filename
        if repo_directory_name is None:
            repo_directory_name = self.__repo_directory_name

        return GitHub.get_clone(self, git_username=username, pat=pat, filename=filename, org_name=org_name,
                                repo_name=repo_name, repo_list_filename=repo_list_filename,
                                repo_directory_name=repo_directory_name)

    def search_files(self, directory_path: str = None, search_string: str or list = None, search_save_path: str = None):

        if directory_path is None:
            directory_path = self.__directory_path
        if search_string is None:
            search_string = self.__search_string
        if search_save_path is None:
            search_save_path = self.__search_save_path

        return SearchFiles.search_files(self, directory_path=directory_path, search_string=search_string,
                                        save_path=search_save_path)

    def search_dependencies(self, tables: list | str = None,
                            token: str | None = None,
                            save_path: str = None,
                            username: str | None = None,
                            warehouse: str | None = None,
                            role: str | None = None,
                            database: str | None = None,
                            schema: str | list | None = None,
                            github_save_path: str | None = None,
                            snowflake_save_path: str | None = None):

        from NikeCA import Snowflake
        import json

        """

        :param token: 
        :param save_path:
        :param tables:
        :param username:
        :param warehouse:
        :param role:
        :param database:
        :param schema:
        :return:
        """

        if tables is None:
            tables = self.__tables
        if username is None:
            username = self.__username
        if warehouse is None:
            warehouse = self.__warehouse
        if role is None:
            role = self.__role
        if database is None:
            database = self.__database
        if schema is None:
            schema = self.__schema
        if save_path is None:
            save_path = self.__save_path
        if token is None:
            token = self.__token
        if tables is None:
            tables = self.__tables

        gh = GitHub.github_dependencies(self, token=token, tables=tables, save_path=github_save_path)
        sf = Snowflake(username=username, warehouse=warehouse, role=role).snowflake_dependencies(tables=tables,
                                                                                                 database=database,
                                                                                                 schema=schema,
                                                                                                 save_path=snowflake_save_path)

        d = {'github_dependencies': gh, 'snowflake_dependencies': sf}

        if save_path is not None:
            with open(save_path, "w+") as f:
                json.dump(d, f, indent=4)

        return d

