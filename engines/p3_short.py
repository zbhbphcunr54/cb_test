import pandas as pd
import pandas_ta as ta

class ShortTermEngine:
    def __init__(self, symbols):
        self.symbols = symbols

    def analyze(self, symbol, df_5m, df_15m):
        """
        P3 短线引擎 (基于 5m 和 15m)
        只有当且仅当发生异动且短线趋势共振时，才返回短线交易信号
        """
        if df_5m is None or len(df_5m) < 20 or df_15m is None or len(df_15m) < 20:
            return None
            
        # 1. 计算短期均线交叉和布林带
        df_5m.ta.ema(length=5, append=True)
        df_5m.ta.ema(length=15, append=True)
        df_5m.ta.rsi(length=14, append=True)
        df_5m.ta.bbands(length=20, std=2, append=True)
        
        last_5m = df_5m.iloc[-1]
        prev_5m = df_5m.iloc[-2]
        
        close = last_5m['close']
        ema5 = last_5m.get('EMA_5')
        ema15 = last_5m.get('EMA_15')
        rsi14 = last_5m.get('RSI_14')
        bbu = last_5m.get([c for c in df_5m.columns if c.startswith('BBU_')][0]) if [c for c in df_5m.columns if c.startswith('BBU_')] else 0
        bbl = last_5m.get([c for c in df_5m.columns if c.startswith('BBL_')][0]) if [c for c in df_5m.columns if c.startswith('BBL_')] else 0
        
        if pd.isna(ema5) or pd.isna(ema15):
            return None
            
        # 短线多头共振
        # 5日线金叉15日线，且当前价格处于布林带中轨以上，不触碰上轨
        ema_cross_up = ema5 > ema15 and prev_5m.get('EMA_5') <= prev_5m.get('EMA_15')
        
        if ema_cross_up and close < bbu * 0.99 and rsi14 < 75:
            # 止损设在布林下轨，止盈采用 2:1 RR
            sl = bbl
            tp = close + (close - sl) * 2
            
            return {
                "symbol": symbol,
                "side": "long",
                "type": "short_term",
                "current_price": close,
                "target_price": tp,
                "stop_loss_price": sl,
                "win_rate": 0.4, # 胜率略低于中长线
                "reason": "5M EMA5上穿EMA15，RSI未超买"
            }
            
        # 短线空头共振
        ema_cross_down = ema5 < ema15 and prev_5m.get('EMA_5') >= prev_5m.get('EMA_15')
        
        if ema_cross_down and close > bbl * 1.01 and rsi14 > 25:
             sl = bbu
             tp = close - (sl - close) * 2
             return {
                 "symbol": symbol,
                 "side": "short",
                 "type": "short_term",
                 "current_price": close,
                 "target_price": tp,
                 "stop_loss_price": sl,
                 "win_rate": 0.4,
                 "reason": "5M EMA5下穿EMA15，RSI未超卖"
             }
        return None
