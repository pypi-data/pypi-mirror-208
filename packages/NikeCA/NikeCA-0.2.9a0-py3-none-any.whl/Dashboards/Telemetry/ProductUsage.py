
from NikeCA import Snowflake
from Dashboards.Telemetry.Telemetry import Telemetry


class ProductUsage(Telemetry):

    def __init__(self, username, warehouse, role, database):
        super().__init__(username=username, warehouse=warehouse, role=role, database=database)

        self.username = username
        self.warehouse = warehouse
        self.role = role
        self.database = database

    @staticmethod
    def get_base_query(filters: list | None = None
                       , start_date: str = '1900-01-01'
                       , end_date: str = '9999-12-31'
                       ):

        import configparser

        config = configparser.ConfigParser()
        config.read('pip.ini')

        table = config['telemetry_product_usage'].get('table')
        a = config['telemetry_product_usage'].get('col_a')
        b = config['telemetry_product_usage'].get('col_b')
        c = config['telemetry_product_usage'].get('col_c')
        d = config['telemetry_product_usage'].get('col_d')
        e = config['telemetry_product_usage'].get('col_e')
        f = config['telemetry_product_usage'].get('col_f')
        g = config['telemetry_product_usage'].get('col_g')
        date_column = config['telemetry_product_usage'].get('date_column')
        filter_a = config['telemetry_product_usage'].get('filter_a')
        filter_b = config['telemetry_product_usage'].get('filter_b')
        filter_c = config['telemetry_product_usage'].get('filter_c')

        # Ensure filters is a list
        if not (isinstance(filters, list) or filters is None):
            raise TypeError("filters must be a list")

        if filters is None:
            filters = []
            filters_str = f'WHERE {date_column} BETWEEN {start_date} AND {end_date}'

        # Join column filters into comma-separated string, if any
        if len(filters) > 0:
            filters_str = 'AND '.join(filters)
            filters_str = f"WHERE {date_column} BETWEEN '{start_date}' AND '{end_date}' AND {filters_str}"
        else:
            filters_str = f"WHERE {date_column} BETWEEN '{start_date}' AND '{end_date}'"

        base_query = f"""
            SELECT
                DISTINCT 
                {a}
                , {b}
                , CASE 
                    WHEN {b} = '{filter_a}' THEN {c}
                    WHEN {b} = '{filter_b}' THEN {d}
                    WHEN {b} = '{filter_c}' THEN {e}
                    else null 
                END AS PRODUCT_NAME
                , COUNT(DISTINCT {f})
                , (SUM({g})/NULLIF(COUNT(DISTINCT {f}),0 )) AS DAILY_USAGE
            FROM 
                {table}
            
            {filters_str}
            
            GROUP BY
                {a}
                , {b}
                , PRODUCT_NAME
    """
        return base_query

    def product_viewed(self
                       , username: str | None = None
                       , warehouse: str | None = None
                       , database: str | None = None
                       , role: str | None = None
                       , filters: list | None = None
                       , order_by: list | None = None
                       , polars: bool = False
                       , start_date: str = '1900-01-01'
                       , end_date: str = '9999-12-31'
                       ):

        if username is None:
            username = self.username
        if warehouse is None:
            warehouse = self.warehouse
        if database is None:
            database = self.database
        if role is None:
            role = self.role

        # from NikeCA import Snowflake
        import polars as pl
        import configparser

        config = configparser.ConfigParser()
        config.read('pip.ini')

        b = config['telemetry_product_usage'].get('col_b')

        # Ensure filters is a list
        if not (isinstance(filters, list) or filters is None):
            raise TypeError("filters must be a list")

        # Ensure order_by is a list
        if not (isinstance(order_by, list) or order_by is None):
            raise TypeError("order_by must be a list")

        if order_by is None:
            order_by = config['telemetry_product_usage'].get('order_by')
        else:
            order_by = ', '.join(order_by)

        query = f"""
            /*
            The query calculates the daily usage of different data products on different platforms, groups the data by platform and product, and sorts the result in descending order based on the total usage
            */
            SELECT 
                {b}
                , PRODUCT_NAME
                , SUM(DAILY_USAGE) AS TOTAL_USAGE
            FROM (

            {self.get_base_query(start_date=start_date, end_date=end_date)}
            
            )
            
            GROUP BY 
                {b}
                , PRODUCT_NAME
                
            HAVING 
                TOTAL_USAGE > 0
                
            ORDER BY
                {order_by}
                
            ;
        """

        df = pl.DataFrame(Snowflake(username=username, warehouse=warehouse, database=database,
                                    role=role).snowflake_pull(query=query, polars=polars))

        print(query)

        if polars:
            return df
        else:
            return df.to_pandas()

    def summary(self
                , username: str | None = None
                , warehouse: str | None = None
                , database: str | None = None
                , role: str | None = None
                , filters: list | None = None
                , order_by: list | None = None
                , polars: bool = False
                , start_date: str = '1900-01-01'
                , end_date: str = '9999-12-31'
                ):

        if username is None:
            username = self.username
        if warehouse is None:
            warehouse = self.warehouse
        if database is None:
            database = self.database
        if role is None:
            role = self.role

        import configparser

        config = configparser.ConfigParser()
        config.read('pip.ini')
        b = config['telemetry_product_usage'].get('col_b')

        if order_by is None:
            order_by = config['telemetry_product_usage'].get('order_by')
        else:
            order_by = ', '.join(order_by)

        query = f"""
    SELECT 
        DISTINCT
        {b}
        , SUM(DAILY_USAGE) OVER (PARTITION BY {b}) AS TOTAL_USAGE
    FROM (
        {self.get_base_query(start_date=start_date, end_date=end_date, filters=filters)}   
    )
    ORDER BY
        {order_by}
"""

        from NikeCA import Snowflake
        import polars as pl

        df = pl.DataFrame(Snowflake(username=username, warehouse=warehouse, database=database,
                                    role=role).snowflake_pull(query=query, polars=polars))

        print(query)

        return df


