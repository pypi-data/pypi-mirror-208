
"""
Africa Macroeconomic Monitor Database API

An Python API providing access to a relational database with macroeconomic data for Africa. The
database is maintained at the Kiel Institute for the World Economy. The package is built around the
Polars DataFrame library. Its contents are summarized as follows:

Datasets providing information about the available data

sources()       - Data sources
series()        - Series (can be queried by source)
countries()     - African countries
countries_wld() - All countries (data is provided for all available countries)
entities()      - Regional entities in Africa

Retrieve the data from the database

data()          - By default retrieves all data for all African countries

Functions to reshape data and add temporal identifiers

pivot_wider()   - Wrapper around Polars .melt()
pivot_longer()  - Wrapper around Polars .pivot()
expand_date()   - Create Year, Quarter, Month or Day columns from a date

Helper functions to convert inputs to date strings

as_date()       - E.g. "2011M01" -> "2011-01-01"

Lists with identifiers

AMCOUNTRY       - ISO3 codes of 55 African countries
AMID            - Cross-sectional identifiers
AMT             - Temporal identifiers

"""


import polars as _pl
from datetime import datetime as _datetime, timedelta as _timedelta

AMID = ["ISO3", "Series"]

AMT = ["Date", "Year", "Quarter", "Month", "Day"] # , "FY", "QFY"

AMCOUNTRY = ["DZA", "AGO", "BEN", "BWA", "BFA", "BDI", "CMR", "CPV", "CAF", "TCD",
             "COM", "COG", "COD", "CIV", "DJI", "EGY", "GNQ", "ERI", "SWZ", "ETH",
             "GAB", "GMB", "GHA", "GIN", "GNB", "KEN", "LSO", "LBR", "LBY", "MDG",
             "MWI", "MLI", "MRT", "MUS", "MAR", "MOZ", "NAM", "NER", "NGA", "RWA",
             "SEN", "SYC", "SLE", "SOM", "ZAF", "SSD", "SDN", "STP", "TZA", "TGO",
             "TUN", "UGA", "ESH", "ZMB", "ZWE"]

__uri__ = "mysql://IFW_READ:$QL5Dbg8+^g`)$D.@65.108.142.177:3306/AFRMDB"


### Some failed attempts to include package data as Polars dataframe
### I also asked about it: https://stackoverflow.com/questions/74584709/python-cross-plattform-single-module-package-including-csv-data-files-to-be-read

## import os
# os.getcwd()
# os.chdir("src")

# Reading data
# TODO: Need to make cross-plattform compatible?:
# https://kiwidamien.github.io/making-a-python-package-vi-including-data-files.html


## import os
#
# _ROOT = os.path.abspath(os.path.dirname(__file__))
# def get_data(path):
#     return os.path.join(_ROOT, 'data', path)

# print get_data('resource1/foo.txt')


# import pkg_resources
#
# def load_countries():
#     """Return a dataframe about the 68 different Roman Emperors.
#
#     Contains the following fields:
#         index          68 non-null int64
#         name           68 non-null object
#         name.full      68 non-null object
#     ... (docstring truncated) ...
#
#     """
#     # This is a stream-like object. If you want the actual info, call stream.read()
#     stream = pkg_resources.resource_stream(__name__, 'africamonitor/data/countries.csv')
#     return _pl.read_csv(stream)

# DATA_PATH = pkg_resources.resource_filename('africamonitor', 'data/')

# import pkg_resources
#
# my_file = pkg_resources.resource_filename('africamonitor', 'data/countries.csv')
#
# countries = _pl.read_csv("data/countries.csv")

# def load_countries_wld():
#     stream = pkg_resources.resource_stream(__name__, 'africamonitor/data/countries_wld.csv')
#     return _pl.read_csv(stream)

# countries_wld = _pl.read_csv(DATA_PATH + "countries_wld.csv")

# def load_entities():
#     stream = pkg_resources.resource_stream(__name__, 'africamonitor/data/entities.csv')
#     return _pl.read_csv(stream)

# entities = _pl.read_csv(DATA_PATH + "entities.csv")

# import pkgutil
#
# data_pathc = pkgutil.get_data("africamonitor", "countries.csv")
#

