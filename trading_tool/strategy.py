from datetime import datetime

def simple_strategy(df, alpha=0.1, delta=0.01, wallet=(1, 1)):
    
    buy = []
    sell = []
    
    
    while df.shape[0] > 0:
        
        actual = df["open"].iloc[0]
        
        buy_limit = actual - delta
        sell_limit = actual + delta
        
        buy_future = df.loc[df["open"] <= buy_limit]
        sell_future = df.loc[df["open"] >= sell_limit]
        
        if buy_future.shape[0] > 0:
            buy_hor = buy_future.iloc[0]["dateTime"]
        else:
            buy_hor = datetime.max
            
        if sell_future.shape[0] > 0:
            sell_hor = sell_future.iloc[0]["dateTime"]
        else:
            sell_hor = datetime.max  
            
        next_brake = min(buy_hor, sell_hor)
        if next_brake == datetime.max:
            break
    
        df = df.loc[df["dateTime"] > next_brake]
        ratio = df["open"].iloc[0]
    
        is_buy = buy_hor < sell_hor
        
        if is_buy:

            if wallet[1] < alpha:
                break
            wallet = wallet[0] + alpha/ratio, wallet[1] - alpha
            buy.append(next_brake)
            
        else:

            if wallet[0] < alpha:
                break
            wallet = wallet[0] - alpha, wallet[1] + alpha*ratio
            sell.append(next_brake)
            

    return buy, sell, wallet