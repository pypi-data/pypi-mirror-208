

# Nike CA

This package was developed informally for the Commercial Analytics Team at Nike

Before trying to use this package ensure that you have the proper access (This can be found under the "Usage" Section below)

This is a start to see about developing package to facilitate, standardize, and automate repetitive tasks


# Installation and Setup
<details><summary>See Information about Installation, Setup, and Running</summary>

<details><summary> Dependencies that will automatically be installed if not already satisfied:</summary>

* "wheel",
* "asn1crypto==1.5.1",
* "certifi==2022.12.7",
* "cffi==1.15.1",
* "charset-normalizer==2.1.1",
* "cryptography==39.0.1",
* "databricks==0.2",
* "databricks-sql==1.0.0",
* "databricks-sql-connector==2.2.1",
* "filelock==3.9.0",
* "gitdb==4.0.10",
* "GitPython==3.1.31",
* "greenlet==2.0.2",
* "idna==3.4",
* "jupyter-contrib-core==0.4.2",
* "jupyter-contrib-nbextensions==0.7.0",
* "jupyter-events==0.6.3",
* "jupyter-highlight-selected-word==0.2.0",
* "jupyter-nbextensions-configurator==0.6.1",
* "jupyter-ydoc==0.2.2",
* "jupyter_client==8.0.3",
* "jupyter_core==5.2.0",
* "jupyter_server==2.3.0",
* "jupyter_server_fileid==0.8.0",
* "jupyter_server_terminals==0.4.4",
* "jupyter_server_ydoc==0.6.1",
* "jupyterlab==3.6.1",
* "jupyterlab-pygments==0.2.2",
* "jupyterlab_server==2.19.0",
* "lz4==4.3.2",
* "numpy==1.23.4",
* "oauthlib==3.2.2",
* "oscrypto==1.3.0",
* "pandas==1.5.3",
* "pyarrow==10.0.1",
* "pycparser==2.21",
* "pycryptodomex==3.17",
* "PyJWT==2.6.0",
* "pyOpenSSL==23.0.0",
* "pystache==0.6.0",
* "python-dateutil==2.8.2",
* "pytz==2022.7.1",
* "requests==2.28.2",
* "six==1.16.0",
* "smmap==5.0.0",
* "snowflake-connector-python==3.0.0",
* "snowflake-sqlalchemy==1.4.6",
* "SQLAlchemy==1.4.46",
* "thrift==0.16.0",
* "typing_extensions==4.5.0",
* "urllib3==1.26.14",
* "xcrun==0.4",
* "configparser~=5.3.0"

</details>

## Installing and Setting up a New Environment (if you are new to python start here):

<details><summary>Installation and Setup with a New Environment</summary>

<details><summary>For Mac</summary>

### Note: This assumes that you already have Python 3.11.2 installed

<details><summary> How do I tell which version of Python I have?</summary>

1. Launch the Terminal by typing "Terminal" in the Launchpad search field or Spotlight

2. Enter the following command in the Terminal

```
python3 --version
```
and you should see this:
> Python 3.11.2

</details>

<details> <summary> To Install Python 3.11.2</summary>

1. Go to https://www.python.org/downloads/

2. Click on "Download Python 3.11.2"

3. Open the file and click through the installation steps accepting the defaults

</details>

<details><summary> When running for the first time, open the Terminal and run the following commands where you want the files to be kept:</summary>

```unix
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install NikeCA
```
* After running the command above, restart the terminal and proceed to the "To open Jupyter Notebook after installation (Mac)"

</details></details>

</details>


## Installing without Setting up a New Environment:

<details><summary> pip Install Without Setting up a New Environment</summary>

Run the following to install:

```
$ python pip install NikeCA
```
</details>

## To open Jupyter Notebook after installation (Mac)

<details><summary> Navigate to the installation location in the terminal and run the following:</summary>

```unix
source venv/bin/activate
jupyter notebook
```
</details></details>



# Modules
### NikeCA

A Module for interacting with the Databases and doing Analytics

<details><summary>Import</summary>

Run the following to import:

```
import NikeCA
```
</details>


## Classes:
<details><summary>Snowflake Class</summary>


## Snowflake:
Snowflake(username: str, warehouse: str, role: str, database: str = None, schema: str = None, table: str = None, column_name: str = None, col_and_or: str = 'AND', get_ex_val: bool = None, like_flag: bool = False, sample_table: bool = False, sample_val: bool = False, table_sample: dict = None, dtypes_conv = None)

