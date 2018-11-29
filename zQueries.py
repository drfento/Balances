#!/usr/bin/python -tt


# Business Date
def sql_businessdate():
    SSQL = "SELECT business_date FROM odstrade.control"

    return SSQL


# Sub Fund Account
def sql_subacct(cntrprty_subacct_num, active_yn, macro_cntrprty_id, file_data):
    SSQL = "  SELECT F.FUND_ID, F.SUB_ACCT_ID, F.CNTRPRTY_SUBACCT_NUM, F.NAME, MULTI_CSN.CSNCOUNT,  "
    SSQL = SSQL + "  CASE WHEN MULTI_CSN.CSNCOUNT IS NOT NULL AND F.SUB_ACCT_ID LIKE '%SMSPB' THEN F.SUB_ACCT_ID ELSE '' END AS PB_ACCT,   "
    SSQL = SSQL + "  TR.LAST_NAME TRADER, TR.TRADER_ID   "
    SSQL = SSQL + "FROM ODSTRADE.FUND_SUB_ACCOUNT F    "
    SSQL = SSQL + "LEFT JOIN ODSTRADE.GL_TRADER G ON G.GL_TRADER=F.GL_TRADER "
    SSQL = SSQL + "LEFT JOIN ODSTRADE.TRADER TR ON TR.TRADER_ID=G.TRADER_ID "
    SSQL = SSQL + "LEFT JOIN (SELECT DISTINCT REPLACE(CNTRPRTY_SUBACCT_NUM,'-','') CSN, COUNT(REPLACE(CNTRPRTY_SUBACCT_NUM,'-','')) CSNCOUNT  "
    SSQL = SSQL + "        FROM ODSTRADE.FUND_SUB_ACCOUNT  "
    SSQL = SSQL + "         WHERE  1=1 "
    SSQL = SSQL + "           AND (FUND_ID in (SELECT FUND_ID FROM OPERATIONS.VW_FUND_ACTIVE) or FUND_ID = 'ZH')  "
    SSQL = SSQL + "           AND ACTIVE_STATUS = '" + active_yn + "'  "
    SSQL = SSQL + "        GROUP BY CNTRPRTY_SUBACCT_NUM  "
    SSQL = SSQL + "        HAVING COUNT(REPLACE(CNTRPRTY_SUBACCT_NUM,'-','')) > 1) MULTI_CSN ON MULTI_CSN.CSN = REPLACE(F.CNTRPRTY_SUBACCT_NUM,'-','')  "
    SSQL = SSQL + "WHERE   1=1 "
    SSQL = SSQL + "   AND (F.FUND_ID in (SELECT FUND_ID FROM OPERATIONS.VW_FUND_ACTIVE) or F.FUND_ID = 'ZH')  "
    SSQL = SSQL + "   AND F.ACTIVE_STATUS = '" + active_yn + "'    "
    if macro_cntrprty_id == 'GS' or (macro_cntrprty_id == 'MS' and file_data == 'SMV'):
        SSQL = SSQL + "   AND REPLACE(F.CNTRPRTY_SUBACCT_NUM,'-','') = '" + unicode.replace(cntrprty_subacct_num, "-", "") + "' "
    else:
        SSQL = SSQL + "   AND REPLACE(F.CNTRPRTY_SUBACCT_NUM,'-','') = '" + str.replace(cntrprty_subacct_num, "-", "") + "' "
    SSQL = SSQL + "ORDER BY F.CNTRPRTY_SUBACCT_NUM, PB_ACCT, F.SUB_ACCT_ID  "

    return SSQL


# Missing cntrprty_subacct_num
def sql_get_missing_cntrprty(businessdate):
    SSQL = " Select CNTRPRTY_SUBACCT_NUM "
    SSQL = SSQL + " From OPERATIONS.BALANCE_MANAGEMENT  "
    SSQL = SSQL + " Where 1=1    "
    SSQL = SSQL + " and BUSINESS_DATE = '" + businessdate.strftime('%d-%b-%Y') + "'   "
    SSQL = SSQL + " and FUND_ID not in (SELECT FUND_ID FROM OPERATIONS.VW_FUND_ACTIVE) "

    return SSQL

