#!/usr/bin/python -tt
import os.path
import datetime
import ySQL
import zQueries
import glob
import zipfile


# unzip folder
def unzip_folder(path_to_zip_file, directory_to_extract_to):
    zip_ref = zipfile.ZipFile(path_to_zip_file, 'r')
    zip_ref.extractall(directory_to_extract_to)
    zip_ref.close()


# Return File information
def get_filepath(businessdate, macro_cntrprty_id, file_data):
    # paths
    bal_man_path = r'\\cnjfile00\opercommon\Incoming From FTP\Balance Management'
    broker_bal_path = r'\\cnjfile00\operations\Checkout Automation\Broker Balance Data'
    margin_path = r'\\cnjfile00\opercommon\Incoming From FTP\Margin Data'
    # files
    gs_file_base = 'SRPB_197602_1200129169_Settle_Date_Expo_302238_695349_yyyymmdd.xls'
    cs_market_base = 'SDPositions&CashbyCCY_yyyymmdd.csv'
    cs_cash_base = 'NYCashBySD_yyyymmdd.csv'
    citi_sd_base = 'OCAXTON_PF_SDPosDtl_LE263615_yyyymmdd.csv'
    citi_hold_base = 'OCAXTON_PF_Holdings_EX100157_263615_yyyymmdd.csv'
    citi_bal_base = 'OCAXTON_PF_Balances_EX100158_263615_yyyymmdd.csv'
    ms_zip_file = 'Caxton_CustomTDCash_yyyymmdd.zip'
    ms_smv_base = 'TN000001476.PQN2219X.9373641.yyyymmdd.*.xls'
    ms_int_base = 'MS_DailyIntbyTraderin106mx_yyyymmdd.txt'

    if macro_cntrprty_id == 'GS':
        filepath = bal_man_path + '\\' + gs_file_base.replace('yyyymmdd', (businessdate + datetime.timedelta(days=1)).strftime('%Y%m%d'))
        sunday_filepath = bal_man_path + '\\' + gs_file_base.replace('yyyymmdd', (businessdate + datetime.timedelta(days=2)).strftime('%Y%m%d'))
        monday_filepath = bal_man_path + '\\' + gs_file_base.replace('yyyymmdd', (businessdate + datetime.timedelta(days=3)).strftime('%Y%m%d'))
    elif macro_cntrprty_id == 'CS' and file_data == 'MARKET':
        filepath = bal_man_path + '\\' + cs_market_base.replace('yyyymmdd', businessdate.strftime('%Y%m%d'))
        sunday_filepath = bal_man_path + '\\' + cs_market_base.replace('yyyymmdd', (businessdate + datetime.timedelta(days=2)).strftime('%Y%m%d'))
        monday_filepath = bal_man_path + '\\' + cs_market_base.replace('yyyymmdd', (businessdate + datetime.timedelta(days=3)).strftime('%Y%m%d'))
    elif macro_cntrprty_id == 'CS' and file_data == 'CASH':
        filepath = broker_bal_path + '\\' + cs_cash_base.replace('yyyymmdd', (businessdate + datetime.timedelta(days=1)).strftime('%Y%m%d'))
        sunday_filepath = broker_bal_path + '\\' + cs_cash_base.replace('yyyymmdd', (businessdate + datetime.timedelta(days=2)).strftime('%Y%m%d'))
        monday_filepath = broker_bal_path + '\\' + cs_cash_base.replace('yyyymmdd', (businessdate + datetime.timedelta(days=3)).strftime('%Y%m%d'))
    elif macro_cntrprty_id == 'CT' and file_data == 'SD':
        filepath = margin_path + '\\' + citi_sd_base.replace('yyyymmdd', businessdate.strftime('%Y%m%d'))
        sunday_filepath = margin_path + '\\' + citi_sd_base.replace('yyyymmdd', (businessdate + datetime.timedelta(days=2)).strftime('%Y%m%d'))
        monday_filepath = margin_path + '\\' + citi_sd_base.replace('yyyymmdd', (businessdate + datetime.timedelta(days=3)).strftime('%Y%m%d'))
    elif macro_cntrprty_id == 'CT' and file_data == 'HOLD':
        filepath = margin_path + '\\' + citi_hold_base.replace('yyyymmdd', businessdate.strftime('%Y%m%d'))
        sunday_filepath = margin_path + '\\' + citi_hold_base.replace('yyyymmdd', (businessdate + datetime.timedelta(days=2)).strftime('%Y%m%d'))
        monday_filepath = margin_path + '\\' + citi_hold_base.replace('yyyymmdd', (businessdate + datetime.timedelta(days=3)).strftime('%Y%m%d'))
    elif macro_cntrprty_id == 'CT' and file_data == 'BAL':
        filepath = margin_path + '\\' + citi_bal_base.replace('yyyymmdd', businessdate.strftime('%Y%m%d'))
        sunday_filepath = margin_path + '\\' + citi_bal_base.replace('yyyymmdd', (businessdate + datetime.timedelta(days=2)).strftime('%Y%m%d'))
        monday_filepath = margin_path + '\\' + citi_bal_base.replace('yyyymmdd', (businessdate + datetime.timedelta(days=3)).strftime('%Y%m%d'))
    elif macro_cntrprty_id == 'MS' and file_data == 'SMV':
        # unzip folder to directory
        unzip_folder(bal_man_path + '\\' + ms_zip_file.replace('yyyymmdd', (businessdate + datetime.timedelta(days=1)).strftime('%Y%m%d')), bal_man_path + '\\')
        # using wildcard requires a list to be pulled and tested before setting variable
        filepaths = glob.glob(bal_man_path + '\\' + ms_smv_base.replace('yyyymmdd', businessdate.strftime('%Y%m%d')))
        sunday_filepaths = glob.glob(bal_man_path + '\\' + ms_smv_base.replace('yyyymmdd', (businessdate + datetime.timedelta(days=2)).strftime('%Y%m%d')))
        monday_filepaths = glob.glob(bal_man_path + '\\' + ms_smv_base.replace('yyyymmdd', (businessdate + datetime.timedelta(days=3)).strftime('%Y%m%d')))
        if filepaths:
            filepath = str(filepaths[0])
        else:
            filepath = None
        if sunday_filepaths:
            sunday_filepath = str(sunday_filepaths[0])
        else:
            sunday_filepath = None
        if monday_filepaths:
            monday_filepath = str(monday_filepaths[0])
        else:
            monday_filepath = None
    elif macro_cntrprty_id == 'MS' and file_data == 'INT':
        filepath = broker_bal_path + '\\' + ms_int_base.replace('yyyymmdd', (businessdate + datetime.timedelta(days=1)).strftime('%Y%m%d'))
        sunday_filepath = broker_bal_path + '\\' + ms_int_base.replace('yyyymmdd', (businessdate + datetime.timedelta(days=2)).strftime('%Y%m%d'))
        monday_filepath = broker_bal_path + '\\' + ms_int_base.replace('yyyymmdd', (businessdate + datetime.timedelta(days=3)).strftime('%Y%m%d'))
    else:
        filepath = None
        sunday_filepath = None
        monday_filepath = None

    # Validate file path. If day is friday check for a drop on monday and sunday
    if not os.path.isfile(filepath) and (businessdate.isoweekday == 5 and os.path.isfile(sunday_filepath)):
        filepath = sunday_filepath
    elif not os.path.isfile(filepath) and (businessdate.isoweekday == 5 and os.path.isfile(monday_filepath)):
        filepath = monday_filepath

    return filepath