### In the meanwhile, I just load it from the database

def countries():
    """Retrieve African Countries Table.

        Columns:
            Country - Short Country Name
            Country_ISO - ISO Standardized Country Name
            ISO2 - ISO 2-Character Country Code
            ISO3 - ISO 3-Character Country Code
            ISO3N - ISO Numeric Country Code
            IMF - IMF Numeric Country Code
            Region - 2-Region Classification (UN except for Sudan)
            Region_Detailed - 5-Region Classification (Former World Bank)
            Currency - Main Official Currency

        Returns:
            A Polars DataFrame providing information about 55 African countries (Incl. Western Sahara).
    """
    res = _pl.read_sql("SELECT * FROM COUNTRY ORDER BY Country", __uri__)
    if len(res) == 0:
        raise Exception("Query resulted in empty dataset. This means something is wrong with your internet connection, the connection to the database or with the database itself.")
    return res

def countries_wld():
    """Retrieve All Countries Table.

        Columns:
            Country - Short Country Name
            Country_ISO - ISO Standardized Country Name
            ISO2 - ISO 2-Character Country Code
            ISO3 - ISO 3-Character Country Code
            ISO3N - ISO Numeric Country Code
            IMF - IMF Numeric Country Code
            Region - 2-Region Classification (UN except for Sudan)
            Region_Detailed - 5-Region Classification (Former World Bank)
            Currency - Main Official Currency

        Returns:
            A Polars DataFrame providing information about 195 countires in the World (193 UN Members, Western Sahara and Taiwan).
    """
    res = _pl.read_sql("SELECT * FROM COUNTRY_WLD ORDER BY Country", __uri__)
    if len(res) == 0:
        raise Exception("Query resulted in empty dataset. This means something is wrong with your internet connection, the connection to the database or with the database itself.")
    return res

def entities():
    """Retrieve African Regional Entities Table.

        Columns:
            Country - Short Country Name
            Country_ISO - ISO Standardized Country Name
            ISO2 - ISO 2-Character Country Code
            ISO3 - ISO 3-Character Country Code
            ISO3N - ISO Numeric Country Code
            IMF - IMF Numeric Country Code
            NOA - North Africa
            SSA - Sub-Saharan Africa
            OEC - Oil-Exporting Countries
            MIC - Middle-Income Countries
            LIC - Low-Income Countries
            CFS - Countries in Fragile Situations
            WAEMU - West African Economic and Monetary Union
            CEMAC - Economic and Monetary Community of Central Africa
            COMESA - Common Market for Eastern and Southern Africa
            EAC - East African Community
            EAC5 - East African Community Excl. South Sudan
            SADC - Southern African Development Community
            SACU - Southern African Customs Union
            ECOWAS - Economic Community of West African States
            ECCAS - Economic Community of Central African States
            AMU - Arab Maghreb Union
            CEN_SAD - Community of Sahel-Saharan States
            IGAD - Intergovernmental Authority on Development
            CwA - Compact with Africa
            ORIC - Other Resource-Intensive Countries
            NRIC - Non-Resource Intensive Countries

        Returns:
            A Polars DataFrame providing information about regional entities in Africa.
    """
    res = _pl.read_sql("SELECT * FROM ENTITY ORDER BY Country", __uri__)
    if len(res) == 0:
        raise Exception("Query resulted in empty dataset. This means something is wrong with your internet connection, the connection to the database or with the database itself.")
    return res

def sources(ordered = True):
    """Retrieve Data Sources Table.

        Parameters:
            ordered: logical. 'True' orders the result in the order data was entered into the database, while 'False' returns the result in a random order, to the benefit of faster query execution.

        Returns:
            A Polars DataFrame providing information about the sources of data in the Africamonitor Database.
    """
    query = "SELECT DSID, Source, Url, NSeries, Frequency, Data_From, Data_To, Description, Updated, Access FROM DATASOURCE"
    if ordered:
        query += " ORDER BY DS_Order"
    res = _pl.read_sql(query, __uri__)
    if len(res) == 0:
        raise Exception("Query resulted in empty dataset. This means something is wrong with your internet connection, the connection to the database or with the database itself.")
    return res


