
"""
South Africa Macroeconomic Database API

A python API providing access to a relational database with public macroeconomic data for South Africa, obtained from
from the South African Reserve Bank (SARB) and Statistics South Africa (STATSSA), and updated on a regular basis via the
EconData (https://www.econdata.co.za/) platform and automated scraping of the SARB and STATSSA websites.
The database is maintained at the Department of Economics at Stellenbosch University. The package is built around the
Polars DataFrame library. Its contents are summarized as follows:

Datasets providing information about the available data

datasources()   - Data sources
datasets()      - Datasets
series()        - Series (can be queried by dataset)

Retrieve the data from the database

data()          - By default retrieves all data

Functions to reshape data and add temporal identifiers

pivot_wider()   - Wrapper around Polars .melt()
pivot_longer()  - Wrapper around Polars .pivot()
expand_date()   - Create year, quarter, month and day columns from a date

Helper functions to convert inputs to date strings

as_date()       - E.g. "2011M01" -> "2011-01-01"

Lists with identifiers

SAMADB_ID       - Cross-sectional identifiers
SAMADB_T        - Temporal identifiers

"""


import polars as _pl
from datetime import datetime as _datetime, timedelta as _timedelta

SAMADB_ID = ["dsid", "series"]

SAMADB_T = ["date", "year", "quarter", "month", "day"]

__uri__ = "mysql://SAMADB_READ:0c7Wg975vj@102.214.9.99:3306/SAMADB"



def datasources(ordered = True):
    """Retrieve Data Sources Table.
    
        This function pulls and returns a table called 'DATASOURCE' from the database. The 'DATASOURCE' table gives 
        information about the sources of data in this database, including the source website, and the number of 
        datasets available from the source.

        Parameters:
            ordered: boolean. 'True' orders the result in the order data was entered into the database, while 'False' returns the result in a random order, to the benefit of faster query execution.

        Returns:
            A Polars DataFrame providing information about the sources of data in the database.
    """
    query = "SELECT * FROM DATASOURCE"
    if ordered:
        query += " ORDER BY src_order"
    res = _pl.read_sql(query, __uri__)
    if len(res) == 0:
        raise Exception("Query resulted in empty dataset. This means something is wrong with your internet connection, the connection to the database or with the database itself.")
    return res.drop("src_order")
  
  
def datasets(ordered = True):
    """Retrieve Datasets Table.
    
        This function pulls and return a table called 'DATASET' from the database. The 'DATASET' table gives information about 
        the different datasets fetched from different providers at regular intervals. It provides a unique id for each dataset, 
        the frequency of data, the number of records (datapoints) in each dataset, the minimum and maximum time coverage, when 
        the dataset was last updated, and information about the data source, provider, and method of data access.

        Parameters:
            ordered: boolean. 'True' orders the result in the order data was entered into the database, while 'False' returns the result in a random order, to the benefit of faster query execution.

        Returns:
            A Polars DataFrame providing information about the available datasets in the database.
    """
    query = "SELECT * FROM DATASET"
    if ordered:
        query += " ORDER BY ds_order"
    res = _pl.read_sql(query, __uri__)
    if len(res) == 0:
        raise Exception("Query resulted in empty dataset. This means something is wrong with your internet connection, the connection to the database or with the database itself.")
    return res.drop("ds_order")