<details><summary> Import:</summary>

    from NikeCA import Snowflake

</details>

<details><summary>Parameters:</summary>

* username (str): The Snowflake account username


* warehouse (str): The Snowflake warehouse to use


* role (str): The Snowflake role to use


* database (str, optional, default=None): The Snowflake database to use


* schema (str, optional, default=None): The Snowflake schema to use


* table (str, optional, default=None): The Snowflake table to use


* column_name (str, optional, default=None): The name of the column to search


* col_and_or (str, optional, default=None): The AND/OR operator to use between search criteria


* get_ex_val (bool, optional, default=None): Whether to return exact matches only


* like_flag (bool, optional, default=None): Whether to use the LIKE operator for search criteria

</details>

## Methods:

<details>
<summary> snowflake_pull() - pulls snowflake data
</summary>

### snowflake_pull(
self, query: str, username: str | None = None, warehouse: str | None = None, database: str | None = None, role: str | None = None, sample_table: bool = False, sample_val: bool = False, table_sample: dict | None = None, dtypes_conv: Any = None

) -> DataFrame:

<details><summary>Dependencies:</summary>

* pandas
* snowflake.connector

</details>

<details><summary> Parameters:</summary>

* query (str): SQL query to run on Snowflake 
  * e.g. ```SELECT * FROM {}```


* username (str or None, default=None): Nike Snowflake Username 


* database (str or None, default=None): Name of the Database 


* warehouse (str or None, default=None): Name of the Warehouse 


* role (str or None, default=None): Name of the role under which you are running Snowflake 


* sample_table (bool, optional, Default=False): pull only 500 records from table


* sample_val (bool, optional, default=False)


* table_sample (dictionary, optional, default=None) 


* dtypes_conv (any, default=None)

</details>

#### return: pandas.DataFrame

Run the following in python to generate a sample query:


```
from NikeCA import Snowflake

username = <Your Username>
warehouse = <The Name of the Warehouse>
role = <Name of Your Role>
database = <Name of the Database>

sf =  Snowflake(username=username, warehouse=warehouse, role=role, database=database)

query = 'SELECT TOP 2 * FROM  {}'

print(sf.snowflake_pull(query)) 
```

</details>

<details><summary>build_search_query() - Builds and returns a search query based on the specified parameters and instance variables
</summary>

### build_search_query(
self, inp_db: str | None = None, schema: str | None = None, table: str | None = None, column_name=None, like_flag: bool = False, col_and_or: str = 'AND'

) -> str

#### Dependencies - None

<details><summary> Parameters:</summary>

* inp_db (str or None, optional, default=None): The database name to search in. If not specified, search all databases
  

* schema (str or None, optional, default=None): The schema name to search in. If not specified, search all schemas


* table (str or None, optional, default=None): The table name to search for. If not specified, search all tables


* column_name(any, optional, default=None): The column name(s) to search for. If not specified, search all columns
  * If a list is provided, search for any columns that match any of the names in the list


* like_flag (bool, optional, default=False) 
  * If True, uses a SQL LIKE statement to search for columns that contain the specified column name(s)
    ```
    f"AND column_name like '{column_name}' " if like_flag else where_stmt + f"AND column_name = '{column_name}' "
    ```
  * If False, searches for exact matches to the specified column name(s)
    ```
    f"AND column_name like '{column_name}' " if like_flag else where_stmt + f"AND column_name = '{column_name}' "
    ```
    

* col_and_or (str: optional, default='AND'): If specified and column_name is a list, determines whether to search for columns that match all or any of 
the names in the list. Must be one of the following values: 'AND', 'and', 'OR', 'or'.

</details>

#### return: string of the SQL Statement

#### Run the following in python to generate a sample query
```
from NikeCA import Snowflake

username = <Your Username>
warehouse = <The Name of the Warehouse>
role = <Name of Your Role>
database = <Name of the Database>

sf = Snowflake(username=username, warehouse=warehouse, role=role, database=database)

print(sf.build_search_query(column_name='%***%', like_flag=True))
```

</details>


<details><summary>search_schema() - Search snowflake structure for specific schemas/tables/columns </summary>

### search_schema(
self, username=None, warehouse=None, database=None, role=None, sample_table: bool = False, sample_val: bool = False, table_sample: dict = None, dtypes_conv=None, schema=None, table=None, column_name=None, col_and_or='and', get_ex_val=False, like_flag=False

)

Notes: Will allow to search for tables/cols/etc. even without knowing the db if database=None

<details><summary>Dependencies</summary>