def series(dsid = None,
           source_info = True,
           ordered = True,
           return_query = False):
  """Retrieve Series Table.

        Parameters:
            dsid: (optional) list of id's of datasources matching the 'DSID' column of the data sources table ('am.sources()').
            source_info: logical. 'True' returns additional information from the data sources table (the source, the frequency of the data and when data from the source was last updated).
            ordered: logical. 'True' returns the series in a fixed order, while 'False' returns the result in a random order, to the benefit of faster query execution.
            return_query: logical. 'True' will not query the database but instead return the constructed SQL query as a character string (for debugging purposes).

        Returns:
            A Polars DataFrame providing the codes and labels of all series in the Africamonitor Database.

        Notes:
            Columns 'DSID', 'Updated' and 'Source' are added from the data sources table ('am.sources()').
            Columns 'Nctry' and 'Avg_Obs' show the data availability for Africa. The database has data for all countries.

        Examples:
            import africamonitor as am

            # By default returns all series with additional information
            am.series()

            # Raw series table
            am.series(source_info = False)

            # Only series in the WEO
            am.series("IMF_WEO")
  """
  if source_info:
    query = "SELECT DSID, Series, Label, Topic, S_Frequency, S_From, S_To, Nctry, Avg_Obs, Updated, Source, S_Description, S_Source, S_Url FROM SERIES NATURAL JOIN DATASOURCE" # , DS_Url
  else:
    query = "SELECT Series, Label, Topic, S_Frequency, S_From, S_To, Nctry, Avg_Obs, S_Description, S_Source, S_Url FROM SERIES"

  if dsid is not None:
      if type(dsid) is str:
          dsid = [dsid]
      if len(dsid) == 1:
          query += " WHERE DSID = '" + "".join(dsid) + "' ORDER BY S_Order" if ordered else "'"
      else:
          query += " WHERE DSID IN ('" + "', '".join(dsid) + "') ORDER BY S_Order" if ordered else "')"
  elif ordered:
      query += " ORDER BY S_Order"

  if return_query:
      return query
  res = _pl.read_sql(query, __uri__)
  if len(res) == 0:
      raise Exception("Query resulted in empty dataset. This means something is wrong with your internet connection, the connection to the database or with the database itself.")
  return res


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
            x: a datetime.date or date-string "YYYY-MM-DD" or "YYYY-MM", year-quarter "YYYYQN" or "YYYY-QN", year-month "YYYYMNN" or "YYYY-MNN", fiscal year "YYYY/YY" or calendar year YYYY (integer or string).
            end: logical. 'True' replaces missing time information with a period end-date which is the last day of the period. 'False' replaces missing month and day information with "-01".

        Returns:
            A complete "YYYY-MM-DD" date-string.

        Examples:
            import africamonitor as am
            am.as_date("2011-05")
            am.as_date(2011)
            am.as_date("2011/12")
            am.as_date("2011/12", end = True)
            am.as_date("2011Q1")
            am.as_date("2011Q1", end = True)
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

  if ncx >= 6 and ncx <= 8:  # could be "1999/1"
      if x[4] == "/":
          return str(int(x[:4]) + 1) + "-06-30" if end else x[:4] + "-07-01"
      elif x[4] == "Q" or x[5] == "Q":
          Q = int(x[ncx-1])
          if end:
              return x[:4] + "-0" + str(Q * 3) + ("-31" if Q % 2 else "-30")
          else:
              return x[:4] + "-0" + str(Q * 3 - 2) + "-01"
      else:
          if x[4] == "M" or x[5] == "M":
              st = 6 if x[4] == "M" else 7
              M = x[(st-1):(st+1)]
              x = x[:4] + "-" + M + "-01"
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

# x = data.get_column("Date")
# l = data.drop("Date")