def series(dsid = None,
           series = None,
           dataset_info = False,
           ordered = True,
           return_query = False):
  """Retrieve Series Table.
  
     This function pulls the 'SERIES' table from the database, providing information about the time series in the database.
     Each series is given a code which unique across datasets.

        Parameters:
            dsid: (optional) list of id's of datasets matching the 'dsid' column of the 'DATASET' table ('sm.datasets()') for which series information is to be returned.
            series: string. (optional) list of series codes for which information in to be returned. If 'dsid' is also specificed, the two are combined using SQL 'OR' i.e. these series are retrieved in addition to all series matched through 'dsid'.
            dataset_info: boolean. 'True' returns additional information from the 'DATASET' table (the dataset name, when data was last updated, the source id and the data provider and access mode).
            ordered: boolean. 'True' returns the series in a fixed order, while 'False' returns the result in a random order, to the benefit of faster query execution.
            return_query: boolean. 'True' will not query the database but instead return the constructed SQL query as a string (for debugging purposes).

        Returns:
            A Polars DataFrame providing the codes and labels of all series in the database.

        Examples:
            import samadb as sm

            # By default returns all series

            sm.series()

            # Adding information about the dataset and provider

            sm.series(dataset_info = True)

            # Only series in the QB

            sm.series("QB")
  """
  if dataset_info:
      query = "SELECT * FROM SERIES NATURAL JOIN (SELECT dsid, dataset, updated, srcid, src_dsid, provider, access FROM DATASET) AS DS" 
  else:
      query = "SELECT * FROM SERIES"

  if dsid is not None:
      if type(dsid) is str:
          dsid = [dsid]
      if len(dsid) == 1:
          query += " WHERE dsid = '" + "".join(dsid) + "'"
      else:
          query += " WHERE dsid IN ('" + "', '".join(dsid) + "')"
          
  if series is not None:
      add = " WHERE " if dsid is None else " OR "
      if type(series) is str:
          series = [series]
      if len(series) == 1:
          query += add + "series = '" + "".join(series) + "'"
      else:
          query += add + "series IN ('" + "', '".join(series) + "')"
          
  if ordered:
      query += " ORDER BY s_order"

  if return_query:
      return query
    
  res = _pl.read_sql(query, __uri__)
  if len(res) == 0:
      raise Exception("Query resulted in empty dataset. This means something is wrong with your internet connection, the connection to the database or with the database itself.")
  return res.drop("s_order")


# dt.strftime(dt.strptime("2011-01-01", "%Y-%m-%d"), "%Y-%m-%d")
#
# x = dt.strptime("2011-01-01", "%Y-%m-%d")
# type()
#
# x = "2018-03"
#
#
# from datetime import datetime, date, timedelta
#
# my_str = '09-24-2023'  # (mm-dd-yyyy)
# date_1 = datetime.strptime(my_str, '%m-%d-%Y')
#
# print(date_1)  # 2023-09-24 00:00:00
#
# result_1 = date_1 + timedelta(days=3)
# print(result_1)
#
# x[5:7]
# strptime("2011-01-01", pl.Date, "%Y-%m-%d")

is_date = lambda x: (type(x) is _datetime.date or
          str(type(x)) in ["<class 'datetime.date'>", "<class 'datetime.datetime'>"] or
          (str(type(x)) == "<class 'polars.internals.series.series.Series'>" and
           x.dtype is _pl.datatypes.Date))

        