* pandas
* snowflake.connector

</details>
 
<details><summary>Parameters</summary>

* username (str or None, default=None): Nike Snowflake Username 


* database (str or None, default=None): Name of the Database 


* warehouse (str or None, default=None): Name of the Warehouse 


* role (str or None, default=None): Name of the role under which you are running Snowflake 


* sample_table (bool, optional, Default=False): pull only 500 records from table


* sample_val (bool, optional, default=False)


* table_sample (dictionary, optional, default=None) 
  * Notes: The below code is built within the Module

        if table_sample is not None: 
             table_sample = {'db': None, 'schema': None, 'table': None, 'col': None}

* dtypes_conv (any, default=None)


* schema (str, default=None): Snowflake schema name from any database 


* table (str, default=None): Snowflake table name


* column_name (str, default=None): column name to filter


* col_and_or (str, default='and'): either 'and' or 'or'
  * will use in the where statement


* get_ex_val (bool, default=False)


* like_flag (bool, default=False): This signifies whether the "column_name like " or "column_name = "

</details>

#### return: pandas.Dataframe

Run the following in python to generate a sample table:

    from NikeCA import Snowflake
    
    sf = Snowflake(username=<your username>, warehouse=<your warehouse>, 
         role=<your role>, database=<database you would like to search or none>)
    
    sf.column_name = '*****'
    sf.schema = '*****'
    sf.like_flag = True
    
    print(sf.search_schema())

</details>

<details><summary>snowflake_dependencies() - Searches the snowflake database and finds instances where the table is referenced and where the reference is not in the actual creation of the table itself
</summary>


### snowflake_dependencies(

self, tables: str | list, username: str, warehouse: str, role: str, database: str | None = None, schema: str | list | None = None

) -> pandas.DataFrame:

Note: If the table's get_ddl() is empty, it will throw an error - I will fix this soon
 

<details><summary>Dependencies</summary>

* pandas
* snowflake.connector

</details>

<details><summary>Parameters</summary>

* tables (list | str, required): This is a list or string to check for in the database could be a table name or anything contained within the get_ddl() string


* username (str, default=self): Username for Snowflake


* warehouse (str, default=self): Name of the Snowflake warehouse


* role (str, default=self): Role for Snowflake


* database (str, required, default=self): database to search in


* schema (str | list | None, optional, default=self): Snowflake schema to search in
  * notes: filling this in can really speed up the query

</details>

#### return: pandas.Dataframe

Run the following in python to generate a sample table:

    import pandas as pd
    
    username = 
    warehouse =
    role = 
    database = 
    
    sf = Snowflake(username=username, warehouse=warehouse, role=role, database=database)
    
    tables = ['***', '***']
     
    schema = '***'

    df = sf.snowflake_dependencies(tables='***', schema=schema)
    
    print(df)

</details>


