#!/usr/bin/python -tt
import xlrd
import csv
import os.path
import datetime
import bFunctions as bF
import ySQL
import zQueries
import cEmail


# XLS process file data
def process_xls_data_file(businessdate, macro_cntrprty_id, file_data):

    filepath = bF.get_filepath(businessdate, macro_cntrprty_id, file_data)

    if os.path.isfile(filepath):
        print 'Getting', macro_cntrprty_id + ',', file_data, 'data for', businessdate.strftime('%b %d, %Y'), '\n' + filepath
        workbook = xlrd.open_workbook(filepath)
        worksheet = workbook.sheet_by_index(0)
        num_rows = worksheet.nrows - 1

        # ~~ Reset values for business day ~~ #
        ySQL.send_sql(zQueries.sql_reset_balancemanagement(businessdate, macro_cntrprty_id), 'OPDS')

        # Loop through data to find variables
        for r in range(bF.get_enum(macro_cntrprty_id, 'r_forstart', file_data), num_rows):

            # reset variables
            fund = 'NA'
            sub_acct = 'NA'
            account_name = 'NA'
            trader = 'NA'
            trader_id = 'NA'
            long_mkt_value_usd = 0
            # long_mkt_value_local = 0
            short_mkt_value_usd = 0
            short_mkt_value_local = 0
            settle_date_cash_usd = 0
            # settle_date_cash_local = 0
            cash_ex_short_local = 0
            cash_ex_short_usd = 0

            # Get acct
            cntrprty_subacct_num = worksheet.cell_value(r, bF.get_enum(macro_cntrprty_id, 'c_macroid', file_data))

            # do not process
            if macro_cntrprty_id == 'MS' and file_data == 'SMV':
                # skip accounts with 052 and 05A
                if cntrprty_subacct_num[:3] == '052' or cntrprty_subacct_num[:3] == '05A':
                    continue
                # skip Asset Class = 'Cash Securities' AND L/S = 'L' or Asset Class = 'Cash'
                elif not ((unicode.upper(worksheet.cell_value(r, 2)) == 'CASH SECURITIES' and unicode.upper(worksheet.cell_value(r, 3)) == 'L')
                          or unicode.upper(worksheet.cell_value(r, 2)) == 'CASH'):
                    continue

            # grab fsa info from db
            results = bF.get_fsa_data(cntrprty_subacct_num, macro_cntrprty_id, file_data)
            if results:
                fund = results[0][0]
                sub_acct = results[0][1]
                account_name = results[0][3]
                trader = results[0][6]
                trader_id = results[0][7]

            ccy = worksheet.cell_value(r, bF.get_enum(macro_cntrprty_id, 'c_ccy', file_data))
            fx_rate = ySQL.get_sql_fetchone(zQueries.sql_fxrate(businessdate, ccy), 'OPDS')
            if macro_cntrprty_id == 'MS' and file_data == 'SMV':
                if unicode.upper(worksheet.cell_value(r, 2)) == 'CASH SECURITIES' and unicode.upper(worksheet.cell_value(r, 3)) == 'L':
                    long_mkt_value_usd = worksheet.cell_value(r, bF.get_enum(macro_cntrprty_id, 'c_longusd', file_data)) or 0
                elif unicode.upper(worksheet.cell_value(r, 2)) == 'CASH':
                    settle_date_cash_usd = worksheet.cell_value(r, bF.get_enum(macro_cntrprty_id, 'c_settleusd', file_data)) or 0
            else:
                long_mkt_value_usd = worksheet.cell_value(r, bF.get_enum(macro_cntrprty_id, 'c_longusd', file_data)) or 0
                settle_date_cash_usd = worksheet.cell_value(r, bF.get_enum(macro_cntrprty_id, 'c_settleusd', file_data)) or 0
                short_mkt_value_usd = abs(worksheet.cell_value(r, bF.get_enum(macro_cntrprty_id, 'c_shortusd', file_data))) or 0
                short_mkt_value_local = abs(short_mkt_value_usd / fx_rate)

            long_mkt_value_local = long_mkt_value_usd / fx_rate
            settle_date_cash_local = settle_date_cash_usd / fx_rate

            # print (businessdate, macro_cntrprty_id, fund, sub_acct, ccy, cntrprty_subacct_num, account_name,
            #        long_mkt_value_local, long_mkt_value_usd, short_mkt_value_local, short_mkt_value_usd,
            #        settle_date_cash_local, settle_date_cash_usd, cash_ex_short_local, cash_ex_short_usd,
            #        fx_rate, trader, trader_id)

            # ~~ merge into operations.balance_management ~~ #
            ySQL.send_sql(zQueries.sql_merge_balancemanagement(businessdate, macro_cntrprty_id, fund, sub_acct,
                                                               ccy, cntrprty_subacct_num, account_name,
                                                               long_mkt_value_local, long_mkt_value_usd,
                                                               short_mkt_value_local, short_mkt_value_usd,
                                                               settle_date_cash_local, settle_date_cash_usd,
                                                               cash_ex_short_local, cash_ex_short_usd,
                                                               fx_rate, trader, trader_id, file_data), 'OPDS')

    else:
        print 'File not found:', filepath
        return filepath