def as_date(x, end = False):
  """Coerce Input to Date-String.

        Parameters:
            x: a datetime.date or date-string "YYYY-MM-DD" or "YYYY-MM", year-quarter "YYYYQN" or "YYYY-QN", year-month "YYYYMNN" or "YYYY-MNN" or calendar year YYYY (integer or string).
            end: boolean. 'True' replaces missing time information with a period end-date which is the last day of the period. 'False' replaces missing month and day information with "-01".

        Returns:
            A complete "YYYY-MM-DD" date-string.

        Examples:
            import samadb as sm

            sm.as_date("2011-05")

            sm.as_date(2011)

            sm.as_date("2011Q1")

            sm.as_date("2011Q1", end = True)

            sm.as_date("2011M2")

            sm.as_date("2011M2", end = True)

  """
  if is_date(x):
      return _datetime.strftime(x, "%Y-%m-%d")

  if type(x) is int and (x > 1800 or x < 2100):
      x = str(x)

  if type(x) is not str:
      raise Exception("x needs to be an object of class datetime.datetime or a (partial) date string.")

  ncx = len(x)
  if ncx == 4:
      return x + ("-12-31" if end else "-01-01")

  if ncx >= 6 and ncx <= 8: 
      # if x[4] == "/":
      #     return str(int(x[:4]) + 1) + "-06-30" if end else x[:4] + "-07-01"
      if x[4] == "Q" or x[5] == "Q":
          Q = int(x[ncx-1])
          if end:
              return x[:4] + ("-0" + str(Q * 3) if Q < 4 else "-" + str(Q * 3)) + ("-31" if Q % 2 else "-30")
          else:
              return x[:4] + ("-0" + str(Q * 3 - 2) if Q < 4 else "-" + str(Q * 3 - 2)) + "-01"
      else:
          if x[4] == "M" or x[5] == "M":
              st = 6 if x[4] == "M" else 7
              M = x[(st-1):(st+1)]
              x = x[:4] + "-" + (M if len(M) == 2 else "0"+M) + "-01"
          else:  # Assuming now Year-Month type string
              if ncx != 8:
                   x += "-01"
          if end:
              x = _datetime.strftime(_datetime.strptime(x, "%Y-%m-%d") + _timedelta(days = 31), "%Y-%m-01")
              return _datetime.strftime(_datetime.strptime(x, "%Y-%m-%d") - _timedelta(days = 1), "%Y-%m-%d")
          else:
              return x
  if ncx != 10:
     raise Exception("x needs to be an object of class datetime.datetime or a (partial) date string.")
  return x.replace("/", "-")


# as_date(x = "2011Q1")
#
# as_date("2011M01", True)
#
# x = ["a", "b", "c", "a"]
# x.setdiff(set(x))
# help(pl.Categorical)

# x = data.get_column("date")
# l = data.drop("date")

def expand_date(x,
                gen = ["year", "quarter", "month"],
                keep_date = True,
                remove_missing_date = True,
                sort = True,
                # as_categorical = True,
                name = "date",
                **kwargs):
      """Generate Temporal Indentifiers from a Date Column.

            This function can be used to extact the year, quarter, month or day from a date column as additional columns. It is meant as an aid to facilitate
            computations.

            Parameters:
                x: either a date series (datetime.date or polars.datatypes.Date), or a DataFrame with a date column called 'name'.
                gen: a list of identifiers to generate from 'x'. The possible identifiers are "year", "quarter", "month" and "day".
                keep_date: boolean. 'True' will keep the date variable in the resulting dataset, 'False' will remove the date variable in favor of the generated identifiers.
                remove_missing_date: boolean. 'True' will remove missing values in 'x'. If 'x' is a DataFrame, rows missing the date column will be removed.
                sort: boolean. 'True' will sort the data by the date column.
                name: string. The name of the date column to expand.
                **kwargs: not used.

            Returns:
                A Polars DataFrame with additional columns next to, or in place of, the date column.

            Examples:
                import samadb as sm

                # Monthly business cycle data

                sm.expand_date(sm.data("BUSINESS_CYCLES"))

                # Same thing

                sm.data("BUSINESS_CYCLES", expand_date = True)
      """
      lxl = False
      genopts = ['year', 'quarter', 'month', 'day']

      if type(gen) is str:
          gen = [gen]
      elif type(gen) is int:
          gen = genopts[gen]
      # elif not set(gen).issubset(genopts):
      #  raise Exception("invalid gen options") # TODO: better error!!

      if not is_date(x):
          lxl = True
          if not name in x.columns:
              raise Exception("Column '{}' not found in dataset".format(name))
          l = x.drop(name)
          x = x.get_column(name)

      if type(x) is str: # TODO: What if is character Series ??
          x = _datetime.strptime(x, "%Y-%m-%d")
      elif not is_date(x):
           raise Exception("Column '{}' of type '{}' is not a date".format(name, str(type(x))))

      if remove_missing_date and x.is_null().any():
          nna = x.is_not_null()
          x = x[nna]
          if lxl:
              l = l.filter(nna)

      if not lxl and sort:
          x = x.sort()

      # Empty dictionary
      if keep_date:
          res = dict.fromkeys([name] + gen)
          res[name] = x
      else:
          res = dict.fromkeys(gen)

      xdt = x.dt
      for g in gen:
          if g == "year":
              res[g] = xdt.year()
          elif g == "quarter":
              res[g] = xdt.quarter()
          elif g == "month":
              res[g] = xdt.month()
          elif g == "day":
              res[g] = xdt.day()
          else:
              raise Exception("invalid gen option: " + g)

      res = _pl.DataFrame(res)

      if lxl:
          res = _pl.concat([res, l], how = "horizontal")
          if sort:
              res = res.sort(name if keep_date else gen)

      return res

