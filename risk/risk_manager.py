import numpy as np

class RiskControlHub:
    def __init__(self, config):
        self.max_exposure = config.get("risk", {}).get("max_exposure_per_trade", 0.05)
        self.min_rr_ratio = config.get("risk", {}).get("min_rr_ratio", 2.0)
        
    def evaluate_signal(self, signal: dict) -> bool:
        """
        风控中枢
        signal 必须包含: target_price, stop_loss_price, current_price, win_rate
        """
        side = signal.get("side", "long")
        entry = signal["current_price"]
        tp = signal["target_price"]
        sl = signal["stop_loss_price"]
        win_rate = signal.get("win_rate", 0.4)
        
        # 计算潜在盈利和亏损
        if side == "long":
            pot_profit = tp - entry
            pot_loss = entry - sl
        else:
            pot_profit = entry - tp
            pot_loss = sl - entry
            
        if pot_loss <= 0:
            print(f"[{signal['symbol']}] 止损与入场价格不合理，风控拒绝")
            return False
            
        rr_ratio = pot_profit / pot_loss
        expected_value = (win_rate * pot_profit) - ((1 - win_rate) * pot_loss)
        
        if rr_ratio < self.min_rr_ratio:
            print(f"[{signal['symbol']}] 盈亏比 {rr_ratio:.2f} 极低 (要求 {self.min_rr_ratio})，风控拒绝")
            return False
            
        if expected_value <= 0:
            print(f"[{signal['symbol']}] 期望收益为负 {expected_value:.2f}，风控拒绝")
            return False
            
        print(f"[{signal['symbol']}] 信号通过风控校验, 盈亏比 {rr_ratio:.2f}, EV: {expected_value:.2f}")
        return True
