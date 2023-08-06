'''所有因子一律只计算一日数据'''
import pandas as pd
import numpy as np

class Factor_get_method(object):
    def __init__(self) -> None:
        pass

    def get_all_tables(self,con):
        sql = "select name from sqlite_master where type ='table' order by name"
        c = con.cursor()
        result = c.execute(sql)
        factorfilelist = [i[0] for i in result.fetchall()]
        return factorfilelist

    def sql_fetch(self,con,tablename):
        cursorObj = con.cursor()
        cursorObj.execute('PRAGMA table_info("{}")'.format(tablename))
        return cursorObj.fetchall()
    
    def sql_exec(self,sql,sqlcols,conn):
        cur = conn.cursor()
        result = cur.execute(sql)
        result = pd.DataFrame(result,columns = sqlcols).set_index(['date','symbol'])
        return result

    def get_prev_days_factor_by_name(self,factorname:str,date:str,conn):
        sql = "select * from {} where {}.date >= '{}'".format(factorname,factorname,date)
        sqlcols = [txt[1] for txt in self.sql_fetch(conn,factorname)]
        return self.sql_exec(sql,sqlcols,conn)
    
    def get_selected_date_factor_by_name(self,factorname:str,date:str,conn):
        sql = "select * from {} where {}.date = '{}'".format(factorname,factorname,date)
        sqlcols = [txt[1] for txt in self.sql_fetch(conn,factorname)]
        return self.sql_exec(sql,sqlcols,conn)
    
def mmt_intraday_M(tempClose,tempOpen):
    # 1个月日内动量
    mmt_intraday_M = (tempClose/tempOpen - 1).iloc[-22:].cumsum()
    mmt_intraday_M = pd.DataFrame(mmt_intraday_M.iloc[-1:].stack(),columns = ['mmt_intraday_M'])
    return mmt_intraday_M

# 一个月振幅调整动量
def mmt_range_M(tempHigh,tempLow,tempClose):
    High_m = tempHigh.iloc[-22:].max()
    Low_m = tempLow.iloc[-22:].min()
    mmt_range_M = (High_m-Low_m)/tempClose.shift(22)
    mmt_range_M = pd.DataFrame(mmt_range_M.iloc[-1:].stack(),columns = ['mmt_range_M'])
    return mmt_range_M

def mmt_overnight_M(tempOpen,tempClose):
    # 隔夜动量
    mmt_overnight = tempOpen/tempClose.shift(1) - 1
    todaydate = mmt_overnight.index[-1]
    mmt_overnight_M = pd.DataFrame(mmt_overnight.iloc[-20:].sum(),columns = ['mmt_overnight_M'])
    mmt_overnight_M['date'] = todaydate
    mmt_overnight_M = mmt_overnight_M.reset_index().set_index(['date','symbol'])
    return mmt_overnight_M

def mmt_route_M(tempClose):
    # 路径调整动量
    mmt_route_M = (tempClose/tempClose.shift(20) - 1)/abs(tempClose/tempClose.shift(1)-1).rolling(20).sum()
    mmt_route_M = pd.DataFrame(mmt_route_M.iloc[-1:].stack(),columns = ['mmt_route_M'])
    return mmt_route_M

def mmt_discrete_M(tempClose):
    # 信息离散度动量
    daily_up = (tempClose/tempClose.shift(1)-1).applymap(lambda x: int(x>0) if not np.isnan(x) else np.nan)
    daily_down = (tempClose/tempClose.shift(1)-1).applymap(lambda x: int(x<0) if not np.isnan(x) else np.nan)
    mmt_discrete_M = daily_up.rolling(20).sum()/20-daily_down.rolling(20).sum()/20
    mmt_discrete_M = pd.DataFrame(mmt_discrete_M.iloc[-1:].stack(),columns = ['mmt_discrete_M'])
    return mmt_discrete_M

