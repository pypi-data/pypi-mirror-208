
class InclusionExclusion:

    def pos_data_quality_review(self
                                , username: str
                                , warehouse: str
                                , database: str
                                , role: str
                                , columns: list | None = None
                                , filters: list | None = None
                                , order_by: list | None = None
                                , polars: bool = False
                                , start_date: str | None = None
                                , end_date: str | None = None):

        from NikeCA import Snowflake
        import polars as pl
        import datetime
        import configparser

        config = configparser.ConfigParser()
        config.read('pip.ini')

        table = config['inclusion_exclusion_pos_data_quality_review'].get('table')
        a = config['inclusion_exclusion_summary_and_home'].get('col_a')

        # Ensure columns is a list
        if not (isinstance(columns, list) or columns is None):
            raise TypeError("columns must be a list")

        # Ensure filters is a list
        if not (isinstance(filters, list) or filters is None):
            raise TypeError("filters must be a list")

        # Ensure order_by is a list
        if not (isinstance(order_by, list) or order_by is None):
            raise TypeError("order_by must be a list")

        if columns is None:
            columns_str = config['inclusion_exclusion_pos_data_quality_review'].get('columns')
        else:
            columns_str = ', '.join(columns)

        if filters is None:
            filters = []
        # Join column filters into comma-separated string, if any
        if len(filters) > 0:
            filters_str = 'AND '.join(filters)
            filters_str = f'WHERE {filters_str}'
        else:
            filters_str = ''

        if order_by is None:
            order_by = config['inclusion_exclusion_pos_data_quality_review'].get('order_by')
        else:
            order_by = ', '.join(order_by)

        query = f"""
            SELECT
                {columns_str}
                
            FROM
                {table}
            {filters_str}
                
            ORDER BY
                {order_by}
                
            ;
        """

        print(query)

        df = pl.DataFrame(Snowflake(username=username, warehouse=warehouse, database=database,
                                    role=role).snowflake_pull(query=query, polars=polars))

        if start_date is None and end_date is None:
            return df.filter(pl.col(a) == pl.col(a).max())
        elif end_date is None:
            return df.filter((pl.col(a) >= datetime.datetime.strptime(start_date, '%Y-%m-%d')))
        elif start_date is None:
            return df.filter((pl.col(a) <= datetime.datetime.strptime(end_date, '%Y-%m-%d')))
        else:
            df = df.filter((pl.col(a) >= datetime.datetime.strptime(start_date, '%Y-%m-%d')))
            return df.filter((pl.col(a) <= datetime.datetime.strptime(end_date, '%Y-%m-%d')))

    def summary(self
                , username: str
                , warehouse: str
                , database: str
                , role: str
                , columns=None
                , filters=None
                , order_by=None
                , polars: bool = True
                , start_date: str | None = None
                , end_date: str | None = None
                ):

        import polars as pl
        import pandas as pd
        import configparser

        config = configparser.ConfigParser()
        config.read('pip.ini')

        a = config['inclusion_exclusion_summary_and_home'].get('col_a')
        b = config['inclusion_exclusion_summary_and_home'].get('col_b')
        c = config['inclusion_exclusion_summary_and_home'].get('col_c')

        df = InclusionExclusion.pos_data_quality_review(self, username=username, warehouse=warehouse,
                                                        database=database, role=role, columns=columns, filters=filters,
                                                        order_by=order_by, polars=polars, start_date=start_date,
                                                        end_date=end_date)

        df_pd = pd.DataFrame()

        df_pd['RETAILERS'] = df.select(pl.col(b).count()).to_arrow()[0]

        df_pd['INCLUDED'] = df.select(df.filter(pl.col(c) == 'Y').select(pl.col(b).count())).to_arrow()[0]
        df_pd['PERCENT_INCLUDED'] = f"{str(round(df_pd['INCLUDED']/df_pd['RETAILERS']*100, 0))}%"
        df_pd['EXCLUDED'] = df.select(df.filter(pl.col(c) == 'N').select(pl.col(b).count())).to_arrow()[0]
        df_pd['PERCENT_EXCLUDED'] = f"{str(round(df_pd['EXCLUDED']/df_pd['RETAILERS'] * 100, 0))}%"

        if polars:
            return pl.DataFrame(df_pd)
        return df_pd

    def home_summary(self
                     , username: str
                     , warehouse: str
                     , database: str
                     , role: str
                     , columns=None
                     , filters=None
                     , order_by=None
                     , polars: bool = True
                     , start_date: str | None = None
                     , end_date: str | None = None
                     ):

        import datetime

        import polars as pl
        import configparser

        config = configparser.ConfigParser()
        config.read('pip.ini')

        a = config['inclusion_exclusion_summary_and_home'].get('col_a')
        b = config['inclusion_exclusion_summary_and_home'].get('col_b')
        c = config['inclusion_exclusion_summary_and_home'].get('col_c')
        d = config['inclusion_exclusion_summary_and_home'].get('col_d')
        e = config['inclusion_exclusion_summary_and_home'].get('col_e')
        f = config['inclusion_exclusion_summary_and_home'].get('col_f')
        g = config['inclusion_exclusion_summary_and_home'].get('col_g')
        h = config['inclusion_exclusion_summary_and_home'].get('col_h')

        df = InclusionExclusion.pos_data_quality_review(self, username=username, warehouse=warehouse, database=database,
                                                        role=role, columns=columns, filters=filters, order_by=order_by,
                                                        polars=polars, start_date=start_date, end_date=end_date)
        df_count = (
            df
            .with_columns([
                pl.col(c).count().over([
                    d
                    ]).alias('Total Retailers')
                , pl.col(c).filter(
                    pl.col(c) == 'Y'
                    ).count().over(d).alias('INCLUDED')
                , pl.col(c).filter(
                    pl.col(c) == 'N'
                    ).count().over(d).alias('EXCLUDED')
                , pl.col(e).filter(
                    pl.col(e) == 'Y'
                    ).count().over(d).alias('SALE AVLB')
                , pl.col(e).filter(
                    pl.col(e) == 'N'
                    ).count().over(d).alias('SALE UNAVLB')
                , pl.col(f).filter(
                    pl.col(f) == 'Y'
                    ).count().over(d).alias('SALE IN TREND')
                , pl.col(f).filter(
                    pl.col(f) == 'N'
                    ).count().over(d).alias('SALE NOT IN TREND')
                , pl.col(g).filter(
                    pl.col(g) == 'Y'
                    ).count().over(d).alias('INV IN TREND')
                , pl.col(g).filter(
                    pl.col(g) == 'N'
                    ).count().over(d).alias('INV NOT IN TREND')


            ])
        ).select([h, 'Total Retailers', 'INCLUDED', 'EXCLUDED', 'SALE AVLB', 'SALE UNAVLB',
                  'SALE IN TREND', 'SALE NOT IN TREND', 'INV IN TREND', 'INV NOT IN TREND']).unique()

        df_count = (df_count
                    .lazy()
                    .with_columns([
                        (pl.col('INCLUDED') / pl.col('Total Retailers') * 100).round(0).alias('% INCLUDED')
                        , (pl.col('EXCLUDED') / pl.col('Total Retailers') * 100).round(0).alias('% EXCLUDED')
                        , (pl.col('SALE AVLB') / pl.col('Total Retailers') * 100).round(0).alias('% Retailers Sales Available')
                        , (pl.col('SALE UNAVLB') / pl.col('Total Retailers') * 100).round(0).alias('% Retailers Sales Unavailable')
                        , (pl.col('SALE IN TREND') / pl.col('Total Retailers') * 100).round(0).alias('% SALE IN TREND')
                        , (pl.col('SALE NOT IN TREND') / pl.col('Total Retailers') * 100).round(0).alias('% SALE NOT IN TREND')
                        , (pl.col('INV IN TREND') / pl.col('Total Retailers') * 100).round(0).alias('% INV IN TREND')
                        , (pl.col('INV NOT IN TREND') / pl.col('Total Retailers') * 100).round(0).alias('% INV NOT IN TREND')

        ]).collect()
                    )

        return df_count