def expand_date(x,
                gen = ["Year", "Quarter", "Month"],
                keep_date = True,
                remove_missing_date = True,
                sort = True,
                # as_categorical = True,
                name = "Date",
                **kwargs):
      """Generate Temporal Indentifiers from a Date Column.

            This function can be used to extact the year, quarter, month or day from a date column as additional columns. It is meant as an aid to facilitate
            computations on data from the Africamonitor Database.

            Parameters:
                x: either a date deries (datetime.date or polars.datatypes.Date), or a DataFrame with a date column called 'name'.
                gen: a list of identifiers to generate from 'x'. The possible identifiers are "Year", "Quarter", "Month" and "Day".
                keep_date: logical. 'True' will keep the date variable in the resulting dataset, 'False' will remove the date variable in favor of the generated identifiers.
                remove_missing_date: logical. 'True' will remove missing values in 'x'. If 'x' is a DataFrame, rows missing the date column will be removed.
                sort: logical. 'True' will sort the data by the date column.
                name: string. The name of the date column to expand.
                **kwargs: not used.

            Returns:
                A Polars DataFrame with additional columns next to, or in place of, the date column.

            Examples:
                import africamonitor as am

                # Monthly Industrial Production in Kenya
                am.expand_date(am.data("KEN", "AIP_IX_M"))

                # Same thing
                am.data("KEN", "AIP_IX_M", expand_date = True)
      """
      lxl = False
      genopts = ['Year', 'Quarter', 'Month', 'Day']

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
          if g == "Year":
              res[g] = xdt.year()
          elif g == "Quarter":
              res[g] = xdt.quarter()
          elif g == "Month":
              res[g] = xdt.month()
          elif g == "Day":
              res[g] = xdt.day()
          else:
              raise Exception("invalid gen option: " + g)

      res = _pl.DataFrame(res)

      if lxl:
          if "ISO3" in l.columns:
              res = _pl.concat([l.select("ISO3"), res, l.drop("ISO3")], how = "horizontal")
              if sort:
                  res = res.sort(["ISO3", name] if keep_date else ["ISO3"] + gen)
          else:
              res = _pl.concat([res, l], how = "horizontal")
              if sort:
                  res = res.sort(name if keep_date else gen)

      return res

# For internal use
_expand_date = expand_date


