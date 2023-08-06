"""This module contains the Company class, which provides methods for obtaining
financial reports and calculating financial indicators for a company. Users can
set the accounting method, unit, tax rate, and language for the company object.

Classes:
    Company: Represents a company with its financial information and allows
    users to generate financial reports and indicators.

Abreviations used in code:
    dfc = company dataframe
    dfi = input dataframe
    dfo = output dataframe

RuntimeWarning:
    Pandas query + numexpr module -> Engine has switched to 'python' because
    numexpr does not support extension array dtypes (category not supported
    yet). Please set your engine to python manually. That means that the query
    method has to use engine='python' to work with category dtype. N.B. Only
    FinLogic Dataframe uses category dtype for efficiency.

"""
from typing import Literal
import numpy as np
import pandas as pd
from .language import language_df
from .finprint import print_dict
from .fl_duckdb import execute


class Company:
    """A class to represent a company financial data.

    This class provides methods to create financial reports and to calculate
    financial indicators based on a company's accounting data. The class also
    has an AI generated dictionary to translate from Portuguese to English.

    Methods:
        report: Creates a financial report for the company.
        custom_report: Creates a custom financial report for the company.
        indicators: Calculates the financial indicators of the company.

    Raises:
        ValueError: If the input arguments are invalid.
    """

    def __init__(
        self,
        identifier: int | str,
        acc_method: Literal["consolidated", "separate"] = "consolidated",
        acc_unit: int | float | str = 1,
        tax_rate: float = 0.34,
        language: str = "english",
    ):
        """Initializes a new instance of the Company class."""
        self._initialized = False
        self.identifier = identifier
        self.acc_method = acc_method
        self.acc_unit = acc_unit
        self.tax_rate = tax_rate
        self.language = language
        self._initialized = True
        # Only set company dataframe after identifier, acc_method and acc_unit are set
        self._set_dfc()

    @property
    def identifier(self) -> int | str:
        """Set a unique identifier to select the company in FinLogic Database.

        This method sets the company's CVM and fiscal ID based on a given
        identifier. The identifier can be either the CVM ID or the Fiscal ID
        (CNPJ). If the identifier is not found in the database, a KeyError is
        raised.

        Args:
            identifier: A unique identifier to select a company in FinLogic
                Database. Both CVM ID or Fiscal ID can be used. CVM ID
                (regulator number) must be an integer. Fiscal ID must be a
                string in 'XX.XXX.XXX/XXXX-XX' format.

        Returns:
            None

        Raises:
            KeyError: If the given identifier isn't found in Finlogic Database.
        """
        return self._identifier

    @identifier.setter
    def identifier(self, identifier: int | str):
        # Create custom data frame for ID selection
        query = f"""
            SELECT DISTINCT cvm_id, tax_id, name_id
              FROM reports
             WHERE CAST(cvm_id AS VARCHAR) = '{identifier}'
                OR tax_id = '{identifier}'
        """
        df = execute(query, "df")
        if not df.empty:
            self._cvm_id = df.loc[0, "cvm_id"]
            self.tax_id = df.loc[0, "tax_id"]
            self.name_id = df.loc[0, "name_id"]
            self._identifier = identifier
        else:
            raise KeyError(f"Company 'identifier' {identifier} not found.")
        # If object was already initialized, reset company dataframe
        if self._initialized:
            self._set_dfc()

    @property
    def acc_method(self) -> Literal["consolidated", "separate"]:
        """Gets or sets the accounting method for registering investments in
        subsidiaries.

        The "acc_method" must be "consolidated" or "separate". Consolidated
        accounting combines the financial statements of a parent company and its
        subsidiaries, while separate accounting keeps them separate. Defaults to
        'consolidated'.

        Raises:
            ValueError: If the accounting method is invalid.
        """
        return self._acc_unit

    @acc_method.setter
    def acc_method(self, value: Literal["consolidated", "separate"]):
        if value in {"consolidated", "separate"}:
            # Set accounting method to upper case as in FinLogic Database
            self._acc_method = value.upper()
        else:
            raise ValueError("acc_method expects 'consolidated' or 'separate'")
        # If object was already initialized, reset company dataframe
        if self._initialized:
            self._set_dfc()

    @property
    def acc_unit(self) -> float:
        """Gets or sets the accounting unit for the financial statements.

        The "acc_unit" is a constant that will divide all company
        accounting values. The constant must be a number greater than
        zero or one of the following strings:
            - "thousand" to represent thousands       (1,000)
            - "million" to represent millions     (1,000,000)
            - "billion" to represent billions (1,000,000,000)

        Returns:
            The current accounting unit.

        Raises:
            ValueError: If the accounting unit is invalid.

        Examples:
            To set the accounting unit to millions:
                company.acc_unit = "million"

            To set the accounting unit to a custom factor, e.g., 10,000:
                company.acc_unit = 10_000
        """
        return self._acc_unit

    @acc_unit.setter
    def acc_unit(self, value: int | float | str) -> float | int:
        match value:
            case "thousand":
                self._acc_unit = 1_000
            case "million":
                self._acc_unit = 1_000_000
            case "billion":
                self._acc_unit = 1_000_000_000
            case str():  # Add this case to catch invalid strings
                raise ValueError("Invalid string for Accounting Unit")
            case v if v > 0:
                self._acc_unit = v
            case _:
                raise ValueError("Accounting Unit is invalid")

        # If object was already initialized, reset company dataframe
        if self._initialized:
            self._set_dfc()

    @property
    def tax_rate(self) -> float:
        """Gets or sets company 'tax_rate' property.

        The "tax_rate" is used to calculate some of the company
        indicators, such as EBIT and net income. The default value
        is 0.34, which is the standard corporate tax rate in Brazil.

        Returns:
            The tax rate value.

        Raises:
            ValueError: If the tax rate is not a float between 0 and 1.

        Examples:
            To set the tax rate to 21%:
                company.tax_rate = 0.21

            To set the tax rate to 0% (tax exempt):
                company.tax_rate = 0.0
        """
        return self._tax_rate

    @tax_rate.setter
    def tax_rate(self, value: float):
        if 0 <= value <= 1:
            self._tax_rate = value
        else:
            raise ValueError("Company 'tax_rate' value is invalid")

    @property
    def language(self) -> str:
        """Gets or sets the language of the account names.

        It is the language used in the account names of the financial
        statements. This property accepts a string representing the
        desired language. Supported languages are "english" and
        "portuguese". The default is 'english'.

        Returns:
            The language used in the account names.

        Raises:
            KeyError: If the provided language is not supported.
        """

        return self._language

    @language.setter
    def language(self, language: str):
        # Supported languages
        list_languages = ["english", "portuguese"]
        if language.lower() in list_languages:
            self._language = language.capitalize()
        else:
            sup_lang = f"Supported languages: {', '.join(list_languages)}"
            raise KeyError(f"'{language}' not supported. {sup_lang}")

    def _set_dfc(self) -> pd.DataFrame:
        """Sets the company data frame.

        This method creates a data frame with the company's financial
        statements.
        """
        # Create the company data frame
        query = f"""
            SELECT *
              FROM reports
             WHERE cvm_id = {self._cvm_id}
               AND acc_method = '{self._acc_method}'
             ORDER BY acc_code, period_reference, period_end
        """
        dfc = execute(query, "df")

        # Change acc_unit only for accounts different from 3.99
        dfc["acc_value"] = np.where(
            dfc["acc_code"].str.startswith("3.99"),
            dfc["acc_value"],
            dfc["acc_value"] / self._acc_unit,
        )
        annual_reports = dfc.query('report_type == "ANNUAL"')
        self._first_annual = annual_reports["period_end"].min()
        self._last_annual = annual_reports["period_end"].max()
        quarterly_reports = dfc.query('report_type == "QUARTERLY"')
        self._last_quarterly = quarterly_reports["period_end"].max()

        # Drop columns that are already company atributes
        dfc.drop(columns=["name_id", "cvm_id", "tax_id", "acc_method"], inplace=True)

        # Keep only the newest 'report_version' in df
        cols = [
            "report_type",
            "report_version",
            "period_reference",
            "period_order",
            "acc_code",
        ]
        dfc.sort_values(by=cols, ignore_index=True, inplace=True)
        cols = dfc.columns.tolist()
        cols_remove = ["report_version", "acc_value", "acc_fixed"]
        [cols.remove(col) for col in cols_remove]
        # Ascending order --> last is the newest report_version
        dfc.drop_duplicates(cols, keep="last", inplace=True, ignore_index=True)

        # Set company data frame
        self._dfc = dfc

    def info(self) -> dict:
        """Print a concise summary of a company."""
        # Some companies have no quarterly reports (see cvm_id 9784)
        if self._last_quarterly is pd.NaT:
            last_quarterly = "No quarterly reports"
        company_info = {
            "Name": self.name_id,
            "CVM ID": self._cvm_id,
            "Fiscal ID (CNPJ)": self.tax_id,
            "Total Accounting Rows": len(self._dfc.index),
            "Selected Accounting Method": self._acc_method,
            "Selected Accounting Unit": self._acc_unit,
            "Selected Tax Rate": self._tax_rate,
            "First Annual Report": self._first_annual.strftime("%Y-%m-%d"),
            "Last Annual Report": self._last_annual.strftime("%Y-%m-%d"),
            "Last Quarterly Report": last_quarterly,
        }
        print_dict(info_dict=company_info, table_name="Company Info")

    def _build_report(self, dfi: pd.DataFrame) -> pd.DataFrame:
        # keep only last quarterly fs
        if self._last_annual > self._last_quarterly:
            df = dfi.query('report_type == "ANNUAL"').copy()
            df.query(
                "period_order == 'PREVIOUS' or \
                 period_end == @self._last_annual",
                inplace=True,
            )
        else:
            df = dfi.query(
                'report_type == "ANNUAL" or \
                 period_end == @self._last_quarterly'
            ).copy()
            df.query(
                "period_order == 'PREVIOUS' or \
                 period_end == @self._last_quarterly or \
                 period_end == @self._last_annual",
                inplace=True,
            )

        # Create output dataframe with only the index
        dfo = df.sort_values(by="period_end", ascending=True)[
            ["acc_name", "acc_code", "acc_fixed"]
        ].drop_duplicates(subset="acc_code", ignore_index=True, keep="last")

        periods = sorted(df["period_end"].drop_duplicates())
        for period in periods:
            year_cols = ["acc_value", "acc_code"]
            df_year = df.query("period_end == @period")[year_cols].copy()
            period_str = period.strftime("%Y-%m-%d")
            if period == self._last_quarterly:
                period_str += " (ttm)"
            df_year.rename(columns={"acc_value": period_str}, inplace=True)
            dfo = pd.merge(dfo, df_year, how="left", on=["acc_code"])

        return dfo.sort_values("acc_code", ignore_index=True)

    def report(
        self,
        report_type: str,
        acc_level: int | None = None,
        num_years: int = 0,
    ) -> pd.DataFrame:
        """Generate an accounting report for the company.

        This function generates a report representing one of the financial
        statements for the company adjusted by the attributes passed.

        Args:
            report_type: Type of financial report to be generated. Options
                include: "assets", "cash", "current_assets",
                "non_current_assets", "liabilities", "debt",
                "current_liabilities", "non_current_liabilities",
                "liabilities_and_equity", "equity", "income",
                "earnings_per_share", "comprehensive_income",
                "changes_in_equity", "cash_flow" and "added_value".
            acc_level: Detail level to show for account codes. Options are 2,
                3, 4 or None. Defaults to None. How the values works:
                    2    -> X.YY       (show 2 levels)
                    3    -> X.YY.ZZ    (show 3 levels)
                    4    -> X.YY.ZZ.WW (show 4 levels)
                    None -> X...       (default: show all accounts)
            num_years: Number of years to include in the report. Defaults to 0
                (all years).

        Returns:
            pd.DataFrame: Generated financial report as a pandas DataFrame.

        Raises:
            ValueError: If some argument is invalid.
        """
        # Check input arguments.
        if acc_level not in {None, 2, 3, 4}:
            raise ValueError("acc_level expects None, 2, 3 or 4")

        df = self._dfc.copy()

        # Set language
        class MyDict(dict):
            """Custom dictionary class to return key if key is not found."""

            def __missing__(self, key):
                return "(pt) " + key

        if self._language == "English":
            _pten_dict = dict(language_df.values)
            _pten_dict = MyDict(_pten_dict)
            df["acc_name"] = df["acc_name"].map(_pten_dict)

        # Filter dataframe for selected acc_level
        if acc_level:
            acc_code_limit = acc_level * 3 - 2  # noqa
            df.query("acc_code.str.len() <= @acc_code_limit", inplace=True)
        """
        Filter dataframe for selected report_type (report type)
        df['acc_code'].str[0].unique() -> [1, 2, 3, 4, 5, 6, 7]
        The first part of 'acc_code' is the report type
        Table of reports correspondence:
            1 -> Balance Sheet - Assets
            2 -> Balance Sheet - Liabilities and Shareholders’ Equity
            3 -> Income
            4 -> Comprehensive Income
            5 -> Changes in Equity
            6 -> Cash Flow (Indirect Method)
            7 -> Added Value
        """
        report_types = {
            "assets": ["1"],
            "cash": ["1.01.01", "1.01.02"],
            "current_assets": ["1.01"],
            "non_current_assets": ["1.02"],
            "liabilities": ["2.01", "2.02"],
            "debt": ["2.01.04", "2.02.01"],
            "current_liabilities": ["2.01"],
            "non_current_liabilities": ["2.02"],
            "liabilities_and_equity": ["2"],
            "equity": ["2.03"],
            "income": ["3"],
            "earnings_per_share": ["3.99"],
            "comprehensive_income": ["4"],
            "changes_in_equity": ["5"],
            "cash_flow": ["6"],
            "added_value": ["7"],
        }
        acc_codes = report_types[report_type]
        expr = ""
        for count, acc_code in enumerate(acc_codes):
            if count > 0:
                expr += " or "
            expr += f'acc_code.str.startswith("{acc_code}")'
        df.query(expr, inplace=True)

        # remove earnings per share from income statment
        if report_type == "income":
            df = df[~df["acc_code"].str.startswith("3.99")]

        if report_type in {"income", "cash_flow"}:
            df = self._calculate_ttm(df)

        df.reset_index(drop=True, inplace=True)

        report_df = self._build_report(df)
        report_df.set_index(keys="acc_code", drop=True, inplace=True)
        # Show only selected years
        if num_years > 0:
            cols = report_df.columns.to_list()
            cols = cols[0:2] + cols[-num_years:]
            report_df = report_df[cols]
        # Fill NaN values with 0
        report_df.fillna(0, inplace=True)
        return report_df

    def _calculate_ttm(self, dfi: pd.DataFrame) -> pd.DataFrame:
        if self._last_annual > self._last_quarterly:
            return dfi.query('report_type == "ANNUAL"').copy()

        df1 = dfi.query("period_end == @self._last_quarterly").copy()
        df1.query("period_begin == period_begin.min()", inplace=True)

        df2 = dfi.query("period_reference == @self._last_quarterly").copy()
        df2.query("period_begin == period_begin.min()", inplace=True)
        df2["acc_value"] = -df2["acc_value"]

        df3 = dfi.query("period_end == @self._last_annual").copy()

        df_ttm = (
            pd.concat([df1, df2, df3], ignore_index=True)[["acc_code", "acc_value"]]
            .groupby(by="acc_code")
            .sum()
            .reset_index()
        )
        df1.drop(columns="acc_value", inplace=True)
        df_ttm = pd.merge(df1, df_ttm)
        df_ttm["report_type"] = "QUARTERLY"
        df_ttm["period_begin"] = self._last_quarterly - pd.DateOffset(years=1)

        df_annual = dfi.query('report_type == "ANNUAL"').copy()

        return pd.concat([df_annual, df_ttm], ignore_index=True)

    def custom_report(
        self,
        acc_list: list[str],
        num_years: int = 0,
    ) -> pd.DataFrame:
        """Generate a financial report from custom list of accounting codes

        Args:
            acc_list: A list of strings containg accounting codes to be used
                in the report
            num_years: Select how many years to show in the report.
                Defaults to 0 (show all years)

        Returns:
            pd.DataFrame: Generated financial report as a pandas DataFrame.

        Raises:
            ValueError: If some argument is invalid.
        """
        df_as = self.report("assets")
        df_le = self.report("liabilities_and_equity")
        df_is = self.report("income")
        df_cf = self.report("cash_flow")
        dfo = pd.concat([df_as, df_le, df_is, df_cf]).query("acc_code == @acc_list")
        # Show only selected years
        if num_years > 0:
            cols = dfo.columns.to_list()
            cols = cols[0:2] + cols[-num_years:]
            dfo = dfo[cols]
        return dfo

    @staticmethod
    def _prior_values(s: pd.Series, is_prior: bool) -> pd.Series:
        """Shift row to the right in order to obtain series previous values"""
        if is_prior:
            arr = s.iloc[:-1].values
            return np.append(np.nan, arr)
        else:
            return s

    def indicators(self, num_years: int = 0, is_prior: bool = True) -> pd.DataFrame:
        """Calculate the company main operating indicators.

        Args:
            num_years: Number of years to consider for calculation. If 0, use
                all available years. Defaults to 0.
            is_prior: Divide return measurements by book values from the end of
                the prior year (see Damodaran reference). Defaults to True.

        Returns:
            pd.DataFrame: Dataframe containing calculated financial indicators.

        References:
            [1] Aswath Damodaran, "Return on Capital (ROC), Return on Invested
                Capital (ROIC) and Return on Equity (ROE): Measurement and
                Implications.", 2007,
                https://people.stern.nyu.edu/adamodar/pdfoles/papers/returnmeasures.pdf
                https://people.stern.nyu.edu/adamodar/New_Home_Page/datafile/variable.htm
        """
        df_as = self.report("assets")
        df_le = self.report("liabilities_and_equity")
        df_in = self.report("income")
        df_cf = self.report("cash_flow")
        df = pd.concat([df_as, df_le, df_in, df_cf]).drop(
            columns=["acc_fixed", "acc_name"]
        )
        # Calculate indicators series
        revenues = df.loc["3.01"]
        gross_profit = df.loc["3.03"]
        ebit = df.loc["3.05"]
        ebt = df.loc["3.07"]
        effective_tax = df.loc["3.08"]
        depreciation_amortization = df.loc["6.01.01.04"]
        ebitda = ebit + depreciation_amortization
        operating_cash_flow = df.loc["6.01"]
        # capex = df.loc["6.02"]
        net_income = df.loc["3.11"]
        total_assets = df.loc["1"]
        total_assets_p = self._prior_values(total_assets, is_prior)
        equity = df.loc["2.03"]
        equity_p = self._prior_values(equity, is_prior)
        total_cash = df.loc["1.01.01"] + df.loc["1.01.02"]
        current_assets = df.loc["1.01"]
        current_liabilities = df.loc["2.01"]
        working_capital = current_assets - current_liabilities
        total_debt = df.loc["2.01.04"] + df.loc["2.02.01"]
        net_debt = total_debt - total_cash
        invested_capital = total_debt + equity - total_cash
        invested_capital_p = self._prior_values(invested_capital, is_prior)

        # Output Dataframe (dfo)
        dfo = pd.DataFrame(columns=df.columns)
        dfo.loc["revenues"] = revenues
        dfo.loc["operating_cash_flow"] = operating_cash_flow
        # dfo.loc["capex"] = capex
        dfo.loc["ebitda"] = ebitda
        dfo.loc["ebit"] = ebit
        dfo.loc["ebt"] = ebt
        dfo.loc["effective_tax_rate"] = -1 * effective_tax / ebt
        dfo.loc["net_income"] = net_income
        dfo.loc["total_cash"] = total_cash
        dfo.loc["total_debt"] = total_debt
        dfo.loc["net_debt"] = net_debt
        dfo.loc["working_capital"] = working_capital
        dfo.loc["invested_capital"] = invested_capital
        dfo.loc["return_on_assets"] = ebit * (1 - self._tax_rate) / total_assets_p
        dfo.loc["return_on_capital"] = ebit * (1 - self._tax_rate) / invested_capital_p
        dfo.loc["return_on_equity"] = net_income / equity_p
        dfo.loc["gross_margin"] = gross_profit / revenues
        dfo.loc["ebitda_margin"] = ebitda / revenues
        dfo.loc["pre_tax_operating_margin"] = ebit / revenues
        dfo.loc["after_tax_operating_margin"] = ebit * (1 - self._tax_rate) / revenues
        dfo.loc["net_margin"] = net_income / revenues

        dfo.index.name = "Company Financial Indicators"
        # Show only the selected number of years
        if num_years > 0:
            dfo = dfo[dfo.columns[-num_years:]]
        return dfo
