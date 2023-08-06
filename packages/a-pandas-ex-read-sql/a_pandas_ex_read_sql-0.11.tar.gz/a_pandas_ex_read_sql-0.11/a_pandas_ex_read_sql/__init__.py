import ast
import sqlite3
import sqlparse
from a_pandas_ex_apply_ignore_exceptions import pd_add_apply_ignore_exceptions
from a_pandas_ex_less_memory_more_speed import pd_add_less_memory_more_speed
from pandas.core.frame import DataFrame
import pandas as pd
from check_if_nan import is_nan
pd_add_less_memory_more_speed()
pd_add_apply_ignore_exceptions()



def insert_sql_file_to_df(sql_file: str, encoding: str = "utf-8") -> pd.DataFrame:
    """
    Reads an SQL file (.sql) and converts all INSERT commands into a DataFrame.

    Args:
        sql_file (str): Path to the SQL file.
        encoding (str, optional): File encoding (default is "utf-8").

    Returns:
        pd.DataFrame: DataFrame containing the data from the SQL file.
    """
    with open(sql_file, "r", encoding=encoding) as file:
        sql_script = file.read()

    sta = []
    statements = sqlparse.split(sql_script)
    for statement in statements:
        sta.append(sqlparse.parse(statement))

    alfa = []
    for r in sta:
        dax = []
        for s in r:
            try:
                dax.append(pd.DataFrame(s).T)
            except Exception as fe:
                pass
        try:
            cona = pd.concat(dax)
        except Exception:
            continue
        alfa.append(cona)
    df2 = pd.concat(alfa)
    alldfs = []
    alldfs2 = []
    df = df2.copy()
    df = df.loc[df[0].apply(str).str.contains("INSERT")].reset_index(drop=True)
    for co in list(df.columns):
        try:
            df["aa_exten"] = df.ds_apply_ignore(
                pd.DataFrame(), lambda u: (pd.DataFrame(u.iloc[co])), axis=1
            )
            dfa = pd.concat(df.aa_exten.to_list(), ignore_index=True)
            dfa = dfa.loc[dfa[0].ds_apply_ignore(pd.NA, lambda u: u.ttype).isna()]
            dfa[0] = dfa[0].ds_apply_ignore(
                pd.DataFrame(),
                lambda c: [
                    e
                    for e in c.flatten()
                    if not repr(e).startswith("<Punctuation")
                    and not repr(e).startswith("<Whitespace")
                ],
            )
            alldfs2.append(dfa.copy())
            dffinal = pd.concat(
                dfa[0]
                .dropna()
                .ds_apply_ignore(pd.DataFrame(), lambda te: pd.DataFrame(te).T)
                .to_list()
            )
            alldfs.append(dffinal.copy())
        except Exception as fe:
            continue
    df = pd.concat(alldfs, ignore_index=True)
    for co in df.columns:
        df[co] = df[co].ds_apply_ignore(pd.NA, lambda q: ast.literal_eval(str(q)))
    df = df.ds_reduce_memory_size_carefully(verbose=False)
    return df


def sql_db_to_one_df(path: str) -> pd.DataFrame:
    r"""
    Reads an SQLite database file and converts all tables into a single DataFrame.

    Args:
        path (str): Path to the SQLite database file.

    Returns:
        pd.DataFrame: DataFrame containing the data from all tables in the database.
    """
    sqlconv = read_db_file(path)
    ala = [idf.copy().assign(aa_table=i) for i, idf in sqlconv.items()]
    aladf = pd.concat(ala).ds_reduce_memory_size_carefully(verbose=False)
    return aladf


def multidf_2_sql(dfdict: dict) -> pd.DataFrame:
    r"""
    Concatenates multiple DataFrames from a dictionary into a single DataFrame.

    Args:
        dfdict (dict): Dictionary containing the DataFrames to be concatenated.

    Returns:
        pd.DataFrame: Concatenated DataFrame.
    """
    return pd.concat(
        [idf.copy() for i, idf in dfdict.items()]
    ).ds_reduce_memory_size_carefully(verbose=False)


def read_db_file(path: str) -> dict:
    r"""
    Reads an SQLite database file and returns a dictionary of DataFrames, with each table represented as a DataFrame.

    Args:
        path (str): Path to the SQLite database file.

    Returns:
        dict: Dictionary where the keys are table names and the values are DataFrames containing the table data.
    """
    try:
        with sqlite3.connect(path) as sqlconn:
            tables = tuple(
                pd.read_sql_query(
                    "SELECT name FROM sqlite_master WHERE type='table';", sqlconn
                )["name"]
            )
            sqlconv = {
                t: pd.read_sql_query(f'SELECT * from "{t}"', sqlconn) for t in tables
            }
        return sqlconv
    except Exception as fe:
        print(fe)
        print(
            "Error! You might need to update the sqlite3.dll file!\nGo to: https://www.sqlite.org/download.html ,\ndownload the dll and put it in the DLLs folder of your env!"
        )


def split_in_group_dfs(df: pd.DataFrame, columns: list) -> dict:
    r"""
    Splits a DataFrame into multiple DataFrames based on specified columns.

    Args:
        df (pd.DataFrame): DataFrame to be split.
        columns (list): List of column names used for splitting.

    Returns:
        dict: Dictionary where the keys are group names and the values are the corresponding split DataFrames.
    """
    return {
        name if not is_nan(name) else "NaN": group.dropna(how="all", axis=1)
        for name, group in df.groupby(columns, dropna=False)
    }


def read_sqlite(path: str, encoding: str = "utf-8") ->dict|pd.DataFrame:
    r"""
    Reads either an SQLite database file or an SQL file and returns the corresponding data.

    Args:
        path (str): Path to the SQLite database file or SQL file.
        encoding (str, optional): File encoding (default is "utf-8").

    Returns:
        dict or pd.DataFrame: If the file is an SQLite database, returns a dictionary of DataFrames representing each table.
                              If the file is an SQL file, returns a DataFrame containing the data from the SQL file.
    """
    if path.lower().endswith(".db"):
        return read_db_file(path)
    elif path.lower().endswith(".sql"):
        return insert_sql_file_to_df(sql_file=path, encoding=encoding)
    else:
        try:
            return read_db_file(path)
        except Exception:
            return insert_sql_file_to_df(sql_file=path, encoding=encoding)


def pd_add_read_sql_file():
    pd.Q_read_sql = read_sqlite
    pd.Q_db_to_one_df = sql_db_to_one_df
    DataFrame.d_split_in_groups = split_in_group_dfs
    pd.Q_groupdict_to_one_df = multidf_2_sql
