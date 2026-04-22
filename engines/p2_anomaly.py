import pandas as pd

class AnomalyDetectionEngine:
    def __init__(self, volume_spike_threshold=3.0, price_spike_threshold=0.015):
        # 默认设定量能放大3倍，价格5分钟内波动 1.5% 为异动
        self.vol_threshold = volume_spike_threshold
        self.price_threshold = price_spike_threshold

    def detect(self, symbol, current_kline, recent_klines):
        """
        P2 异动监控引擎
        current_kline: 当前5分钟的K线数据 (dict, 需要 keys: open, close, volume)
        recent_klines: 过去N根K线的历史数据 (DataFrame)
        """
        if recent_klines is None or recent_klines.empty:
            return None

        avg_vol = recent_klines['volume'].mean()
        current_vol = current_kline.get('volume', 0)
        
        # 成交量异常突增
        vol_spike = current_vol > (avg_vol * self.vol_threshold)
        
        # 价格突变
        open_p = current_kline.get('open', 0)
        close_p = current_kline.get('close', 0)
        if open_p == 0:
            return None
            
        price_change = (close_p - open_p) / open_p
        price_spike = abs(price_change) >= self.price_threshold
        
        # 必须量价齐升/跌才算完全确认的短线异动
        if vol_spike and price_spike:
            direction = "up" if price_change > 0 else "down"
            return {
                "symbol": symbol,
                "type": "anomaly",
                "direction": direction,
                "price_change": price_change,
                "vol_multiple": current_vol / avg_vol if avg_vol > 0 else 0,
                "current_price": close_p,
                "reason": f"成交量放大 {current_vol/avg_vol:.1f}倍, 价格{'拉升' if direction=='up' else '暴跌'} {price_change*100:.2f}%"
            }
        return None
