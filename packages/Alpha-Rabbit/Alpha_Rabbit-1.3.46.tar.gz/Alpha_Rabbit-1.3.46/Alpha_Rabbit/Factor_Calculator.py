from Alpha_Rabbit.Factor_Def_and_Get_Method import *
_method = Factor_get_method()
def Factor_Calculator(pricebyday,minbar,conn,todaydate,notst,factors_to_cal):
    ######################################## 日间数据计算因子 ####################################
    uploadfactordict = {}
    Close = pricebyday['close'].unstack().sort_index()
    Open = pricebyday['open'].unstack().sort_index()
    High = pricebyday['high'].unstack().sort_index()
    Low = pricebyday['low'].unstack().sort_index()
    volume = pricebyday[['volume']].pivot_table(index = 'date',columns = 'symbol',values = 'volume').sort_index()
    total_turnover = pricebyday[['total_turnover']].pivot_table(index = 'date',columns = 'symbol',values = 'total_turnover').sort_index()
    tovr_r = pricebyday['turnover_ratio'].unstack().sort_index()
    Close_ret = Close.pct_change()


    tempClose = Close.iloc[-30:]
    tempOpen = Open.iloc[-30:]
    tempHigh = High.iloc[-30:]
    tempLow = Low.iloc[-30:]
    anaual_close = Close.iloc[-272:]
    anaual_High = High.iloc[-272:]
    
    if 'mmt_intraday_M' in factors_to_cal or factors_to_cal == 'all':
        # 1个月日内动量
        uploadfactordict['mmt_intraday_M'] = mmt_intraday_M(tempClose,tempOpen)
    if 'mmt_range_M' in factors_to_cal or factors_to_cal == 'all':
        # 一个月振幅调整动量
        uploadfactordict['mmt_range_M'] = mmt_range_M(tempHigh,tempLow,tempClose)
    if 'mmt_overnight_M' in factors_to_cal or factors_to_cal == 'all':
        # 隔夜动量
        uploadfactordict['mmt_overnight_M'] = mmt_overnight_M(tempOpen,tempClose)
    if 'mmt_route_M' in factors_to_cal or factors_to_cal == 'all':
        # 路径调整动量
        uploadfactordict['mmt_route_M'] = mmt_route_M(tempClose)
    if 'mmt_discrete_M' in factors_to_cal or factors_to_cal == 'all':
        # 信息离散度动量
        uploadfactordict['mmt_discrete_M'] = mmt_discrete_M(tempClose)
    if 'mmt_sec_rank_M' in factors_to_cal or factors_to_cal == 'all':
        # 截面rank动量
        uploadfactordict['mmt_sec_rank_M'] = mmt_sec_rank_M(tempClose)
    if 'mmt_time_rank_M' in factors_to_cal or factors_to_cal == 'all':
        # 时序rank_score
        uploadfactordict['mmt_time_rank_M'] = mmt_time_rank_M(anaual_close)
    if 'mmt_highest_days_A' in factors_to_cal or factors_to_cal == 'all':
        # 最高价距今天数
        uploadfactordict['mmt_highest_days_A'] = mmt_highest_days_A(anaual_High)
    if 'volumestable' in factors_to_cal or factors_to_cal == 'all':
        # 成交量稳定度
        uploadfactordict['volumestable'] = volumestable(volume)
    if '_con' in factors_to_cal or factors_to_cal == 'all':
        # 收益一致性因子
        uploadfactordict['_con'] = re_con(tempClose)
    if 'bofu_money' in factors_to_cal or factors_to_cal == 'all':
        # 波幅/成交额
        uploadfactordict['bofu_money'] = bofu_money(tempHigh,tempLow,tempOpen,total_turnover)
    if 'vol_std_1M' in factors_to_cal or factors_to_cal == 'all':
        # 一个月收益率波动
        uploadfactordict['vol_std_1M'] = vol_std(Close_ret,'1M',30)
    if 'vol_up_std_1M' in factors_to_cal or factors_to_cal == 'all':
        # 一个月上行收益率波动
        uploadfactordict['vol_up_std_1M'] = vol_up_std(Close_ret,'1M',30)
    if 'vol_down_std_1M' in factors_to_cal or factors_to_cal == 'all':
        # 一个月下行收益率波动
        uploadfactordict['vol_down_std_1M'] = vol_down_std(Close_ret,'1M',30)   
    if 'vol_updown_ratio_1M' in factors_to_cal or factors_to_cal == 'all':
        # 一个月上行波动和下行波动比
        uploadfactordict['vol_updown_ratio_1M'] = vol_updown_ratio(Close_ret,'1M',30)   
    if 'vol_highlow_avg_1M' in factors_to_cal or factors_to_cal == 'all':
        # 一个月振幅均值
        uploadfactordict['vol_highlow_avg_1M'] = vol_highlow_avg(High,Low,'1M',30)   
    if 'vol_highlow_std_1M' in factors_to_cal or factors_to_cal == 'all':
        # 一个月振幅波动
        uploadfactordict['vol_highlow_std_1M'] = vol_highlow_std(High,Low,'1M',30)   
    if 'vol_highlow_stable_1M' in factors_to_cal or factors_to_cal == 'all':
        # 一个月振幅稳定度
        uploadfactordict['vol_highlow_stable_1M'] = vol_highlow_stable(High,Low,'1M',30)   
    if 'vol_upshadow_avg_1M' in factors_to_cal or factors_to_cal == 'all':
        # 一个月上影线均值
        uploadfactordict['vol_upshadow_avg_1M'] = vol_upshadow_avg(High,Open,Close,'1M',30) 
    if 'vol_upshadow_std_1M' in factors_to_cal or factors_to_cal == 'all':
        # 一个月上影线波动
        uploadfactordict['vol_upshadow_std_1M'] = vol_upshadow_std(High,Open,Close,'1M',30) 
    if 'vol_upshadow_stable_1M' in factors_to_cal or factors_to_cal == 'all':
        # 一个月上影线稳定度
        uploadfactordict['vol_upshadow_stable_1M'] = vol_upshadow_stable(High,Open,Close,'1M',30) 
    if 'vol_downshadow_avg_1M' in factors_to_cal or factors_to_cal == 'all':
        # 一个月下影线均值
        uploadfactordict['vol_downshadow_avg_1M'] = vol_downshadow_avg(Low,Open,Close,'1M',30) 
    if 'vol_downshadow_std_1M' in factors_to_cal or factors_to_cal == 'all':
        # 一个月下影线波动
        uploadfactordict['vol_downshadow_std_1M'] = vol_downshadow_std(Low,Open,Close,'1M',30) 
    if 'vol_downshadow_stable_1M' in factors_to_cal or factors_to_cal == 'all':
        # 一个月下影线稳定度
        uploadfactordict['vol_downshadow_stable_1M'] = vol_downshadow_stable(Low,Open,Close,'1M',30) 
    if 'vol_w_upshadow_avg_1M' in factors_to_cal or factors_to_cal == 'all':
        # 一个月威廉上影线均值
        uploadfactordict['vol_w_upshadow_avg_1M'] = vol_w_upshadow_avg(High,Close,'1M',30) 
    if 'vol_w_upshadow_std_1M' in factors_to_cal or factors_to_cal == 'all':
        # 一个月威廉上影线波动
        uploadfactordict['vol_w_upshadow_std_1M'] = vol_w_upshadow_std(High,Close,'1M',30) 
    if 'vol_w_upshadow_stable_1M' in factors_to_cal or factors_to_cal == 'all':
        # 一个月威廉上影线稳定度
        uploadfactordict['vol_w_upshadow_stable_1M'] = vol_w_upshadow_stable(High,Close,'1M',30) 
    if 'vol_w_downshadow_avg_1M' in factors_to_cal or factors_to_cal == 'all':
        # 一个月威廉下影线均值
        uploadfactordict['vol_w_downshadow_avg_1M'] = vol_w_downshadow_avg(Low,Close,'1M',30) 
    if 'vol_w_downshadow_std_1M' in factors_to_cal or factors_to_cal == 'all':
        # 一个月威廉下影线波动
        uploadfactordict['vol_w_downshadow_std_1M'] = vol_w_downshadow_std(Low,Close,'1M',30) 
    if 'vol_w_downshadow_stable_1M' in factors_to_cal or factors_to_cal == 'all':
        # 一个月威廉下影线稳定度
        uploadfactordict['vol_w_downshadow_stable_1M'] = vol_w_downshadow_stable(Low,Close,'1M',30) 

    if 'liq_turn_avg_1M' in factors_to_cal or factors_to_cal == 'all':
        # 一个月换手均值
        uploadfactordict['liq_turn_avg_1M'] = liq_turn_avg(tovr_r,'1M',30) 
        
    if 'liq_turn_std_1M' in factors_to_cal or factors_to_cal == 'all':
        # 一个月换手方差
        uploadfactordict['liq_turn_std_1M'] = liq_turn_std(tovr_r,'1M',30) 
        
    if 'liq_vstd_1M' in factors_to_cal or factors_to_cal == 'all':
        # 一个月成交波动比
        uploadfactordict['liq_vstd_1M'] = liq_vstd(tovr_r,Close_ret,'1M',30) 

    if 'liq_amihud_avg_1M' in factors_to_cal or factors_to_cal == 'all':
        # 一个月amihud非流动因子均值
        uploadfactordict['liq_amihud_avg_1M'] = liq_amihud_avg(tovr_r,Close_ret,'1M',30) 

    if 'liq_amihud_std_1M' in factors_to_cal or factors_to_cal == 'all':
        # 一个月amihud非流动因子波动
        uploadfactordict['liq_amihud_std_1M'] = liq_amihud_std(tovr_r,Close_ret,'1M',30) 

    if 'liq_amihud_stable_1M' in factors_to_cal or factors_to_cal == 'all':
        # 一个月amihud非流动因子稳定度
        uploadfactordict['liq_amihud_stable_1M'] = liq_amihud_stable(tovr_r,Close_ret,'1M',30) 
        
    if 'liq_shortcut_avg_1M' in factors_to_cal or factors_to_cal == 'all':
        # 一个月最短路径非流动因子均值
        uploadfactordict['liq_shortcut_avg_1M'] = liq_shortcut_avg(tovr_r,High,Low,Open,Close,'1M',30) 

    if 'liq_shortcut_std_1M' in factors_to_cal or factors_to_cal == 'all':
        # 一个月最短路径非流动因子波动
        uploadfactordict['liq_shortcut_std_1M'] = liq_shortcut_std(tovr_r,High,Low,Open,Close,'1M',30) 

    if 'liq_shortcut_stable_1M' in factors_to_cal or factors_to_cal == 'all':
        # 一个月最短路径非流动因子稳定度
        uploadfactordict['liq_shortcut_stable_1M'] = liq_shortcut_stable(tovr_r,High,Low,Open,Close,'1M',30) 

    if 'PLUS' in factors_to_cal or factors_to_cal == 'all':
        # 上下影线差
        uploadfactordict['PLUS'] = PLUS(tempClose,tempHigh,tempLow) 

    if 'liq_std_w_plus_1M' in factors_to_cal or factors_to_cal == 'all':
        # 上下影线差*换手波动
        uploadfactordict['liq_std_w_plus_1M'] = liq_std_w_plus(tempClose,tempHigh,tempLow, tovr_r,'1M',30) 

    if 'HL_Sprd' in factors_to_cal or factors_to_cal == 'all':
        # 理想振幅因子
        uploadfactordict['HL_Sprd'] = HL_Sprd(Close,High,Low,20)

    if 'tvr_std_1M' in factors_to_cal or factors_to_cal == 'all':
        # 换手率稳定度
        uploadfactordict['tvr_std_1M'] = tvr_std(tovr_r,'1M',20)

    if 'corr_price_turn_1M' in factors_to_cal or factors_to_cal == 'all':
        # 换手率与价格的相关性因子
        timerange = sorted(list(pricebyday.index.get_level_values('date').drop_duplicates()))[-20:]
        uploadfactordict['corr_price_turn_1M'] = corr_price_turn(timerange,pricebyday,'1M')

    if 'corr_ret_turn_post_1M' in factors_to_cal or factors_to_cal == 'all':
        # 收益率与换手率的相关性因子
        timerange = sorted(list(pricebyday.index.get_level_values('date').drop_duplicates()))[-21:] # 涉及到计算pct_change需要多一天
        uploadfactordict['corr_ret_turn_post_1M'] = corr_ret_turn_post(timerange,pricebyday,'1M')

    if 'corr_ret_turnd_1M' in factors_to_cal or factors_to_cal == 'all':
        # 收益率与换手率变动的相关性因子
        timerange = sorted(list(pricebyday.index.get_level_values('date').drop_duplicates()))[-21:]
        uploadfactordict['corr_ret_turnd_1M'] = corr_ret_turnd(timerange,pricebyday,'1M')
    ######################################## 日内数据计算因子 ####################################

    # #单笔成交金额相关因子
    sing_trade_amt = pd.DataFrame(minbar['total_turnover']/minbar['num_trades'],columns= ['single_trade_amt'])
    sing_trade_amt = sing_trade_amt[sing_trade_amt['single_trade_amt']>=0]
    sing_trade_amt['trading_date'] = todaydate
    sta_del_extrm = sing_trade_amt.groupby(level = 0).apply(lambda x: x.sort_values('single_trade_amt').iloc[:-10]).droplevel(0)# 剔除极大值
    sta_50pct = sing_trade_amt.groupby(level = 0).\
        apply(lambda x: x[x['single_trade_amt']<x['single_trade_amt'].quantile(0.5)]).droplevel(0)# 后百分之五十


    if 'mts' in factors_to_cal or factors_to_cal == 'all':
        # 主力交易强度
        uploadfactordict['mts'] = mts(sta_del_extrm,minbar,todaydate)

    if 'mte' in factors_to_cal or factors_to_cal == 'all':
        # 主力交易情绪
        uploadfactordict['mte'] = mte(sta_del_extrm,minbar,todaydate)

    if 'qua' in factors_to_cal or factors_to_cal == 'all':
        # 分位数因子qua
        uploadfactordict['qua'] = qua(sta_del_extrm,todaydate)

    if 'qua20m' in factors_to_cal or factors_to_cal == 'all':
        prv_factor = _method.get_prev_days_factor_by_name('qua',notst.index[-20],conn)
        q = qua(sta_del_extrm,todaydate)
        qua20m = pd.concat([prv_factor,q]).unstack().rolling(20).mean().iloc[-1:].stack().rename(columns = {'qua':'qua20m'})
        uploadfactordict['qua20m'] = qua20m

    if 'skew' in factors_to_cal or factors_to_cal == 'all':
        # 偏度因子skew
        uploadfactordict['skew'] = skew(sta_50pct,todaydate)

    if 'skew20m' in factors_to_cal or factors_to_cal == 'all':
        prv_factor = _method.get_prev_days_factor_by_name('skew',notst.index[-20],conn)
        sk = skew(sta_50pct,todaydate)
        skew20m = pd.concat([prv_factor,sk]).unstack().rolling(20).mean().iloc[-1:].stack().rename(columns = {'skew':'skew20m'})
        uploadfactordict['skew20m'] = skew20m

    if 's_reverse' in factors_to_cal or factors_to_cal == 'all':
        # 强反转因子
        uploadfactordict['s_reverse'] = s_reverse(sing_trade_amt,minbar,todaydate)

    if 's_reverse_10_sum' in factors_to_cal or factors_to_cal == 'all':
        prv_factor = _method.get_prev_days_factor_by_name('s_reverse',notst.index[-10],conn)
        sr = s_reverse(sing_trade_amt,minbar,todaydate)
        s_reverse_10_sum = pd.concat([prv_factor,sr]).unstack().rolling(10).sum().iloc[-1:].stack().rename(columns = {'s_reverse':'s_reverse_10_sum'})
        uploadfactordict['s_reverse_10_sum'] = s_reverse_10_sum

    if 'daily_sta_90pct' in factors_to_cal or factors_to_cal == 'all':
        # 理想反转因子
        uploadfactordict['daily_sta_90pct'] = daily_sta_90pct(sta_del_extrm)
    
    if 'ideal_reverse' in factors_to_cal or factors_to_cal == 'all':
        prv_factor = _method.get_prev_days_factor_by_name('daily_sta_90pct',notst.index[-20],conn)
        dsta90 = daily_sta_90pct(sing_trade_amt)
        daily_sta_cal = pd.concat([prv_factor,dsta90])
        uploadfactordict['ideal_reverse'] = ideal_reverse(daily_sta_cal,Close)

    return uploadfactordict