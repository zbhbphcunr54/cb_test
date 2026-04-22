import ccxt
import time
import pandas as pd
from typing import List, Dict

class OKXMarketScanner:
    def __init__(self, api_key: str = "", secret: str = "", password: str = ""):
        # 使用 ccxt 实例化 OKX 客户端
        self.exchange = ccxt.okx({
            'apiKey': api_key,
            'secret': secret,
            'password': password,
            'enableRateLimit': True, # 开启 ccxt 内置限频
        })
        self.top_20_symbols: List[str] = []

    def fetch_all_tickers(self, inst_type: str = 'SWAP') -> pd.DataFrame:
        """
        获取全市场某一类型（现货 SPOT 或 合约 SWAP）的 Tickers 数据
        只占用 1 次 REST API 调用
        """
        try:
            # OKX 特有参数
            params = {'instType': inst_type}
            # ccxt 的隐式 API 调用对应 GET /api/v5/market/tickers
            response = self.exchange.public_get_market_tickers(params)
            
            if response and 'data' in response:
                df = pd.DataFrame(response['data'])
                # 把需要用到的字段转为 float
                df['volCcy24h'] = df['volCcy24h'].astype(float) # 24H 成交额(计价货币，通常是 USDT)
                return df
            return pd.DataFrame()
        except Exception as e:
            print(f"[Error] 获取 {inst_type} 市场 tickers 失败: {e}")
            return pd.DataFrame()

    def update_top_20(self, blacklist: List[str] = None) -> List[str]:
        """
        数据采集层 3.1: 动态 Top 20 机制
        按 24H 成交额降序取得前 20 个 U本位永续合约
        """
        if blacklist is None:
            blacklist = []

        df_swap = self.fetch_all_tickers(inst_type='SWAP')
        if df_swap.empty:
            return self.top_20_symbols

        # 过滤只保留 USDT 永续合约 (排除 USDC 合约、交割合约等)
        df_usdt_swap = df_swap[df_swap['instId'].str.endswith('-USDT-SWAP')].copy()

        # 根据 24H 成交额排序（降序）
        df_sorted = df_usdt_swap.sort_values(by='volCcy24h', ascending=False)

        # 提取标的名称列表，例如 BTC-USDT-SWAP -> 去除后缀，如果需要在其他地方作为统一 symbol
        # 我们目前先保留完整 instId
        candidates = df_sorted['instId'].tolist()
        
        # 移出黑名单
        valid_top = [sym for sym in candidates if sym not in blacklist][:20]
        
        # 对比和更新
        old_top_20 = set(self.top_20_symbols)
        new_top_20 = set(valid_top)
        
        dropped = old_top_20 - new_top_20
        added = new_top_20 - old_top_20
        
        self.top_20_symbols = valid_top

        # 实际使用中，这里应该返回发生了怎样变化的字典，由 main 控制逻辑和发送推送
        return {
            "top_20": self.top_20_symbols,
            "added": list(added),
            "dropped": list(dropped)
        }