def mmt_sec_rank_M(tempClose): 
    # 截面rank动量
    mmt_sec_rank_M = (tempClose/tempClose.shift(1)-1).rank(axis = 1).rolling(20).mean()
    mmt_sec_rank_M = pd.DataFrame(mmt_sec_rank_M.iloc[-1:].stack(),columns = ['mmt_sec_rank_M'])
    return mmt_sec_rank_M

def mmt_time_rank_M(anaual_close):
    # 时序rank_score
    # anaual_close = Close.iloc[-272:]
    mmt_time_rank_M = (anaual_close/anaual_close.shift(1)-1).rolling(252,min_periods = 100).rank().rolling(20).mean()
    mmt_time_rank_M  = pd.DataFrame(mmt_time_rank_M.iloc[-1:].stack(),columns = ['mmt_time_rank_M'])
    return mmt_time_rank_M

def mmt_highest_days_A(anaual_High):
# 最高价距今天数
    todaydate = anaual_High.index[-1]
    mmt_highest_days_A = 252- anaual_High.iloc[-252:].apply(lambda x: x.argmax())
    mmt_highest_days_A = pd.DataFrame(mmt_highest_days_A,columns= ['mmt_highest_days_A'])
    mmt_highest_days_A['date'] = todaydate
    mmt_highest_days_A = mmt_highest_days_A.reset_index().set_index(['date','symbol'])
    return mmt_highest_days_A

def volumestable(volume):
    # 成交量稳定度
    vol_m = volume.rolling(20).mean()
    vol_std = volume.rolling(20).std()
    volumestable = (vol_m/vol_std)
    volumestable = pd.DataFrame(volumestable.iloc[-1:].stack(),columns = ['volumestable'])
    return volumestable

def re_con(tempClose):
    # 收益一致性因子
    import numpy as np
    d5_r = tempClose.pct_change(5).iloc[-1:]/5
    d10_r = tempClose.pct_change(10).iloc[-1:]/10/np.sqrt(2)
    d15_r = tempClose.pct_change(15).iloc[-1:]/15/np.sqrt(3)
    con = pd.concat([d5_r.stack(),d10_r.stack(),d15_r.stack()],axis = 1).dropna()
    con = con.mean(axis =1)/con.std(axis = 1)
    con = con.unstack()

    con_output = con.rank(axis = 1) 
    con_output = con_output.apply(lambda x: x-x.mean(),axis = 1).abs()
    _con = pd.DataFrame(con_output.iloc[-1:].stack(),columns = ['_con'])
    return _con

def bofu_money(tempHigh,tempLow,tempOpen,total_turnover):
    # 波幅/成交额
    bofu_money = (tempHigh-tempLow)/tempOpen/total_turnover
    bofu_money = pd.DataFrame(bofu_money.iloc[-1:].stack(),columns = ['bofu_money'])
    return bofu_money

def vol_std(df,periodname,perioddays):
    ret = df.iloc[-perioddays:]
    todaydate = ret.index[-1]
    df = pd.DataFrame(ret.std(),columns = ['vol_std_'+periodname])    
    df['date'] = todaydate
    df = df.reset_index().set_index(['date','symbol'])
    return df

def vol_up_std(df,periodname,perioddays):
    ret = df.iloc[-perioddays:]
    todaydate = ret.index[-1]
    df = (ret*(ret>0).astype(int)).replace(0,np.nan)
    df = pd.DataFrame(df.std(),columns = ['vol_up_std_'+periodname])
    df['date'] = todaydate
    df = df.reset_index().set_index(['date','symbol'])
    return df

def vol_down_std(df,periodname,perioddays):
    ret = df.iloc[-perioddays:]
    todaydate = ret.index[-1]
    df = (ret*(ret<0).astype(int)).replace(0,np.nan)
    df = pd.DataFrame(df.std(),columns = ['vol_down_std_'+periodname])
    df['date'] = todaydate
    df = df.reset_index().set_index(['date','symbol'])
    return df