# FX Rate
def sql_fxrate(businessdate, ccy):
    SSQL = " select FX_SPOT_MID_4_CAL  "
    SSQL = SSQL + "from Odstrade.MV_EOD_FX_SPOT_HIST "
    SSQL = SSQL + "Where 1=1 "
    SSQL = SSQL + "    and BUS_DATE = '" + businessdate.strftime('%d-%b-%Y') + "' "
    SSQL = SSQL + "    and CURRENCY_CODE = ( SELECT inst_id "
    SSQL = SSQL + "                         FROM odstrade.instrument_cross_reference  "
    SSQL = SSQL + "                         WHERE 1 = 1 "
    SSQL = SSQL + "                           AND source_inst_id = '" + ccy + "' "
    SSQL = SSQL + "                           AND market_data_source_id = 'ISO' "
    SSQL = SSQL + "                           AND  inst_id not in ('US$') "
    SSQL = SSQL + "                           AND LENGTH(inst_id) < 4 )  "

    return SSQL


# Balance Management data
def sql_get_balancemanagement(businessdate, macro_cntrprty_id, ccy, fund, cntrprty_subacct_num):
    SSQL = " SELECT SHORT_MARKET_VALUE_LOCAL, SHORT_MARKET_VALUE_USD, LONG_MARKET_VALUE_LOCAL, LONG_MARKET_VALUE_USD   "
    SSQL = SSQL + "FROM OPERATIONS.BALANCE_MANAGEMENT  "
    SSQL = SSQL + "Where 1=1  "
    SSQL = SSQL + " and macro_cntrprty_id = '" + macro_cntrprty_id + "'"
    SSQL = SSQL + " and BUSINESS_DATE = '" + businessdate.strftime('%d-%b-%Y') + "' "
    SSQL = SSQL + " and CNTRPRTY_SUBACCT_NUM = '" + str.replace(cntrprty_subacct_num, "-", "") + "' "
    SSQL = SSQL + " and FUND_ID = '" + fund + "' "
    SSQL = SSQL + " and CCY = '" + ccy + "' "

    return SSQL


# Update Balance Management Cash_Ex
def sql_update_cashexshort_balancemanagement(businessdate, macro_cntrprty_id):
    SSQL = " UPDATE OPERATIONS.BALANCE_MANAGEMENT "
    SSQL = SSQL + "SET    CASH_EX_SHORT_LOCAL = SETTLE_DATE_CASH_LOCAL  - SHORT_MARKET_VALUE_LOCAL , "
    SSQL = SSQL + "       CASH_EX_SHORT_USD   = SETTLE_DATE_CASH_USD - SHORT_MARKET_VALUE_USD "
    SSQL = SSQL + "Where 1=1   "
    SSQL = SSQL + " and macro_cntrprty_id = '" + macro_cntrprty_id + "'"
    SSQL = SSQL + "and BUSINESS_DATE = '" + businessdate.strftime('%d-%b-%Y') + "'  "

    return SSQL


# Reset Balance Management
def sql_reset_balancemanagement(businessdate, macro_cntrprty_id):
    SSQL = "UPDATE operations.balance_management "
    SSQL = SSQL + " SET short_market_value_Local = 0 "
    SSQL = SSQL + "   , short_market_value_usd = 0 "
    SSQL = SSQL + "   , long_market_value_Local = 0 "
    SSQL = SSQL + "   , long_market_value_usd = 0 "
    SSQL = SSQL + "   , SETTLE_DATE_CASH_LOCAL = 0 "
    SSQL = SSQL + "   , SETTLE_DATE_CASH_USD = 0 "
    SSQL = SSQL + "   , CASH_EX_SHORT_LOCAL = 0 "
    SSQL = SSQL + "   , CASH_EX_SHORT_USD = 0 "
    SSQL = SSQL + " WHERE macro_cntrprty_id = '" + macro_cntrprty_id + "'"
    SSQL = SSQL + "   AND business_date = '" + businessdate.strftime('%d-%b-%Y') + "'"

    return SSQL


