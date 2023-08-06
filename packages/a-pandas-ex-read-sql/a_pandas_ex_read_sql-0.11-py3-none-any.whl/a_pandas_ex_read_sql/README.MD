# Convert any SQL Database to a Pandas DataFrame


```python
$ pip install a-pandas-ex-read-sql
from a_pandas_ex_read_sql import pd_add_read_sql_file
pd_add_read_sql_file()
import pandas as pd
dict_with_dfs = pd.Q_read_sql(r"F:\msgstorexxxxxxxxxxxxxxxxx.db")
```






### Update 13.5: 

```python
# Added .SQL File Reading Functionality
# To read an .SQL file and obtain the data, you can use the pd.Q_read_sql() function.
# This code reads the specified SQL file (.sql - only INSERT commands) and returns a DataFrame containing the data from the file.
df = pd.Q_read_sql(r"C:\Users\hansc\Downloads\sax\world.sql")

# Reading an SQLite Database File (.db)
# To read an SQLite database file and retrieve the data, you can also use the pd.Q_read_sql() function.
# This code reads the specified SQLite database file (northwind.db) and returns a DataFrame containing the data in a dict of DataFrames.

df2 = pd.Q_read_sql(r"C:\Users\hansc\Downloads\northwind.db")


# To convert all tables in an SQLite database file into a single DataFrame, you can use the pd.Q_db_to_one_df() # function. This code reads the specified SQLite database file (northwind.db), retrieves all the tables, and combines them into a single DataFrame.
df3 = pd.Q_db_to_one_df(path=r"C:\Users\hansc\Downloads\northwind.db")



# Splitting a DataFrame into Grouped DataFrames (Revert the last step)
# To split a DataFrame into multiple DataFrames based on specified columns, you can use the d_split_in_groups() # function. This code splits the DataFrame (df3) into multiple DataFrames based on the "aa_table" column. The result is a dictionary where the keys are group names, and the values are the corresponding split DataFrames.

df4 = df3.d_split_in_groups(columns=["aa_table"])

# To revert the grouped DataFrames back into a single DataFrame (without reading SQL), you can use the pd.Q_groupdict_to_one_df() function. 
# This code takes the dictionary of grouped DataFrames (df4) and combines them into a single DataFrame.
df5 = pd.Q_groupdict_to_one_df(df4)

```