def data(ctry = AMCOUNTRY, #list(countries["ISO3"]),
         series = None,
         tfrom = None,
         tto = None,
         labels = False,
         wide = True,
         expand_date = False,
         drop_1iso3c = True,
         ordered = True,
         return_query = False,
         **kwargs):
    """Retrieve Data from the Africamonitor Database.

        This is the main function of the package and used to retrieve data from the Africamonitor Database.

        Parameters:
            ctry: list of ISO3 country codes. There is a variable 'AMCOUNTRY' in the package namespace containing the codes of all 55 African countries, and this list is specified as the default argument, but the database has data for all countries where available. The codes for all countries can be found in the 'am.countries_wld()' table. Putting 'None' gets data for all countries.
            series: list of series codes matching the 'Series' column of the SERIES table (retrieved using 'am.series()').
            tfrom: set the start time of the data retrieved by either supplying a start date, a date-string of the form "YYYY-MM-DD" or "YYYY-MM", year-quarters of the form "YYYYQN" or "YYYY-QN", a numeric year YYYY (integer or string), or a fiscal year of the form "YYYY/YY". These expressions are converted to a regular date (first day of period) by the included 'as_date()' function.
            tto: same as 'from', to set the time period until which data is retrieved. For expressions that are not full "YYYY-MM-DD" dates, the last day of the period is chosen.
            labels: logical. 'True' will also return labels (series descriptions) along with the series codes. If 'wide = True', labels are returned in a separate DataFrame.
            wide: logical. 'True' calls 'am.pivot_wider()' on the result. 'False' returns the data in a long format without missing values.
            expand_date: logical. 'True' will call 'am.expand_date()' on the result.
            drop_1iso3c: logical. If only one country is selected through 'ctry', 'True' will drop the 'ISO3' column in the output.
            ordered: logical. 'True' orders the result by 'Date' and, if 'labels = True' and 'wide = False', by series, maintaining a fixed column-order of series. 'False' returns the result in a random order, to the benefit of faster query execution.
            return_query: logical. 'True' will not query the database but instead return the constructed SQL query as a character string (for debugging purposes).
            **kwargs: further arguments passed to 'am.pivot_wider()' (if 'wide = True') or 'am.expand_date()' (if 'expand_date = True'), no conflicts between these two.

        Returns:
            A Polars DataFrame.

        Examples:
            import africamonitor as am

            # Return all indicators for Kenya from 2000
            am.data("KEN", tfrom = 2015)

            # Return all indicators for Kenya from 2000 in long format
            am.data("KEN", tfrom = 2015, wide = False)
            am.data("KEN", tfrom = 2015, wide = False, labels = True)

            # Return wide, with date expanded, and auxiliary labels data frame
            am.data("KEN", tfrom = 2015, expand_date = True, labels = True)

            # Getting only GDP growth
            am.data("KEN", "NGDP_RPCH", tfrom = 2015)
            am.data("KEN", "NGDP_RPCH", tfrom = 2015, drop_1iso3c=False)

            # Getting GDP growth for all countries
            am.data(series = "NGDP_RPCH", tfrom = 2015)

            # Getting growth and inflation for the EAC countries (all available years)
            am.data(ctry = ["UGA", "KEN", "TZA", "RWA", "BDI", "SSD"],
                    series = ["NGDP_RPCH", "PCPIPCH"])
    """
    c0 = ctry is None
    s0 = series is None
    if not c0 and type(ctry) is str:
        ctry = [ctry]
    if not s0 and type(series) is str:
        series = [series]
    if not c0 and len(ctry) != len(set(ctry)):
        raise Exception("duplicated country code: " + ", ".join(set([x for x in ctry if ctry.count(x) > 1])))
    if not s0 and len(series) != len(set(series)):
        raise Exception("duplicated series code: " +  ", ".join(set([x for x in series if series.count(x) > 1])))
    if labels:
        data = "DATA NATURAL JOIN SERIES"
        lab = ", Label"
    else:
        data = "DATA"
        lab = ""

    if not c0 and drop_1iso3c and len(ctry) == 1:
        cond = "ISO3 = '" + "".join(ctry) + "'"
        vars = "Date, Series" + lab + ", Value"
        if ordered:
            ord = "S_Order, Date" if labels else "Series, Date"
    else:
        cond = "" if c0 else "ISO3 IN ('" + "', '".join(ctry) + "')"
        vars = "ISO3, Date, Series" + lab + ", Value"
        if ordered:
            ord = "ISO3, S_Order, Date" if labels else "ISO3, Series, Date"

    if not s0:
        add = "" if c0 else " AND "
        if len(series) == 1:
          # vars <- sub(", Series", "", vars) # This is inconvenient -> cannot use pivot_wider anymore
            cond += add + "Series = '" + "".join(series) + "'"
        else:
            cond += add + "Series IN ('" + "', '".join(series) + "')"

    if tfrom is not None:
        cond += " AND Date >= '" + as_date(tfrom) + "'"
    if tto is not None:
        cond += " AND Date <= '" + as_date(tto, end = True) + "'"
    where = " " if c0 and s0 else " WHERE " # TODO: Works ??

    query = "SELECT " + vars + " FROM " + data + where + cond + (" ORDER BY " + ord if ordered else "")
    if return_query:
        return query

    res = _pl.read_sql(query, __uri__)
    if len(res) == 0:
        raise Exception("Query resulted in empty dataset. Please make sure that the ISO3, series-codes or the date-range supplied in your query are consistent with the available data. See sources() and series(). Alternatively check your connection to the database.")

    if wide:
        if labels:
            kwargs["return_labels"] = True
            res, labels_df = pivot_wider(res, **kwargs)
        else:
            res = pivot_wider(res, **kwargs)
        if not s0 and len(series) > 1:
            res = res.select((["ISO3", "Date"] if (c0 or len(ctry) > 1 or not drop_1iso3c) else ["Date"]) + series)
    if expand_date:
        res = _expand_date(res, **kwargs)
    if wide and labels:
        return (res, labels_df)
    else:
        return res