# Merge Balance Management
def sql_merge_balancemanagement(businessdate, macro_cntrprty_id, fund, sub_acct, ccy, cntrprty_subacct_num, account_name,
                                long_mkt_value_local, long_mkt_value_usd, short_mkt_value_local, short_mkt_value_usd,
                                settle_date_cash_local, settle_date_cash_usd, cash_ex_short_local, cash_ex_short_usd,
                                fx_rate, trader, trader_id, file_data):
    SSQL = " MERGE INTO operations.balance_management b "
    SSQL = SSQL + "USING (SELECT '" + businessdate.strftime('%d-%b-%Y') + "' business_date  "
    SSQL = SSQL + "                       ,'" + fund + "' fund_id "
    SSQL = SSQL + "                       , '" + sub_acct + "' sub_acct_id "
    SSQL = SSQL + "                       , '" + ccy + "' ccy "
    SSQL = SSQL + "                       , '" + cntrprty_subacct_num + "' cntrprty_subacct_num "
    SSQL = SSQL + "                       , '" + macro_cntrprty_id + "' macro_cntrprty_id "
    SSQL = SSQL + "                       , '" + account_name + "' account_name "
    SSQL = SSQL + "                       , " + str(long_mkt_value_local) + " long_market_value_local "
    SSQL = SSQL + "                       , " + str(long_mkt_value_usd) + " long_market_value_usd "
    SSQL = SSQL + "                       , " + str(short_mkt_value_local) + " short_market_value_local "
    SSQL = SSQL + "                       , " + str(short_mkt_value_usd) + " short_market_value_usd "
    SSQL = SSQL + "                       , " + str(settle_date_cash_local) + " SETTLE_DATE_CASH_LOCAL "
    SSQL = SSQL + "                       , " + str(settle_date_cash_usd) + " SETTLE_DATE_CASH_USD "
    SSQL = SSQL + "                       , " + str(cash_ex_short_local) + " CASH_EX_SHORT_LOCAL "
    SSQL = SSQL + "                       , " + str(cash_ex_short_usd) + " CASH_EX_SHORT_USD "
    SSQL = SSQL + "                       , " + str(fx_rate) + " fx_rate "
    SSQL = SSQL + "                       , '" + trader + "' TRADER "
    SSQL = SSQL + "                       , '" + trader_id + "' TRADER_ID "
    SSQL = SSQL + "            FROM DUAL) r ON (r.business_date = b.business_date AND r.fund_id = b.fund_id AND r.cntrprty_subacct_num = b.cntrprty_subacct_num AND r.ccy = b.ccy AND r.macro_cntrprty_id=b.macro_cntrprty_id) "

    SSQL = SSQL + "WHEN MATCHED THEN  "
    SSQL = SSQL + "    UPDATE SET b.long_market_value_local = b.long_market_value_local + r.long_market_value_local "
    SSQL = SSQL + "             , b.long_market_value_usd = b.long_market_value_usd + r.long_market_value_usd "

    if macro_cntrprty_id == 'MS' and file_data == 'INT':
            SSQL = SSQL + "             , b.short_market_value_local = r.short_market_value_local "
            SSQL = SSQL + "             , b.short_market_value_usd = r.short_market_value_usd "
    else:
            SSQL = SSQL + "             , b.short_market_value_local = b.short_market_value_local + r.short_market_value_local "
            SSQL = SSQL + "             , b.short_market_value_usd = b.short_market_value_usd + r.short_market_value_usd "

    SSQL = SSQL + "             , b.SETTLE_DATE_CASH_LOCAL = b.SETTLE_DATE_CASH_LOCAL + r.SETTLE_DATE_CASH_LOCAL "
    SSQL = SSQL + "             , b.SETTLE_DATE_CASH_USD = b.SETTLE_DATE_CASH_USD + r.SETTLE_DATE_CASH_USD "
    SSQL = SSQL + "             , b.CASH_EX_SHORT_LOCAL = b.CASH_EX_SHORT_LOCAL + r.CASH_EX_SHORT_LOCAL "
    SSQL = SSQL + "             , b.CASH_EX_SHORT_USD = b.CASH_EX_SHORT_USD + r.CASH_EX_SHORT_USD "

    SSQL = SSQL + "WHEN NOT MATCHED THEN "
    SSQL = SSQL + "    INSERT (business_date, macro_cntrprty_id, fund_id, sub_acct_id, ccy, cntrprty_subacct_num, account_name, long_market_value_local, long_market_value_usd, short_market_value_local, short_market_value_usd, SETTLE_DATE_CASH_LOCAL, SETTLE_DATE_CASH_USD, CASH_EX_SHORT_LOCAL, CASH_EX_SHORT_USD, fx_rate, TRADER, TRADER_ID) "
    SSQL = SSQL + "    VALUES (r.business_date, r.macro_cntrprty_id, r.fund_id, r.sub_acct_id, r.ccy, r.cntrprty_subacct_num, r.account_name, r.long_market_value_local, r.long_market_value_usd, r.short_market_value_local, r.short_market_value_usd, r.SETTLE_DATE_CASH_LOCAL, r.SETTLE_DATE_CASH_USD, r.CASH_EX_SHORT_LOCAL, r.CASH_EX_SHORT_USD, r.fx_rate, r.TRADER, r.TRADER_ID) "

    return SSQL