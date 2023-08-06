#!/usr/bin/env python3
from functools import lru_cache
import pymysql
from pymysql import InternalError
import os
import pandas as pd

class OdinDB(object):

    @lru_cache
    def get_dashboard_data(self, tbl_name: str, limit: int = None) -> 'DataFrame':
        # period,area_name,product_name,process_name,value,units

        query: str = """
            SELECT 
                t.period, 
                t.area_name,
                t.product_name, 
                t.process_name, 
                t.value,
                t.units
    
            FROM %s t 
        """ % (tbl_name)

        if limit:
            query += f" LIMIT {limit}"

        try:
            conn: 'MySQL' = pymysql.connect(host=os.environ["MYSQL_HOST"],
                                            user=os.environ["MYSQL_USER"],
                                            password=os.environ["MYSQL_PASSWD"],
                                            database=os.environ["MYSQL_DB"])

            df: 'DataFrame' = pd.read_sql(query, con=conn)
            df['period'] = pd.to_datetime(df['period'])
            df['year'] = df['period'].apply(lambda row: row.year)
            df['quarter'] = df['period'].apply(lambda row: row.quarter)
            df['month'] = df['period'].apply(lambda row: row.month_name())

            conn.close()
            return df

        except InternalError as e:
            raise InternalError(
                "The server has encountered an internal error. Please check your query again!!!\n[QUERY]%s" % (
                    query)) from e

    @lru_cache
    def get_crude_oil_imports(self, **kwargs) -> 'DataFrame':

        try:
            query: str = f"""
                SELECT 
                    c.period,
                    c.originId,
                    c.originName,
                    c.originType, 
                    c.originTypeName, 
                    c.destinationId, 
                    c.destinationName, 
                    c.destinationType, 
                    c.destinationTypeName, 
                    c.gradeId, 
                    c.gradeName, 
                    c.quantity, 
                    c.quantity_units,
                    c.start_date, 
                    c.end_date

                FROM crude_oil_imports c 
                
                {kwargs.get('where', '')}
                {kwargs.get('order_by', '')}
                {kwargs.get('limit', '')}
            """.replace("'", "")

            conn: 'MySQL' = pymysql.connect(host=os.environ["MYSQL_HOST"],
                                            user=os.environ["MYSQL_USER"],
                                            password=os.environ["MYSQL_PASSWD"],
                                            database=os.environ["MYSQL_DB"])

            df: 'DataFrame' = pd.read_sql(query, con=conn)
            conn.close()
            return df

        except InternalError as e:
            raise InternalError(
                "The server has encountered an internal error. Please check your query again!!!\n[QUERY]%s" % (
                    query)) from e

    @lru_cache
    def get_petroleum_stocks(self, tbl_name) -> 'DataFrame':

        try:
            query: str = """SELECT 
                                p.period,
                                p.duoarea,
                                p.area_name,
                                p.product,
                                p.product_name,
                                p.process,
                                p.process_name,
                                p.series,
                                p.series_description,
                                p.value,
                                p.units
                        FROM %s 
            """ % (tbl_name)

            conn: 'MySQL' = pymysql.connect(host=os.environ["MYSQL_HOST"],
                                            user=os.environ["MYSQL_USER"],
                                            password=os.environ["MYSQL_PASSWD"],
                                            database=os.environ["MYSQL_DB"])

            df: 'DataFrame' = pd.read_sql(query, con=conn)
            conn.close()
            return df

        except InternalError as e:
            raise InternalError() from e

    @lru_cache
    def get_padd_petroleum_stocks(self, **kwargs) -> 'DataFrame':

        try:
            query: str = f"""
            WITH petroleum_stocks_reports AS 
            (SELECT
                STR_TO_DATE( CONCAT(p1.period, '-01' ) , '%Y-%m-%d' ) AS period,
                p1.area_name,
                p1.series_description,
                IFNULL( p1.value, 0) AS `value`,
                p1.process_name,
                p1.units
    
            FROM petoleum_natural_gas_plant_stocks p1
    
            UNION ALL 
    
            SELECT
                STR_TO_DATE( CONCAT(p2.period, '-01' ) , '%Y-%m-%d' ) AS period,
                p2.area_name,
                p2.series_description, 
                IFNULL( p2.value, 0) AS `value`,
                p2.process_name,
                p2.units
    
            FROM petroleum_motor_gasoline_stocks p2
    
            UNION ALL 
    
            SELECT 
                STR_TO_DATE( CONCAT(p.period, '-01' ) , '%Y-%m-%d' ) AS period,
                p.area_name,
                p.series_description,
                IFNULL( p.value, 0) AS `value`,
                p.process_name,
                p.units
    
            FROM petroleum_refinery_bulk_stocks p
    
            UNION ALL 
    
            SELECT 
                STR_TO_DATE( CONCAT(p.period, '-01' ) , '%Y-%m-%d' ) AS period,
                p.area_name,
                p.series_description,
                IFNULL( p.value, 0) AS `value`,
                p.process_name,
                p.units
    
            FROM petroleum_refinery_stocks p
    
            UNION ALL 
    
            SELECT 
                STR_TO_DATE( CONCAT(p.period, '-01' ) , '%Y-%m-%d' ) AS period,
                p.area_name,
                p.series_description,
                IFNULL( p.value, 0) AS `value`,
                p.process_name,
                p.units
    
            FROM petroleum_stocks_by_type_stocks p
    
            UNION ALL 
    
            SELECT 
                STR_TO_DATE( CONCAT(p.period, '-01' ) , '%Y-%m-%d' ) AS period,
                p.area_name,
                p.series_description,
                IFNULL( p.value, 0) AS `value`,
                p.process_name,
                p.units
    
            FROM petroleum_weekly_stocks p
    
            UNION ALL 
    
            SELECT 
                STR_TO_DATE( CONCAT(p.period, '-01' ) , '%Y-%m-%d' ) AS period,
                p.area_name,
                p.series_description,
                IFNULL( p.value, 0) AS `value`,
                p.process_name,
                p.units
    
            FROM crude_oil_stocks_at_tank_farms_and_pipelines p)
    
            SELECT 
                DISTINCT p.period, 
                IF(SUBSTR(p.area_name, 1,4) = 'PADD' AND LENGTH(p.area_name) = 7,  SUBSTR(p.area_name, 1, 6), p.area_name ) AS area_name, -- catogerize as parent - PADD 
                p.series_description, 
                p.process_name, 
                p.value, -- actual value 
                AVG( p.value) OVER(PARTITION BY YEAR(p.period), p.process_name, p.area_name ORDER BY p.period ASC, p.area_name ASC ) AS yearly_avg_value, 
                AVG( p.value) OVER(PARTITION BY MONTH(p.period), p.process_name, p.area_name ORDER BY p.period ASC, p.area_name ASC ) AS monthly_avg_value,
                p.units
    
    
            FROM petroleum_stocks_reports p 
            WHERE p.area_name  REGEXP 'PADD [1-5]' 
            {kwargs.get('clause', '')}
            """


            conn: 'MySQL' = pymysql.connect(host=os.environ["MYSQL_HOST"],
                                            user=os.environ["MYSQL_USER"],
                                            password=os.environ["MYSQL_PASSWD"],
                                            database=os.environ["MYSQL_DB"])

            df: 'DataFrame' = pd.read_sql(query, con=conn)
            conn.close()
            return df

        except InternalError as e:
            raise InternalError() from e