def pivot_wider(x,
        id_cols = "auto",
        names_from = "Series",
        values_from = "Value",
        labels_from = "Label",
        return_labels = False, # default True ???
        **kwargs):
    """Reshape Long API Data to Column-Based Format.

        Parameters:
            x: a Polars DataFrame e.g from 'am.data(**kwargs, wide = False)'.
            id_cols: list of identifiers of the data. "auto" selects any variables in the 'am.AMT' list and "ISO3" if present in the data.
            names_from: string. The column containing the series codes. These will become the names of new columns in the wider data format.
            values_from: string. The column containing the data values to be distributed across the new columns.
            labels_from: string. The column containing the labels describing the series, if available.
            **kwargs: not used.

        Returns:
            A Polars DataFrame.

        Examples:
            import africamonitor as am

            # Getting growth and inflation for the EAC countries (all available years)
            data = am.data(ctry = ["UGA", "KEN", "TZA", "RWA", "BDI", "SSD"],
                           series = ["NGDP_RPCH", "PCPIPCH"], wide = False)
            # Reshaping wider
            am.pivot_wider(data)

            # Same with labels
            data = am.data(ctry = ["UGA", "KEN", "TZA", "RWA", "BDI", "SSD"],
                           series = ["NGDP_RPCH", "PCPIPCH"], wide = False, labels = True)
            am.pivot_wider(data)
    """
    if type(id_cols) is str and id_cols == "auto":
        id_all = ["ISO3"] + AMT
        id_cols = [c for c in x.columns if c in id_all] # Faster but does not preserve order: list(set(x.columns) & set(["ISO3"] + AMT))

    if "Label" not in x.columns:
        labels_from = None

    # Reshape wider
    res = x.pivot(index = id_cols,
                  columns = names_from,
                  values = values_from,
                  aggregate_fn = 'first',
                  maintain_order = True,
                  sort_columns = False).sort(id_cols)
    # Get names and labels
    if return_labels:
        labels_df = x.select([names_from, labels_from]).unique()
        # Check that columns match labels
        if not all(labels_df.get_column(names_from) == res.columns[len(id_cols):]):
            raise Exception("Mismatch of aggregated names")
    # # Attach labels to columns: does not seem to work
    # # Stackoverflow: https://stackoverflow.com/questions/74278857/python-polars-attach-attributes-to-series-in-dataframe
    # for nam, lab in labels_df.rows():
    #     ser = res[nam]
    #     ser.label = [lab]
    #     res = res.replace(nam, ser)
    if return_labels:
        return (res, labels_df)
    else:
        return res


# TODO: what about the row-order of the output ??
def pivot_longer(x,
        id_cols = "auto",
        to_value = None, # list(set(x.columns) - set(id_cols)) # -> Not needed
        variable_name = "Series",
        value_name = "Value",
        na_rm = True, # default True ?
        labels_df = None,
        **kwargs):
    """Reshape Column-Based Data to Long Format.

        Parameters:
            x: a wide format Polars DataFrame where all series have their own column.
            id_cols: list of identifiers of the data. "auto" selects any variables in the 'am.AMT' list and "ISO3" if present in the data.
            to_value: list of names of all series to be stacked in the long format data frame. By default all non-id columns in 'x'.
            variable_name: string. The name of the variable to store the names of the series.
            value_name: string. The name of the variable to store the data values.
            na_rm: logical. 'True' will remove all missing values from the long data frame.
            labels_df: an optional Polars DateFrame providing labels for the series to be stored in an extra column in the long frame. This DataFrame has two columns: the first containing the series codes, the second the series labels. The column names of this DataFrame are not relevant. See the second example.
            **kwargs: not used.

        Returns:
            A Polars DataFrame.

        Examples:
            import africamonitor as am

            # Getting growth and inflation for the EAC countries (all available years)
            data = am.data(ctry = ["UGA", "KEN", "TZA", "RWA", "BDI", "SSD"],
                           series = ["NGDP_RPCH", "PCPIPCH"])
            # Reshaping to long
            am.pivot_longer(data)

            # Same with labels
            data, labels_df = am.data(ctry = ["UGA", "KEN", "TZA", "RWA", "BDI", "SSD"],
                                      series = ["NGDP_RPCH", "PCPIPCH"], labels = True)
            am.pivot_longer(data, labels_df = labels_df)
    """
    if type(id_cols) is str and id_cols == "auto":
        id_all = ["ISO3"] + AMT
        id_cols = [c for c in x.columns if c in id_all] # Faster but does not preserve order: list(set(x.columns) & set(["ISO3"] + AMT))

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
# if (__name__ == '__main__'):
