def TopK_dropout(k,oldpos,newsignal,allsignal):
    oldpos = list(filter(lambda x: x.volume>0,oldpos))
    if len(oldpos)==0: # 空仓直接买
        return [],newsignal
    symbollist = [p.symbol for p in oldpos] # 老仓标的
    inold_notinnew = list(set(symbollist) - set(newsignal['codes'].to_list())) # 在老仓不在新仓
    innew_notinold = list(set(newsignal['codes'].to_list())-set(symbollist)) # 在新仓不在老仓
    changenumbs = min(len(inold_notinnew),len(innew_notinold)) # 要变的股票数量为二者最小值
    new_pref = allsignal[allsignal.codes.isin(innew_notinold)].sort_values('weighted_factor') # 新信号中不在老仓股票的评分排序
    old_pref = allsignal[allsignal.codes.isin(inold_notinnew)].sort_values('weighted_factor') # 老仓中不在新信号的评分排序
    if 0< changenumbs <=k: # 调仓股票数量在容忍度内
        bad_old_pref = old_pref.iloc[:changenumbs].codes.to_list() # 是多少就换多少
        clean_pos = list(filter(lambda x: x.symbol in bad_old_pref, oldpos))
        buy_item = new_pref.iloc[-changenumbs:]
        return clean_pos,buy_item
    if changenumbs > k: # 调仓股票数量超过容忍度
        bad_old_pref = old_pref.iloc[:k].codes.to_list() # 只换容忍度数量内的
        clean_pos = list(filter(lambda x: x.symbol in bad_old_pref, oldpos))
        buy_item = new_pref.iloc[-k:]
        return clean_pos,buy_item
    if changenumbs == 0: # 仓位一致一动不动
        return [],None