# For internal use
_expand_date = expand_date


def data(dsid = None, 
         series = None,
         tfrom = None,
         tto = None,
         freq = None,
         labels = False,
         wide = True,
         expand_date = False,
         ordered = True,
         return_query = False,
         **kwargs):
    """Retrieve Data from the Database.

        This is the main function of the package to retrieve data from the database.

        Parameters:
            dsid: list of dataset id's matching the 'dsid' column of the 'DATASET' table (retrieved using 'sm.datasets()'). If used, all series from the dataset are returned, in addition to any other series selected with 'series'.
            series: list of series codes matching the 'series' column of the 'SERIES' table (retrieved using 'sm.series()'). If 'dsid' is also specificed, the two are combined using SQL 'OR' i.e. these series are retrieved in addition to all series matched through 'dsid'.
            tfrom: set the start time of the data retrieved by either supplying a start date, a date-string of the form "YYYY-MM-DD" or "YYYY-MM", year-quarters of the form "YYYYQN" or "YYYY-QN", or a numeric year YYYY (integer or string). These expressions are converted to a regular date (first day of period) by the included 'as_date()' function.
            tto: same as 'from', to set the time period until which data is retrieved. For expressions that are not full "YYYY-MM-DD" dates, the last day of the period is chosen.
            freq: string. Return only series at a certain frequency. Allowed are values "D" (Daily), "W" (Weekly), "M" (Monthly), "Q" (Quarterly), "A" (Annual), "AF" (Fiscal Years), matching the 'freq' column in the 'SERIES' table (retrieved using 'sm.series()').
            labels: boolean. 'True' will also return labels (series descriptions) along with the series codes. If 'wide = True', labels are returned in a separate DataFrame.
            wide: boolean. 'True' calls 'sm.pivot_wider()' on the result. 'False' returns the data in a long format without missing values.
            expand_date: boolean. 'True' will call 'sm.expand_date()' on the result.
            ordered: boolean. 'True' orders the result by 'date' and, if 'labels = True' and 'wide = False', by 'series', maintaining a fixed column-order of series. 'False' returns the result in a random order, to the benefit of faster query execution.
            return_query: boolean. 'True' will not query the database but instead return the constructed SQL query as a string (for debugging purposes).
            **kwargs: further arguments passed to 'sm.pivot_wider()' (if 'wide = True') or 'sm.expand_date()' (if 'expand_date = True'), no conflicts between these two.

        Returns:
            A Polars DataFrame, or, if 'labels = True' and 'wide = False', a tuple of two DataFrame's.

        Examples:
            import samadb as sm

            # Return all electricity indicators from 2000

            sm.data("ELECTRICITY", tfrom = 2000)
            
            # wide = False allows compact return in a single frame

            sm.data("ELECTRICITY", tfrom = 2000, wide = False)
            
            # Alternatively we can set labels = False to get a single wide frame

            sm.data("ELECTRICITY", tfrom = 2000, labels = False)
    """
    d0 = dsid is None
    s0 = series is None
    f0 = freq is None
    if not d0 and type(dsid) is str:
        dsid = [dsid]
    if not s0 and type(series) is str:
        series = [series]
    if not d0 and len(dsid) != len(set(dsid)):
        raise Exception("duplicated dataset id: " + ", ".join(set([x for x in dsid if dsid.count(x) > 1])))
    if not s0 and len(series) != len(set(series)):
        raise Exception("duplicated series: " +  ", ".join(set([x for x in series if series.count(x) > 1])))
    # Join series whenever necessary or for returning the full dataset in long format
    series_joined = not d0 or (d0 and s0 and not wide) or labels or not f0
    if series_joined:
        data = "DATA NATURAL JOIN SERIES"
        lab = ", label, unit, seas_adj" if labels else ""
    else:
        data = "DATA"
        lab = ""
    # Cases:
    # 0 dsid and series: return full -> checked
    # 1 dsid and 0 series: return only series codes -> checked
    # 0 dsid and some series: return series codes and dsid if series_joined -> checked
    # 1 dsid and some series: return dsid and series codes -> checked
    # multiple dsid: return dsid and series codes -> checked
    # Also: only need dsid if wide = FALSE
    cond = "" if d0 else "dsid = '{}'".format(dsid[0]) if len(dsid) == 1 else "dsid IN ('{}')".format("', '".join(dsid))
    vars = "date, dsid, series{}, value".format(lab) if not wide and (len(dsid) > 1 or not (d0 or s0) or (d0 and series_joined)) else "date, series{}, value".format(lab)
    if ordered: 
        ord = "s_order, date" if series_joined else "series, date" # Assumes s_order includes dsid!!
        
    if not s0:
        if d0:
            cond = "series = '{}'".format(series[0]) if len(series) == 1 else "series IN ('{}')".format("', '".join(series))
        else:
            cond = "({} OR series = '{}')".format(cond, series[0]) if len(series) == 1 else "({} OR series IN ('{}'))".format(cond, "', '".join(series))

    if tfrom is not None:
        cond += " AND date >= '" + as_date(tfrom) + "'"
    if tto is not None:
        cond += " AND date <= '" + as_date(tto, end = True) + "'"
    if not f0:
        cond += " AND freq = '" + freq[0].capitalize() + "'"
    where = " " if cond == "" else " WHERE " 
    if d0 and s0 and cond != "":
        cond = cond[5:]

    query = "SELECT " + vars + " FROM " + data + where + cond + (" ORDER BY " + ord if ordered else "")
    if return_query:
        return query

    res = _pl.read_sql(query, __uri__)
    if len(res) == 0:
        raise Exception("Query resulted in empty dataset. Please make sure that the dsid, series-codes or the date-range supplied in your query are consistent with the available data. See datasets() and series(). Alternatively check your connection to the database.")
    
    # Constructing enhanced label
    if labels:
        res = res.with_columns((_pl.col("label")  + ' (' + _pl.col("unit") +
          _pl.when((_pl.col("seas_adj") == 1) & (~_pl.col("label").str.contains(r"(?i)seasonally")))
            .then(', Seasonally Adjusted)').otherwise(')')).alias("label")).drop(["unit", "seas_adj"])

    if wide:
        if labels:
            kwargs["return_labels"] = True
            res, labels_df = pivot_wider(res, **kwargs)
        else:
            res = pivot_wider(res, **kwargs)
        if d0 and not s0 and len(series) > 1:
            res = res.select(["date"] + series)
    if expand_date:
        res = _expand_date(res, **kwargs)
    if wide and labels:
        return (res, labels_df)
    else:
        return res


