

from .Telemetry._Telemetry import Telemetry
from .InclusionExclusion._InclusionExclusion import InclusionExclusion


class Dashboards:

    Telemetry = Telemetry
    InclusionExclusion = InclusionExclusion

    def imp_summary_dashboard(self
                              , username: str
                              , warehouse: str
                              , database: str
                              , role: str
                              , date_min: str = '1900-01-01'
                              , date_max: str = '9999-12-31'
                              , column_filters=None
                              , polars: bool = False):

        """Create the data to match IMP Summary Dashboard.

        Args:
            username (str): The username for the Snowflake connection.
            warehouse (str): The warehouse for the Snowflake connection.
            database (str): The database for the Snowflake connection.
            role (str): The role for the Snowflake connection.
            date_min (str): The minimum date for the query (default is '1900-01-01').
            date_max (str): The maximum date for the query (default is '9999-12-31').
            column_filters (list): A list of column filters for the query.
            polars (bool): Whether to return the query results as a Polars DataFrame (default is False, which returns
                a Pandas DataFrame).

        Returns:
            A Pandas or Polars DataFrame containing the query results.

        Raises:
            TypeError: If column_filters is not a list.
        """

        from NikeCA import Snowflake

        if column_filters is None:
            column_filters = []
        import configparser

        config = configparser.ConfigParser()
        config.read('../pip.ini')


        date_begin = config['imp_summary'].get('begin_date')
        date_end = config['imp_summary'].get('date_end')
        date = config['imp_summary'].get('date')
        table = config['imp_summary'].get('table')
        column = config['imp_summary'].get('column')
        column_filter = config['imp_summary'].get('column_filter')
        column_flag = config['imp_summary'].get('column_flag')
        column_flag_answer = config['imp_summary'].get('column_flag_answer')
        aggs = config['imp_summary'].get('aggs')

        # Ensure column_filters is a list
        if not isinstance(column_filters, list):
            raise TypeError("column_filters must be a list")

        # Join column filters into comma-separated string, if any
        if len(column_filters) > 0:
            column_filters_str = ', '.join(column_filters)
            group_column_filters_str = f'''GROUP BY 
                {column_filters_str}'''
            column_filters_str += ', '
        else:
            column_filters_str = column + ', '
            group_column_filters_str = f'GROUP BY {column}'

        query_dashboard = f"""
        SELECT
            {column_filters_str}
            MIN({date_begin}) AS MIN_{date_begin}
            , MAX({date_end}) AS MAX_{date_end}
            , {aggs}
        FROM 
            {table}
        WHERE
            {date} BETWEEN '{date_min}' AND '{date_max}'
            AND {column} = '{column_filter}'
        {group_column_filters_str} 
        UNION
    
        SELECT
            {column_filters_str}
            MIN({date_begin}) AS MIN_{date_begin}
            , MAX({date_end}) AS MAX_{date_end}
            , {aggs}
        FROM 
            {table}
        WHERE
            {date} BETWEEN '{date_min}' AND '{date_max}'
            AND {column} <> '{column_filter}'
            AND {column_flag} = '{column_flag_answer}'
        {group_column_filters_str}
        ;
        """
        print(query_dashboard)

        return Snowflake(username=username, warehouse=warehouse, database=database,
                         role=role).snowflake_pull(query=query_dashboard, polars=polars)