# XLS process file data
def process_csv_data_file(businessdate, macro_cntrprty_id, file_data):

    filepath = bF.get_filepath(businessdate, macro_cntrprty_id, file_data)

    if os.path.isfile(filepath):
        print 'Getting', macro_cntrprty_id + ',', file_data, 'data for', businessdate.strftime('%b %d, %Y'), '\n' + filepath

        #  ## Reset values for business day if first file in the process ## #
        if (macro_cntrprty_id == 'CS' and file_data == 'MARKET') or (macro_cntrprty_id == 'CT' and file_data == 'SD'):
            ySQL.send_sql(zQueries.sql_reset_balancemanagement(businessdate, macro_cntrprty_id), 'OPDS')

        with open(filepath, 'rU') as csvDataFile:
            reader = csv.reader(csvDataFile)
            next(reader, None)
            # Loop through data to find variables
            for r in reader:
                # skip blank lines
                if not r:
                    continue
                # print r
                # skip lines with RV or RP
                if macro_cntrprty_id == 'CT' and file_data == 'SD' and (str.upper(r[18]) == 'RV' or str.upper(r[18]) == 'RP'):
                    continue
                # skip line that are not marked as MARGIN or SHORT
                elif macro_cntrprty_id == 'CT' and file_data == 'HOLD' and (str.upper(r[21]) != 'MARGIN' and str.upper(r[21]) != 'SHORT'):
                    continue
                # if it has more than 2 index in data set
                elif macro_cntrprty_id == 'MS' and file_data == 'INT' and len(r) <= 2:
                    continue
                # skip accounts with 052 and 05A
                elif macro_cntrprty_id == 'MS' and file_data == 'INT' and (r[2][:3] == '052' or r[2][:3] == '05A' or r[4] != businessdate.strftime('%m/%d/%Y')):
                    continue

                # reset variables
                fund = 'NA'
                sub_acct = 'NA'
                account_name = 'NA'
                trader = 'NA'
                trader_id = 'NA'
                long_mkt_value_usd = 0
                long_mkt_value_local = 0
                short_mkt_value_usd = 0
                short_mkt_value_local = 0
                settle_date_cash_usd = 0
                settle_date_cash_local = 0
                cash_ex_short_local = 0
                cash_ex_short_usd = 0

                # Get acct
                if macro_cntrprty_id == 'CS' and file_data == 'MARKET':
                    cntrprty_subacct_num = str.strip(r[bF.get_enum(macro_cntrprty_id, 'c_macroid', file_data)].split("/")[1])
                else:
                    cntrprty_subacct_num = r[bF.get_enum(macro_cntrprty_id, 'c_macroid', file_data)]
                # correct cntrprty file issues
                if macro_cntrprty_id == 'CS' and cntrprty_subacct_num == '7363V0':
                    cntrprty_subacct_num = '7363V0C'

                # grab fsa info from db
                results = bF.get_fsa_data(cntrprty_subacct_num, macro_cntrprty_id, file_data)
                if results:
                    fund = results[0][0]
                    sub_acct = results[0][1]
                    account_name = results[0][3]
                    trader = results[0][6]
                    trader_id = results[0][7]

                ccy = r[bF.get_enum(macro_cntrprty_id, 'c_ccy', file_data)]
                if macro_cntrprty_id == 'MS' and file_data == 'INT':
                    fx_rate = ySQL.get_sql_fetchone(zQueries.sql_fxrate(businessdate, ccy), 'OPDS')
                else:
                    fx_rate = r[bF.get_enum(macro_cntrprty_id, 'c_fx', file_data)]

                if macro_cntrprty_id == 'CS' and file_data == 'MARKET':
                    if str.upper(r[1]) == 'SECURITIES' and float(r[bF.get_enum(macro_cntrprty_id, 'c_qty', file_data)]) > 0:
                        long_mkt_value_usd = r[bF.get_enum(macro_cntrprty_id, 'c_longusd', file_data)] or 0
                        long_mkt_value_local = r[bF.get_enum(macro_cntrprty_id, 'c_longlocal', file_data)] or 0
                    elif str.upper(r[1]) == 'SECURITIES' and str.upper(r[3]) == 'SHORT' and float(r[bF.get_enum(macro_cntrprty_id, 'c_qty', file_data)]) < 0:
                        short_mkt_value_usd = abs(float(r[bF.get_enum(macro_cntrprty_id, 'c_shortusd', file_data)])) or 0
                        short_mkt_value_local = abs(float(r[bF.get_enum(macro_cntrprty_id, 'c_shortlocal', file_data)])) or 0
                elif macro_cntrprty_id == 'CS' and file_data == 'CASH':
                    settle_date_cash_usd = float(r[bF.get_enum(macro_cntrprty_id, 'c_settleusd', file_data)]) or 0
                    settle_date_cash_local = float(r[bF.get_enum(macro_cntrprty_id, 'c_settlelocal', file_data)]) or 0
                elif macro_cntrprty_id == 'CT' and file_data == 'SD':
                    if float(r[bF.get_enum(macro_cntrprty_id, 'c_qty', file_data)]) > 0:
                        long_mkt_value_usd = abs(float(r[bF.get_enum(macro_cntrprty_id, 'c_longusd', file_data)])) or 0
                        long_mkt_value_local = abs(float(r[bF.get_enum(macro_cntrprty_id, 'c_longlocal', file_data)])) or 0
                    elif float(r[bF.get_enum(macro_cntrprty_id, 'c_qty', file_data)]) < 0:
                        short_mkt_value_usd = abs(float(r[bF.get_enum(macro_cntrprty_id, 'c_shortusd', file_data)])) or 0
                        short_mkt_value_local = abs(float(r[bF.get_enum(macro_cntrprty_id, 'c_shortlocal', file_data)])) or 0
                elif macro_cntrprty_id == 'CT' and file_data == 'HOLD':
                    if str.upper(r[21]) == 'MARGIN':
                        long_mkt_value_usd = abs(float(r[bF.get_enum(macro_cntrprty_id, 'c_longusd', file_data)])) or 0
                        long_mkt_value_local = abs(float(r[bF.get_enum(macro_cntrprty_id, 'c_longlocal', file_data)])) or 0
                    elif str.upper(r[21]) == 'SHORT':
                        short_mkt_value_usd = abs(float(r[bF.get_enum(macro_cntrprty_id, 'c_shortusd', file_data)])) or 0
                        short_mkt_value_local = abs(float(r[bF.get_enum(macro_cntrprty_id, 'c_shortlocal', file_data)])) or 0
                elif macro_cntrprty_id == 'CT' and file_data == 'BAL':
                    settle_date_cash_usd = float(r[bF.get_enum(macro_cntrprty_id, 'c_settleusd', file_data)]) or 0
                    settle_date_cash_local = float(r[bF.get_enum(macro_cntrprty_id, 'c_settlelocal', file_data)]) or 0
                elif macro_cntrprty_id == 'MS' and file_data == 'INT':
                    if ccy == 'USD':
                        short_mkt_value_usd = abs(float(r[bF.get_enum(macro_cntrprty_id, 'c_shortusd', file_data)])) or 0
                        short_mkt_value_local = abs(short_mkt_value_usd / fx_rate)
                    else:
                        short_mkt_value_local = abs(float(r[bF.get_enum(macro_cntrprty_id, 'c_2shortusd', file_data)])) or 0
                        short_mkt_value_usd = abs(short_mkt_value_local * fx_rate)


                # print (businessdate, macro_cntrprty_id, fund, sub_acct, ccy, cntrprty_subacct_num, account_name,
                #        long_mkt_value_local, long_mkt_value_usd, short_mkt_value_local, short_mkt_value_usd,
                #        settle_date_cash_local, settle_date_cash_usd, cash_ex_short_local, cash_ex_short_usd,
                #        fx_rate, trader, trader_id)

                #   ~~ merge into operations.balance_management ~~ #
                ySQL.send_sql(zQueries.sql_merge_balancemanagement(businessdate, macro_cntrprty_id, fund, sub_acct,
                                                                   ccy, cntrprty_subacct_num, account_name,
                                                                   long_mkt_value_local, long_mkt_value_usd,
                                                                   short_mkt_value_local, short_mkt_value_usd,
                                                                   settle_date_cash_local, settle_date_cash_usd,
                                                                   cash_ex_short_local, cash_ex_short_usd,
                                                                   fx_rate, trader, trader_id, file_data), 'OPDS')

    else:
        print 'File not found:', filepath
        return filepath


