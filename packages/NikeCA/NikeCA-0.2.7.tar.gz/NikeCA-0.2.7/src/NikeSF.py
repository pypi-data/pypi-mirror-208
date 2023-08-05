import pandas as pd

from _SnowflakeData import SnowflakeData
from _BuildSearchQuery import BuildSearchQuery
from _SnowflakeDependencies import SnowflakeDependencies


class Snowflake(SnowflakeData, SnowflakeDependencies, BuildSearchQuery):


    """
        A class for interacting with Snowflake databases and executing queries.
        Inherits from _SnowflakeData.SnowflakeData.
        """

    # Constructor
    def __init__(self, username: str, warehouse: str, role: str, database: str = None, schema: str = None,
                 table: str = None, column_name: str = None, col_and_or: str = 'AND', get_ex_val: bool = None,
                 like_flag: bool = False, sample_table: bool = False, sample_val: bool = False,
                 table_sample: dict = None, dtypes_conv=None, query='', separate_dataframes: bool = False,
                 tables: list | str | None = None, save_path: str | None = None, date_min: str | None = None,
                 date_max: str | None = None, column_filters: list | None = None, polars: bool = False):
        """
        Parameters:

            username (str): The Snowflake account username.
            warehouse (str): The Snowflake warehouse to use.
            role (str): The Snowflake role to use.
            database (str, optional): The Snowflake database to use (default is None).
            schema (str, optional): The Snowflake schema to use (default is None).
            table (str, optional): The Snowflake table to use (default is None).
            column_name (str, optional): The name of the column to search (default is None).
            col_and_or (str, optional): The AND/OR operator to use between search criteria (default is None).
            get_ex_val (bool, optional): Whether to return exact matches only (default is None).
            like_flag (bool, optional): Whether to use the LIKE operator for search criteria (default is None).
        """

        self.__username = username
        self.__warehouse = warehouse
        self.__role = role
        self.__database = database
        self.__schema = schema
        self.__table = table
        self.__column_name = column_name
        self.__col_and_or = col_and_or
        self.__get_ex_val = get_ex_val
        self.__like_flag = like_flag
        self.__sample_table = sample_table
        self.__sample_val = sample_val
        self.__table_sample = table_sample
        self.__dtypes_conv = dtypes_conv
        self.__query = query
        self.__separate_dataframes = separate_dataframes
        self.__tables = tables
        self.__save_path = save_path
        self.__date_min = date_min
        self.__date_max = date_max
        self.__column_filters = column_filters
        self.__polars = polars

    # Getter and Setter Methods for Instance Variables
    @property
    def username(self):
        return self.__username

    @username.setter
    def username(self, value):
        self.__username = value

    @property
    def warehouse(self):
        return self.__warehouse

    @warehouse.setter
    def warehouse(self, value):
        self.__warehouse = value

    @property
    def role(self):
        return self.__role

    @role.setter
    def role(self, value):
        self.__role = value

    @property
    def database(self):
        return self.__database

    @database.setter
    def database(self, value):
        self.__database = value

    @property
    def schema(self):
        return self.__schema

    @schema.setter
    def schema(self, value):
        self.__schema = value

    @property
    def table(self):
        return self.__table

    @table.setter
    def table(self, value):
        self.__table = value

    @property
    def column_name(self):
        return self.__column_name

    @column_name.setter
    def column_name(self, value):
        self.__column_name = value

    @property
    def col_and_or(self):
        return self.__col_and_or

    @col_and_or.setter
    def col_and_or(self, value):
        self.__col_and_or = value

    @property
    def get_ex_val(self):
        return self.get_ex_val

    @get_ex_val.setter
    def get_ex_val(self, value):
        self.__get_ex_val = value

    @property
    def like_flag(self):
        return self.__like_flag

    @like_flag.setter
    def like_flag(self, value):
        self.__like_flag = value

    @property
    def sample_table(self):
        return self.__sample_table

    @sample_table.setter
    def sample_table(self, value):
        self.__sample_table = value

    @property
    def sample_val(self):
        return self.__sample_val

    @sample_val.setter
    def sample_val(self, value):
        self.__sample_val = value

    @property
    def table_sample(self):
        return self.__table_sample

    @table_sample.setter
    def table_sample(self, value):
        self.__table_sample = value

    @property
    def dtypes_conv(self):
        return self.__dtypes_conv

    @dtypes_conv.setter
    def dtypes_conv(self, value):
        self.__dtypes_conv = value

    @property
    def query(self):
        return self.__query

    @query.setter
    def query(self, value):
        self.__query = value

    @property
    def separate_dataframes(self):
        return self.__separate_dataframes

    @separate_dataframes.setter
    def separate_dataframes(self, value):
        self.__separate_dataframes = value

    @property
    def tables(self):
        return self.__tables

    @tables.setter
    def tables(self, value):
        self.__table = value

    @property
    def save_path(self):
        return self.__save_path

    @save_path.setter
    def save_path(self, value):
        self.__save_path = value

    @property
    def date_min(self):
        return self.__date_min

    @date_min.setter
    def date_min(self, value):
        self.__date_min = value

    @property
    def date_max(self):
        return self.__date_max

    @date_max.setter
    def date_max(self, value):
        self.__date_max = value

    @property
    def column_filters(self):
        return self.__column_filters

    @column_filters.setter
    def column_filters(self, value):
        self.__column_filters = value

    @property
    def polars(self):
        return self.__polars

    @polars.setter
    def polars(self, value):
        self.__polars = value

    @property
    def Dashboards(self):
        from Dashboards.Dashboards import Dashboards
        return Dashboards(username=self.username, role=self.role, database=self.database, warehouse=self.warehouse)

    @property
    def Telemetry(self):
        from Dashboards.Telemetry.Telemetry import Telemetry
        return Telemetry(username=self.username, role=self.role, database=self.database, warehouse=self.warehouse)

    @property
    def InclusionExclusion(self):
        from Dashboards.InclusionExclusion.InclusionExclusion import InclusionExclusion
        return InclusionExclusion(username=self.username, role=self.role, database=self.database, warehouse=self.warehouse)


    def test(self):
        print('teste')
    def build_search_query(self
                           , inp_db: str = None
                           , schema: str = None
                           , table: str = None
                           , column_name=None
                           , like_flag: bool = False
                           , col_and_or: str = 'AND'
                           ):
        """
        Builds and returns a search query based on the specified parameters and instance variables.

        Parameters:
            inp_db (str or None, optional): The database to use (default is None).
            schema (str or None, optional): The schema to use (default is None).
            table (str or None, optional): The table to search (default is None).
            column_name (str or list or None, optional): The name of the column to search (default is None).
            like_flag (bool, optional): Whether to use the LIKE operator for search criteria (default is False).
            col_and_or (str, optional): The AND/OR operator to use between search criteria (default is AND).
        """

        if schema is None:
            schema = self.__schema
        if table is None:
            table = self.__table
        if column_name is None:
            column_name = self.__column_name
        if (not like_flag) and self.__like_flag:
            like_flag = self.__like_flag
        if col_and_or.lower() == 'and' and self.__col_and_or:
            col_and_or = self.__col_and_or

        return BuildSearchQuery.build_search_query(self, inp_db=inp_db, schema=schema, table=table,
                                                   column_name=column_name, like_flag=like_flag,
                                                   col_and_or=col_and_or)

    def snowflake_pull(self,
                       query: str | dict,
                       username: str = None,
                       warehouse: str = None,
                       database: str = None,
                       role: str = None,
                       schema: str = None,
                       table: str = None,
                       sample_table: bool = False,
                       sample_val: bool = False,
                       table_sample: dict = None,
                       dtypes_conv=None,
                       separate_dataframes: bool = True,
                       polars: bool = False
                       ):

        """
        Executes a query in Snowflake and returns the results as a Pandas DataFrame.

        Parameters:
            query (str): The SQL query to execute.
            username (str, optional): The Snowflake username to use. If not provided, uses the one set in the class
                                      constructor.
            warehouse (str, optional): The Snowflake warehouse to use. If not provided, uses the one set in the class
                                       constructor.
            database (str, optional): The Snowflake database to use. If not provided, uses the one set in the class
                                      constructor.
            role (str, optional): The Snowflake role to use. If not provided, uses the one set in the class constructor.
            sample_table (bool, optional): Whether to return only a sample of the result table. Defaults to False.
            sample_val (bool, optional): Whether to return only a sample of the result values. Defaults to False.
            table_sample (dict, optional): Dictionary containing the number of rows to return per table in the query.
                                           If not provided, returns all rows. Defaults to None.
            dtypes_conv (dict, optional): Dictionary containing the column names and their desired data types. If not
                                          provided, uses the default data types.

        Returns:
            pandas.DataFrame: The results of the query as a Pandas DataFrame.
            :param polars:
            :param separate_dataframes:
            :param dtypes_conv:
            :param sample_val:
            :param table_sample:
            :param sample_table:
            :param query:
            :param username:
            :param warehouse:
            :param database:
            :param role:
            :param table:
            :param schema:
        """

        # Set default values for the parameters if they are not provided
        if username is None:
            username = str(self.__username)
        if warehouse is None:
            warehouse = self.__warehouse
        if database is None:
            database = self.__database
        if role is None:
            role = self.__role
        if schema is None:
            schema = self.__schema
        if table is None:
            table = self.__table
        if not sample_table:
            sample_table = self.__sample_table
        if not sample_val:
            sample_val = self.__sample_val
        if table_sample is None:
            table_sample = self.__table_sample
        if dtypes_conv is None:
            dtypes_conv = self.__dtypes_conv
        if not separate_dataframes:
            separate_dataframes = self.__separate_dataframes
        if not polars:
            polars = self.__polars

        # Call the snowflake_pull method from the _SnowflakeData module using the provided or default parameters
        return SnowflakeData.snowflake_pull(self, query, un=username, wh=warehouse, db=database,role=role,
                                            schema=schema, table=table, sample_table=sample_table,
                                            sample_val=sample_val, table_sample=table_sample, dtypes_conv=dtypes_conv,
                                            separate_dataframes=separate_dataframes, polars=polars)

    def search_schema(self,
                      username: str = None,
                      warehouse: str = None,
                      database: str = None,
                      role: str = None,
                      sample_table: bool = False,
                      sample_val: bool = False,
                      table_sample: dict = None,
                      dtypes_conv=None,
                      schema: str = None,
                      table: str = None,
                      column_name: str = None,
                      col_and_or='and',
                      get_ex_val: bool = False,
                      like_flag: bool = False
                      ) -> pd.DataFrame:

        """
        search snowflake structure for specific schema/table/column;
        (optional) specify to return example values from each table-column

        :param username: Any = None
        :param warehouse: Any = None
        :param database: Any = None
        :param role: Any = None
        :param sample_table: bool = False
        :param sample_val: bool = False
        :param table_sample: dict | None = None
        :param dtypes_conv: Any = None
        :param schema: Any = None
        :param table: Any = None
        :param column_name: Any = None
        :param col_and_or: str = 'and'
        :param get_ex_val: bool = False
        :param like_flag: bool = False
        :return: DataFrame
        """

        if username is None:
            username = self.__username
        if warehouse is None:
            warehouse = self.__warehouse
        if database is None:
            database = self.__database
        if role is None:
            role = self.__role
        if not sample_table and self.__sample_table:
            sample_table = self.__sample_table
        if not sample_val and self.__sample_val:
            sample_val = self.__sample_val
        if table_sample is None and self.__table_sample:
            table_sample = self.__table_sample
        if dtypes_conv is None and self.__dtypes_conv:
            dtypes_conv = self.__dtypes_conv
        if schema is None and self.__schema:
            schema = self.__schema
        if table is None and self.__table:
            table = self.__table
        if column_name is None and self.__column_name:
            column_name = self.__column_name
        if col_and_or == 'and' and self.__col_and_or:
            col_and_or = self.__col_and_or
        if not get_ex_val and self.__get_ex_val:
            get_ex_val = self.__get_ex_val
        if not like_flag and self.__like_flag:
            like_flag = self.__like_flag

        return SnowflakeData.search_schema(self, un=username, wh=warehouse, db=database, role=role,
                                           sample_table=sample_table, sample_val=sample_val,
                                           table_sample=table_sample, dtypes_conv=dtypes_conv,
                                           schema=schema, table=table, column_name=column_name,
                                           col_and_or=col_and_or, get_ex_val=get_ex_val,
                                           like_flag=like_flag)

    def optimize_tbl_mem(self,
                         username: str | None = None,
                         warehouse: str | None = None,
                         role: str | None = None,
                         database: str | None = None,
                         schema: str | None = None,
                         table_name: str | None = None,
                         pull_all_cols: bool = True,
                         run_debugging: bool = False,
                         query: any = None
                         ):

        """
        build a dictionary containing keys that reference column:datatype conversion
        (w/ the purpose of optimizing memory after pulling data)

        :param username: str or None = None
        :param warehouse: str or None = None
        :param database: str or None = None
        :param role: str or None = None
        :param schema: str or None = None
        :param table_name: str or None = None
        :param pull_all_cols: bool = True
        :param run_debugging: bool = False
        :param query: str or None = None
        :return: Dictionary
        """

        if username is None:
            username = self.__username
        if warehouse is None:
            warehouse = self.__warehouse
        if role is None:
            role = self.__role
        if database is None:
            database = self.__database

        return SnowflakeData.optimize_tbl_mem(self, username=username, warehouse=warehouse, role=role,
                                              database=database, schema=schema, table_name=table_name,
                                              pull_all_cols=pull_all_cols, run_debugging=run_debugging, query=query)

    def snowflake_dependencies(self,
                               tables: str | list | None = None,
                               username: str | None = None,
                               warehouse: str | None = None,
                               role: str | None = None,
                               database: str | None = None,
                               schema: str | list | None = None,
                               save_path: str = None,
                               ):

        """

        :param recursive:
        :param filter_schemas:
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

        return SnowflakeData.snowflake_dependencies(self, tables=tables, username=username,
                                                    warehouse=warehouse, role=role, database=database,
                                                    schema=schema, save_path=save_path)