[//]: # (## optimize_tbl_mem&#40;&#41;:)

[//]: # (build a dictionary containing keys that reference column:datatype conversion with the purpose of optimizing memory )

[//]: # (after pulling data)

[//]: # ()
[//]: # (#### Dependencies)

[//]: # (* time)

[//]: # (* pandas)

[//]: # (* itertools)

[//]: # ()
[//]: # (#### Parameters:)

[//]: # ()
[//]: # (* username &#40;str or None, default=None&#41;: Nike Snowflake Username )

[//]: # (  * e.g. "USERNAME")

[//]: # ()
[//]: # ()
[//]: # (* database &#40;str or None, default=None&#41;: Name of the Database )

[//]: # (  * e.g. "NGP_DA_PROD")

[//]: # ()
[//]: # ()
[//]: # (* warehouse &#40;str or None, default=None&#41;: Name of the Warehouse )

[//]: # (  * e.g. "DA_DSM_SCANALYTICS_REPORTING_PROD")

[//]: # ()
[//]: # ()
[//]: # (* role &#40;str or None, default=None&#41;: Name of the role under which you are running Snowflake )

[//]: # (  * e.g. "DF_*****")

[//]: # ()
[//]: # ()
[//]: # (* schema &#40;str or None, default=None&#41;: Name of the schema that is being optimized)

[//]: # (  * e.g. "POS")

[//]: # ()
[//]: # ()
[//]: # (* table_name &#40;str or None, default=None&#41;: Name of the table to be optimized)

[//]: # (  * e.g. "TO_DATE_AGG_CHANNEL_CY")

[//]: # ()
[//]: # ()
[//]: # (* pull_all_cols &#40;bool, optional, default=True&#41;:)

[//]: # ()
[//]: # ()
[//]: # (* run_debugging &#40;bool, optional, default=False&#41;:)

[//]: # ()
[//]: # (                         )
[//]: # (* query &#40;any, default=None&#41;: query for the pull for the analyzation of the datatypes)

[//]: # ()
[//]: # (#### return )

[//]: # (* dictionary)

</details>

#



#

<details><summary>QA Class</summary>

## QA:

### Import

Run the following to import:

```
from NikeCA import QA
```

<details><summary>Parameters</summary>

* df (DataFrame)


* df2 (DataFrame, optional, default=None)


* ds1_nm (str, optional, default='Source #1')


* ds2_nm (str, optional, default='Source #2')


* case_sens (bool, optional, default=True)


* print_analysis (bool, optional, default=True)


* check_match_by (any, optional, default=None)


* breakdown_grain (any, optional, default=None)

</details>

## Methods

<details><summary>column_gap_analysis() - Compares 2 DataFrames and gives shape, size, matching columns, non-matching columns, coverages, and percentages
</summary>

## column_gap_analysis(
self, df2: pd.DataFrame = None, ds1_nm: str = 'Source #1', ds2_nm: str = 'Source #2', case_sens: bool = True, print_analysis: bool = True, check_match_by=None, breakdown_grain=None, df=None

)

<details><summary>Dependecnies
</summary>

* "pandas==1.5.3",

</details>

<details><summary>Parameters</summary>

* df (DataFrame)


* df2 (DataFrame, optional, default=None)


* ds1_nm (str, optional, default='Source #1')


* ds2_nm (str, optional, default='Source #2')


* case_sens (bool, optional, default=True)


* print_analysis (bool, optional, default=True)


* check_match_by (any, optional, default=None)


* breakdown_grain (any, optional, default=None)

</details>

#### return: pandas.DataFrame

#### Run the following in python to generate a sample query
```
from NikeCA import QA, Snowflake

username = <Your Username>
warehouse = <The Name of the Warehouse>
role = <Name of Your Role>
database = <Name of the Database>

sf = Snowflake(username=username, warehouse=warehouse, role=role, database=database)

df = sf.snowflake_pull(sf.build_search_query(column_name='%***%', like_flag=True))[['TABLE_CATALOG', 'TABLE_SCHEMA', 'COLUMN_NAME']]

df2 = sf.snowflake_pull(sf.build_search_query(column_name='%***%', schema='***', like_flag=True))

qa = QA(df=df, df2=df2)
print(qa.column_gap_analysis())
```

</details>

<details><summary>data_prfl_analysis() - Takes a pandas.DataFrame as an input and returns a pandas.DataFrame with certain inormation about the dataframes, such 
as a list of columns and data types, nulls, coverage percentage, unique values, etc.
</summary>

## data_prfl_analysis(
self, df: pd.DataFrame = None, ds_name: str = 'Data Source', sample_vals: int = 5, print_analysis: bool = True, show_pct_fmt: bool = True

)

### Still Under Development

<details><summary>Dependencies</summary>

* "pandas==1.5.3",

</details>

<details><summary>Parameters</summary>

* df (DataFrame): pandas.DataFrame to be analyzed


* ds_name (str, optional, default='Data Source'): name of the data source to be included in the output


* sample_vals (int, optional, default=5)


* print_analysis (bool, optional, default=True)


* show_pct_fmt (bool, optional, default=True): show_percentage_format

</details>

#### return: 
<details><summary>pandas.Dataframe with the following columns: </summary>

* 'DATA_SOURCE'
* 'COLUMN'
* 'COL_DATA_TYPE'
* 'TOTAL_ROWS'
* 'ROW_DTYPE_CT'
* 'PRIMARY_DTYPE_PCT'
* 'COVERAGE_PCT', 'NULL_PCT'
* 'DTYPE_ERROR_FLAG'
* 'NON_NULL_ROWS'
* 'NULL_VALUES'
* 'UNIQUE_VALUES'
* 'COL_VALUE_SAMPLE'
* 'NULL_VALUE_SAMPLE'

</details>

```
    from NikeCA import Snowflake, QA
    
    sf = Snowflake(username=<username>, warehouse=<warehouse>, role=<role>, database=<database>)
    
    df = sf.snowflake_pull("""SELECT TOP 200 * FROM ***""")
    
    print(QA(df).data_prfl_analysis())
```

</details>

</details>

<br>

<br>
<br>
<br>
<br>