# Main Definition
def main():
    businessdate = ySQL.get_sql_fetchone(zQueries.sql_businessdate(), 'OPDS')
    t0 = datetime.datetime.today()
    print 'Process started at', t0

    # Process GS Files
    gs = process_xls_data_file(businessdate, 'GS', 'FILE')
    print gs
    print 'GS file complete', datetime.datetime.today() - t0

    # Process CS Files
    cs_market = process_csv_data_file(businessdate, 'CS', 'MARKET')
    print 'CS market complete', datetime.datetime.today()-t0
    cs_cash = process_csv_data_file(businessdate, 'CS', 'CASH')
    print 'CS cash complete', datetime.datetime.today()-t0

    # Process CITI Files
    citi_sd = process_csv_data_file(businessdate, 'CT', 'SD')
    print 'CITI SD complete', datetime.datetime.today()-t0
    citi_hold = process_csv_data_file(businessdate, 'CT', 'HOLD')
    print 'CITI HOLD complete', datetime.datetime.today()-t0
    citi_bal = process_csv_data_file(businessdate, 'CT', 'BAL')
    print 'CITI BAL complete', datetime.datetime.today() - t0

    # Process MS Files
    ms_smv = process_xls_data_file(businessdate, 'MS', 'SMV')
    print 'MS SD complete', datetime.datetime.today()-t0
    ms_int = process_csv_data_file(businessdate, 'MS', 'INT')
    print 'MS INT complete', datetime.datetime.today()-t0

    # ~~~~~~~~~~~~~~~change to only use businessdate after finished
    #  Update Cash Ex Short
    ySQL.send_sql(zQueries.sql_update_cashexshort_balancemanagement(businessdate, 'MS'), 'OPDS')

    # Email Issues
    cEmail.compile_email('#@#.com', '#@#.com, '#@#.com',
                         [gs,
                          cs_market, cs_cash,
                          citi_sd, citi_hold, citi_bal,
                          ms_smv, ms_int
                          ], businessdate)

    # Total time to process
    print 'Time to complete', datetime.datetime.today()-t0


# Main call
if __name__ == '__main__':
    main()