# Get relevant sub_fund_account information
def get_fsa_data(cntrprty_subacct_num, macro_cntrprty_id, file_data):
    # fund=0, sub_acct=1, account_name = 3, trader = 6, trader_id = 7

    # Active
    results = ySQL.get_sql_fetchall(zQueries.sql_subacct(cntrprty_subacct_num, 'Y', macro_cntrprty_id, file_data), 'OPDS')
    if bool(results) is False:
        # Active - 1
        results = ySQL.get_sql_fetchall(zQueries.sql_subacct(cntrprty_subacct_num[:-1], 'Y', macro_cntrprty_id, file_data), 'OPDS')
        if bool(results) is False:
            # Inactive
            results = ySQL.get_sql_fetchall(zQueries.sql_subacct(cntrprty_subacct_num, 'N', macro_cntrprty_id, file_data), 'OPDS')
            if bool(results) is False:
                # Inactive - 1
                results = ySQL.get_sql_fetchall(zQueries.sql_subacct(cntrprty_subacct_num[:-1], 'N', macro_cntrprty_id, file_data), 'OPDS')

    return results


# Get file specific variables
def get_enum(macro_cntrprty_id, variable, file_data):
    if macro_cntrprty_id == 'GS':
        if variable == 'r_forstart':
            return 8
        elif variable == 'c_macroid':
            return 0
        elif variable == 'c_ccy':
            return 2
        elif variable == 'c_longusd':
            return 4
        elif variable == 'c_shortusd':
            return 6
        elif variable == 'c_settleusd':
            return 9
        else:
            return None
    elif macro_cntrprty_id == 'CS':
        if variable == 'c_macroid':
            return 0
        elif variable == 'c_ccy':
            if file_data == 'MARKET':
                return 7
            elif file_data == 'CASH':
                return 4
        elif variable == 'c_fx':
            if file_data == 'MARKET':
                return 10
            elif file_data == 'CASH':
                return 6
        elif variable == 'c_shortusd' or variable == 'c_longusd':
            return 12
        elif variable == 'c_shortlocal' or variable == 'c_longlocal':
            return 11
        elif variable == 'c_settleusd':
            return 7
        elif variable == 'c_settlelocal':
            return 5
        elif variable == 'c_qty':
            return 4
        else:
            return None
    elif macro_cntrprty_id == 'CT':
        if variable == 'c_macroid':
            return 0
        elif variable == 'c_ccy':
            if file_data == 'SD':
                return 16
            elif file_data == 'HOLD':
                return 3
            elif file_data == 'BAL':
                return 2
        elif variable == 'c_fx':
            if file_data == 'SD':
                return 28
            elif file_data == 'HOLD':
                return 6
            elif file_data == 'BAL':
                return 4
        elif variable == 'c_shortusd' or variable == 'c_longusd':
            if file_data == 'SD':
                return 29
            elif file_data == 'HOLD':
                return 30
        elif variable == 'c_shortlocal' or variable == 'c_longlocal':
            if file_data == 'SD':
                return 25
            elif file_data == 'HOLD':
                return 29
        elif variable == 'c_settleusd':
            return 12
        elif variable == 'c_settlelocal':
            return 8
        elif variable == 'c_qty':
            return 25
        else:
            return None
    elif macro_cntrprty_id == 'MS':
        if variable == 'r_forstart':
            return 2
        elif variable == 'c_macroid':
            if file_data == 'SMV':
                return 0
            elif file_data == 'INT':
                return 2
        elif variable == 'c_ccy':
            if file_data == 'SMV':
                return 1
            elif file_data == 'INT':
                return 3
        elif variable == 'c_longusd':
            return 4
        elif variable == 'c_shortusd':
            return 5
        elif variable == 'c_2shortusd':
            return 8
        elif variable == 'c_settleusd':
            return 4
        else:
            return None
    else:
        return None