def vol_highlow_avg(high,low,periodname,perioddays):
    ratio = (high/low).iloc[-perioddays:]
    todaydate = ratio.index[-1]
    df = pd.DataFrame(ratio.mean(),columns = ['vol_highlow_avg_'+periodname])    
    df['date'] = todaydate
    df = df.reset_index().set_index(['date','symbol'])
    return df

def vol_highlow_std(high,low,periodname,perioddays):
    ratio = (high/low).iloc[-perioddays:]
    todaydate = ratio.index[-1]
    df = pd.DataFrame(ratio.std(),columns = ['vol_highlow_std_'+periodname])    
    df['date'] = todaydate
    df = df.reset_index().set_index(['date','symbol'])
    return df

def vol_updown_ratio(df,periodname,perioddays):
    upstd = vol_up_std(df,periodname,perioddays)
    downstd = vol_down_std(df,periodname,perioddays)
    updownratio = pd.DataFrame(upstd['vol_up_std_'+periodname]/downstd['vol_down_std_'+periodname],columns = ['vol_updown_ratio_'+periodname])
    return updownratio

def vol_highlow_stable(high,low,periodname,perioddays):
    hlavg = vol_highlow_avg(high,low,periodname,perioddays)
    hlstd = vol_highlow_std(high,low,periodname,perioddays)
    hlstable = pd.DataFrame(hlavg['vol_highlow_avg_'+periodname]/hlstd['vol_highlow_std_'+periodname],columns = ['vol_highlow_stable_'+periodname])
    return hlstable

def vol_upshadow_avg(High,Open,Close,periodname,perioddays):
    multiper = (Open>Close).astype(int)
    Open_Close_max = multiper*Open + (1-multiper)*Close
    upshadow_df = ((High - Open_Close_max)/High).iloc[-perioddays:]
    todaydate = upshadow_df.index[-1]
    df = pd.DataFrame(upshadow_df.mean(),columns = ['vol_upshadow_avg_'+periodname])    
    df['date'] = todaydate
    df = df.reset_index().set_index(['date','symbol'])
    return df

def vol_upshadow_std(High,Open,Close,periodname,perioddays):
    multiper = (Open>Close).astype(int)
    Open_Close_max = multiper*Open + (1-multiper)*Close
    upshadow_df = ((High - Open_Close_max)/High).iloc[-perioddays:]
    todaydate = upshadow_df.index[-1]
    df = pd.DataFrame(upshadow_df.std(),columns = ['vol_upshadow_std_'+periodname])    
    df['date'] = todaydate
    df = df.reset_index().set_index(['date','symbol'])
    return df

def vol_upshadow_stable(High,Open,Close,periodname,perioddays):
    avg = vol_upshadow_avg(High,Open,Close,periodname,perioddays)
    std = vol_upshadow_std(High,Open,Close,periodname,perioddays)
    df = pd.DataFrame(avg['vol_upshadow_avg_'+periodname]/std['vol_upshadow_std_'+periodname],columns = ['vol_upshadow_stable_'+periodname])
    return df

def vol_downshadow_avg(Low,Open,Close,periodname,perioddays):
    multiper = (Open<Close).astype(int)
    Open_Close_min = multiper*Open + (1-multiper)*Close
    downshadow_df = ((Open_Close_min - Low)/Low).iloc[-perioddays:]
    todaydate = downshadow_df.index[-1]
    df = pd.DataFrame(downshadow_df.mean(),columns = ['vol_downshadow_avg_'+periodname])    
    df['date'] = todaydate
    df = df.reset_index().set_index(['date','symbol'])
    return df
    
def vol_downshadow_std(Low,Open,Close,periodname,perioddays):
    multiper = (Open<Close).astype(int)
    Open_Close_min = multiper*Open + (1-multiper)*Close
    downshadow_df = ((Open_Close_min - Low)/Low).iloc[-perioddays:]
    todaydate = downshadow_df.index[-1]
    df = pd.DataFrame(downshadow_df.std(),columns = ['vol_downshadow_std_'+periodname])    
    df['date'] = todaydate
    df = df.reset_index().set_index(['date','symbol'])
    return df