def pivot_wider(x,
        id_cols = "auto",
        names_from = "series",
        values_from = "value",
        labels_from = "label",
        return_labels = False, # default True ???
        **kwargs):
    """Reshape Long API Data to Column-Based Format.
    
        This function automatically reshapes long (stacked) raw data from the API ('sm.data(**kwargs, wide = False)') to a wide format where each variable has its own column.

        Parameters:
            x: a Polars DataFrame e.g from 'sm.data(**kwargs, wide = False)'.
            id_cols: list of identifiers of the data. "auto" selects any variables in the 'sm.SAMADB_T' list if present in the data.
            names_from: string. The column containing the series codes. These will become the names of new columns in the wider data format.
            values_from: string. The column containing the data values to be distributed across the new columns.
            labels_from: string. The column containing the labels describing the series, if available.
            return_labels: boolean. If True, the function also returns a second DataFrame containing the labels for each series.
            **kwargs: not used.

        Returns:
            A Polars DataFrame, sorted by id_cols.
            
        Notes: 
            If the data is not uniquely identified by id_cols and names_from, the first value within each combination is taken. 

        Examples:
            import samadb as sm

            # Return all electricity indicators from the year 2000 onwards

            data = sm.data("ELECTRICITY", tfrom = 2000, wide = FALSE)
            
            # Reshaping wider

            sm.pivot_wider(data)

            # Same with labels

            data = sm.data("ELECTRICITY", tfrom = 2000, wide = False, labels = True)

            sm.pivot_wider(data, return_labels = True)
    """
    if type(id_cols) is str and id_cols == "auto":
        id_cols = [c for c in x.columns if c in SAMADB_T]

    # Reshape wider
    res = x.pivot(index = id_cols,
                  columns = names_from,
                  values = values_from,
                  aggregate_fn = 'first',
                  maintain_order = True,
                  sort_columns = False).sort(id_cols)
    
    # Get names and labels
    if return_labels and labels_from in x.columns:
        labels_df = x.select([names_from, labels_from]).unique()
        # Check that columns match labels
        if not all(labels_df.get_column(names_from) == res.columns[len(id_cols):]):
            raise Exception("Mismatch of aggregated names")
        return (res, labels_df)
    else:
        return res