def vol_downshadow_stable(Low,Open,Close,periodname,perioddays):
    avg = vol_downshadow_avg(Low,Open,Close,periodname,perioddays)
    std = vol_downshadow_std(Low,Open,Close,periodname,perioddays)
    df = pd.DataFrame(avg['vol_downshadow_avg_'+periodname]/std['vol_downshadow_std_'+periodname],columns = ['vol_downshadow_stable_'+periodname])
    return df

def vol_w_downshadow_avg(Low,Close,periodname,perioddays):
    downshadow_df = ((Close - Low)/Low).iloc[-perioddays:]
    todaydate = downshadow_df.index[-1]
    df = pd.DataFrame(downshadow_df.mean(),columns = ['vol_w_downshadow_avg_'+periodname])    
    df['date'] = todaydate
    df = df.reset_index().set_index(['date','symbol'])
    return df

def vol_w_downshadow_std(Low,Close,periodname,perioddays):
    downshadow_df = ((Close - Low)/Low).iloc[-perioddays:]
    todaydate = downshadow_df.index[-1]
    df = pd.DataFrame(downshadow_df.std(),columns = ['vol_w_downshadow_std_'+periodname])    
    df['date'] = todaydate
    df = df.reset_index().set_index(['date','symbol'])
    return df

def vol_w_downshadow_stable(Low,Close,periodname,perioddays):
    avg = vol_w_downshadow_avg(Low,Close,periodname,perioddays)
    std = vol_w_downshadow_std(Low,Close,periodname,perioddays)
    df = pd.DataFrame(avg['vol_w_downshadow_avg_'+periodname]/std['vol_w_downshadow_std_'+periodname],columns = ['vol_w_downshadow_stable_'+periodname])
    return df

def vol_w_upshadow_avg(High,Close,periodname,perioddays):
    upshadow_df = ((High - Close)/High).iloc[-perioddays:]
    todaydate = upshadow_df.index[-1]
    df = pd.DataFrame(upshadow_df.mean(),columns = ['vol_w_upshadow_avg_'+periodname])    
    df['date'] = todaydate
    df = df.reset_index().set_index(['date','symbol'])
    return df

def vol_w_upshadow_std(High,Close,periodname,perioddays):
    upshadow_df = ((High - Close)/High).iloc[-perioddays:]
    todaydate = upshadow_df.index[-1]
    df = pd.DataFrame(upshadow_df.std(),columns = ['vol_w_upshadow_std_'+periodname])    
    df['date'] = todaydate
    df = df.reset_index().set_index(['date','symbol'])
    return df

def vol_w_upshadow_stable(High,Close,periodname,perioddays):
    avg = vol_w_upshadow_avg(High,Close,periodname,perioddays)
    std = vol_w_upshadow_std(High,Close,periodname,perioddays)
    df = pd.DataFrame(avg['vol_w_upshadow_avg_'+periodname]/std['vol_w_upshadow_std_'+periodname],columns = ['vol_w_upshadow_stable_'+periodname])
    return df

def liq_turn_avg(tovr_r,periodname,perioddays):
    tovr_r_df = tovr_r.iloc[-perioddays:]
    todaydate = tovr_r_df.index[-1]
    df = pd.DataFrame(tovr_r_df.mean(),columns = ['liq_turn_avg_'+periodname])    
    df['date'] = todaydate
    df = df.reset_index().set_index(['date','symbol'])
    return df

def liq_turn_std(tovr_r,periodname,perioddays):
    tovr_r_df = tovr_r.iloc[-perioddays:]
    todaydate = tovr_r_df.index[-1]
    df = pd.DataFrame(tovr_r_df.std(),columns = ['liq_turn_std_'+periodname])    
    df['date'] = todaydate
    df = df.reset_index().set_index(['date','symbol'])
    return df

def liq_vstd(tovr_r,ret,periodname,perioddays):
    tovr_r_df = tovr_r.iloc[-perioddays:]
    ret_df = ret.iloc[-perioddays:]
    df = pd.DataFrame(tovr_r_df.mean()/ret_df.std(),columns = ['liq_vstd_'+periodname])  
    todaydate = tovr_r_df.index[-1]
    df['date'] = todaydate
    df = df.reset_index().set_index(['date','symbol'])
    return df

def liq_amihud_avg(tovr_r,ret,periodname,perioddays):
    tovr_r_df = tovr_r.iloc[-perioddays:]
    ret_df_abs = ret.iloc[-perioddays:].abs()
    amihud = ret_df_abs/tovr_r_df
    df = pd.DataFrame(amihud.mean(),columns = ['liq_amihud_avg_'+periodname])  
    todaydate = amihud.index[-1]
    df['date'] = todaydate
    df = df.reset_index().set_index(['date','symbol'])
    return df

def liq_amihud_std(tovr_r,ret,periodname,perioddays):
    tovr_r_df = tovr_r.iloc[-perioddays:]
    ret_df_abs = ret.iloc[-perioddays:].abs()
    amihud = ret_df_abs/tovr_r_df
    df = pd.DataFrame(amihud.std(),columns = ['liq_amihud_std_'+periodname])  
    todaydate = amihud.index[-1]
    df['date'] = todaydate
    df = df.reset_index().set_index(['date','symbol'])
    return df

def liq_amihud_stable(tovr_r,ret,periodname,perioddays):
    avg = liq_amihud_avg(tovr_r,ret,periodname,perioddays)
    std = liq_amihud_std(tovr_r,ret,periodname,perioddays)
    v = avg['liq_amihud_avg_'+periodname]/std['liq_amihud_std_'+periodname]
    df = pd.DataFrame(v,columns = ['liq_amihud_stable_'+periodname])  
    return df

def liq_shortcut_avg(tovr_r,High,Low,Open,Close,periodname,perioddays):
    shortcut = 2*(High - Low) - (Open - Close).abs()
    v = shortcut.iloc[-perioddays:]/tovr_r.iloc[-perioddays:]
    df = pd.DataFrame(v.mean(),columns = ['liq_shortcut_avg_'+periodname])  
    todaydate = v.index[-1]
    df['date'] = todaydate
    df = df.reset_index().set_index(['date','symbol'])
    return df

def liq_shortcut_std(tovr_r,High,Low,Open,Close,periodname,perioddays):
    shortcut = 2*(High - Low) - (Open - Close).abs()
    v = shortcut.iloc[-perioddays:]/tovr_r.iloc[-perioddays:]
    df = pd.DataFrame(v.std(),columns = ['liq_shortcut_std_'+periodname])  
    todaydate = v.index[-1]
    df['date'] = todaydate
    df = df.reset_index().set_index(['date','symbol'])
    return df

def liq_shortcut_stable(tovr_r,High,Low,Open,Close,periodname,perioddays):
    avg = liq_shortcut_avg(tovr_r,High,Low,Open,Close,periodname,perioddays)
    std = liq_shortcut_std(tovr_r,High,Low,Open,Close,periodname,perioddays)
    v = avg['liq_shortcut_avg_'+periodname]/std['liq_shortcut_std_'+periodname]
    df = pd.DataFrame(v,columns = ['liq_shortcut_stable_'+periodname])  
    return df

def PLUS(Close, High, Low):
    plus = (2*Close - High - Low)/Close.shift(1)
    todaydate = plus.index[-1]
    df = pd.DataFrame(plus.iloc[-1])
    df.columns = ['plus']
    df['date'] = todaydate
    df = df.reset_index().set_index(['date','symbol'])
    return df