# TODO: what about the row-order of the output ??
def pivot_longer(x,
        id_cols = "auto",
        to_value = None, # list(set(x.columns) - set(id_cols)) # -> Not needed
        variable_name = "series",
        value_name = "value",
        na_rm = True, # default True ?
        labels_df = None,
        **kwargs):
    """Reshape Column-Based Data to Long Format.
    
       This function automatically reshapes wide (column-based) data into a long format akin to the format of the raw data 
       coming from the database ('sm_data(**kwargs, wide = FALSE)').

        Parameters:
            x: a wide format Polars DataFrame where all series have their own column.
            id_cols: list of identifiers of the data. "auto" selects any variables in the 'sm.SAMADB_T' list if present in the data.
            to_value: list of names of all series to be stacked in the long format data frame. By default all non-id columns in 'x'.
            variable_name: string. The name of the variable to store the names of the series.
            value_name: string. The name of the variable to store the data values.
            na_rm: boolean. 'True' will remove all missing values from the long data frame.
            labels_df: an optional Polars DateFrame providing labels for the series to be stored in an extra column in the long frame. 
                This DataFrame has two columns: the first containing the series codes, the second the series labels. The column names of this DataFrame are not relevant. See the second example.
            **kwargs: not used.

        Returns:
            A Polars DataFrame.

        Examples:
            import samadb as sm

            # Return all electricity indicators from the year 2000 onwards

            data = sm.data("ELECTRICITY", tfrom = 2000)
            
            # Reshaping to long

            sm.pivot_longer(data)

            # Same with labels

            data, labels_df = sm.data("ELECTRICITY", tfrom = 2000, labels = True)

            sm.pivot_longer(data, labels_df = labels_df)
    """
    if type(id_cols) is str and id_cols == "auto":
        id_cols = [c for c in x.columns if c in SAMADB_T] 

    if type(id_cols) is not list:
        id_cols = [id_cols]
    # Reshape longer
    res = x.melt(id_vars = id_cols,
                 value_vars = to_value,
                 variable_name = variable_name,
                 value_name = value_name)
    if na_rm:
        res = res.drop_nulls(value_name)

    if labels_df is not None:
        if labels_df.shape[1] != 2:
            raise Exception("labels_df needs to be a data fram with 2 columns, the first holding the series codes and the second the corresponding labels")
        res = res.join(labels_df, left_on = variable_name, right_on = labels_df.columns[0],
                      how = "left").select(id_cols +
                      [variable_name, labels_df.columns[1], value_name])
    return res


# Miscellaneous testing
# if __name__ == '__main__':