def liq_std_w_plus(Close, High, Low, tovr_r,periodname,perioddays):
    plus = PLUS(Close, High, Low)
    liq_std = liq_turn_std(tovr_r,periodname,perioddays)
    plus['plus'] = plus['plus'].groupby(level = 'date', group_keys=False).apply(lambda x: x-min(0,x.min()))
    swp = liq_std['liq_turn_std_'+periodname]*plus['plus']
    df = pd.DataFrame(swp,columns = ['liq_std_w_plus_'+periodname])
    return df

def tvr_std(tovr_r,periodname,perioddays):
    df = tovr_r.iloc[-perioddays:]
    todaydate = tovr_r.index[-1]
    fc = pd.DataFrame(df.std())
    fc.columns = ['tvr_std_'+periodname]
    fc['date'] = todaydate
    fc = fc.reset_index().set_index(['date','symbol'])
    return fc.sort_index()

def HL_Sprd(close,high,low,perioddays):
    todaydate = close.index[-1]
    sprd = (high/low - 1).iloc[-perioddays:]
    close_ = close.iloc[-perioddays:]
    phigh = close_.apply(lambda x: x>x.quantile(0.75)).astype(int).replace(0,np.nan)
    plow = close_.apply(lambda x: x<x.quantile(0.25)).astype(int).replace(0,np.nan)
    vhigh = pd.DataFrame((sprd*phigh).mean())
    vlow = pd.DataFrame((sprd*plow).mean())
    vlow['date'],vhigh['date'] = todaydate,todaydate
    vhigh = vhigh.set_index('date',append=True).swaplevel()
    vlow = vlow.set_index('date',append=True).swaplevel()
    hlsprd = vhigh-vlow
    hlsprd.columns = ['HL_Sprd']
    return hlsprd.dropna()

def corr_price_turn(timerange,pricebyday,periodname):
    price = pricebyday.loc[timerange]
    fc = price[['close','turnover_ratio']].groupby(level = 'symbol').apply(lambda x: x.droplevel('symbol').sort_index().corr())
    fc = list(fc.groupby(level = 1))[1][1].droplevel(1)['close']
    fc = pd.DataFrame(fc).dropna()
    fc.columns =['corr_price_turn_'+periodname]
    fc['date'] = timerange[-1]
    fc = fc.reset_index().set_index(['date','symbol'])
    return fc

def corr_ret_turn_post(timerange,pricebyday,periodname):
    pricedf = pricebyday.loc[timerange]
    pricedf['turnover_ratio'] = pricedf['turnover_ratio'].unstack().sort_index().shift(1).stack() # post
    pricedf['ret'] = pricedf['close'].unstack().sort_index().pct_change().stack()
    fc = pricedf[['ret','turnover_ratio']].groupby(level = 'symbol').apply(lambda x: x.droplevel('symbol').sort_index().corr())
    fc = list(fc.groupby(level = 1))[1][1].droplevel(1)['ret']
    fc = pd.DataFrame(fc).dropna()
    fc.columns =['corr_ret_turn_post_'+periodname]
    fc['date'] = timerange[-1]
    fc = fc.reset_index().set_index(['date','symbol'])
    return fc

def corr_ret_turnd(timerange,pricebyday,periodname):
    pricedf = pricebyday.loc[timerange]
    pricedf['turnover_ratio_pct'] = pricedf['turnover_ratio'].unstack().sort_index().pct_change().stack()
    pricedf['ret'] = pricedf['close'].unstack().sort_index().pct_change().stack()
    fc = pricedf[['ret','turnover_ratio_pct']].dropna().groupby(level = 'symbol').apply(lambda x: x.droplevel('symbol').sort_index().corr())
    fc = list(fc.groupby(level = 1))[1][1].droplevel(1)['ret']
    fc = pd.DataFrame(fc).dropna()
    fc.columns =['corr_ret_turnd_'+periodname]
    fc['date'] = timerange[-1]
    fc = fc.reset_index().set_index(['date','symbol'])    
    return fc

def mts(sta_del_extrm,minbar,todaydate):
    mts = sta_del_extrm[['single_trade_amt']]
    mts['total_turnover'] = minbar['total_turnover']
    mts = mts.groupby(level = 'symbol').corr()[::2]['total_turnover'].droplevel(1)
    mts=  pd.DataFrame(mts)
    mts.columns = ['mts']
    mts['date'] = todaydate
    mts = mts.reset_index().set_index(['date','symbol'])
    return mts

def mte(sta_del_extrm,minbar,todaydate):
    mte = sta_del_extrm[['single_trade_amt']]
    mte['close'] = minbar['close']
    mte = mte.groupby(level = 'symbol').corr()[::2]['close'].droplevel(1)
    mte=  pd.DataFrame(mte)
    mte.columns = ['mte']
    mte['date'] = todaydate
    mte = mte.reset_index().set_index(['date','symbol'])
    return mte

def qua(sta_del_extrm,todaydate):
    qua = sta_del_extrm.groupby(level = 'symbol').\
        apply(lambda x: (x['single_trade_amt'].quantile(0.1)-\
            x['single_trade_amt'].min())/(x['single_trade_amt'].max()-x['single_trade_amt'].min()))
    qua = pd.DataFrame(qua,columns = ['qua'])
    qua['date'] = todaydate
    qua = qua.reset_index().set_index(['date','symbol'])
    qua.index.name = ('date','symbol')
    return qua

def skew(sta_50pct,todaydate):# 偏度因子skew
    skew = sta_50pct.groupby(level = 'symbol').\
        apply(lambda x: (((x['single_trade_amt']-x['single_trade_amt'].mean())/x['single_trade_amt'].std())**3).mean())
    skew = pd.DataFrame(skew,columns = ['skew'])
    skew['date'] = todaydate
    skew = skew.reset_index().set_index(['date','symbol'])
    skew.index.name = ('date','symbol')
    return skew

def s_reverse(sing_trade_amt,minbar,todaydate):# 强反转因子
    minute_r = sing_trade_amt.copy()
    minute_r['minute_r'] = minbar['close']/minbar['open'] - 1
    minute_r = minute_r.set_index('trading_date',append = True)
    s_reverse = minute_r.groupby(level = 0).\
        apply(lambda x: x[x.single_trade_amt > x.single_trade_amt.quantile(0.8)].minute_r.sum())
    s_reverse = pd.DataFrame(s_reverse,columns = ['s_reverse'])
    s_reverse['date'] = todaydate
    s_reverse = s_reverse.reset_index().set_index(['date','symbol'])
    s_reverse.index.name = ('date','symbol')
    return s_reverse

def daily_sta_90pct(sta_del_extrm):# 日单笔成交额90分位值
    daily_sta = sta_del_extrm.set_index('trading_date',append = True).rename_axis(index = {'trading_date':'date'})
    daily_sta_90pct = daily_sta.droplevel('datetime').groupby(level = 'symbol').apply(lambda x: x.groupby(level = 1).quantile(0.9)).reset_index().set_index(['date','symbol'])
    daily_sta_90pct.columns = ['daily_sta_90pct']
    return daily_sta_90pct

def ideal_reverse(daily_sta_cal,Close):
    daily_sta_cal['day_return'] = Close.pct_change().stack()
    by_stock = list(daily_sta_cal.groupby(level = 1))
    def apply_rolling_cal(rollingdata):
        if len(rollingdata.index)<20:
            return
        else:
            temp = rollingdata.sort_values('daily_sta_90pct')
            returndf = rollingdata.iloc[-1:].copy()
            returndf['ideal_reverse'] = temp.iloc[:10].day_return.sum() - temp.iloc[10:].day_return.sum()
        return returndf['ideal_reverse']
    ideal_reverse = list(map(lambda x:apply_rolling_cal(x[1]),by_stock))
    ideal_reverse = pd.concat(ideal_reverse)
    ideal_reverse = pd.DataFrame(ideal_reverse)
    ideal_reverse.columns = ['ideal_reverse']
    return ideal_reverse