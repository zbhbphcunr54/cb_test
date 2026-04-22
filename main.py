import time
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from notify.wechat import send_text, send_with_cc

from data.market_scanner import OKXMarketScanner
from db.database import SessionLocal, MarketData
from risk.risk_manager import RiskControlHub
from engines.p1_medium import MediumLongTermEngine
from engines.p2_anomaly import AnomalyDetectionEngine
from engines.p3_short import ShortTermEngine
from engines.p4_wave import WaveAnalysisEngine

scanner = OKXMarketScanner()
risk_manager = RiskControlHub({"risk": {"max_exposure_per_trade": 0.05, "min_rr_ratio": 2.0}})
engines = {
    "p1": MediumLongTermEngine([]),
    "p2": AnomalyDetectionEngine(),
    "p3": ShortTermEngine([]),
    "p4": WaveAnalysisEngine([])
}

def system_heartbeat():
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"🟢 **系统心跳正常**\n>\n>时间: {current_time}\n>状态: 全系引擎挂载运行中"
    send_text("system", msg)
    print(f"[{current_time}] 心跳已发送")

def update_top20_job():
    print("[Task] 执行动态 Top 20 更新...")
    result = scanner.update_top_20()
    engines["p1"].symbols = result.get("top_20", [])
    engines["p3"].symbols = result.get("top_20", [])
    engines["p4"].symbols = result.get("top_20", [])
    
    add_str = ", ".join(result.get("added", [])) if result.get("added") else "无"
    drop_str = ", ".join(result.get("dropped", [])) if result.get("dropped") else "无"
    
    total_msg = f"🌟 **今日 Top 20 币种更新**\n\n**新增**: {add_str}\n**掉出**: {drop_str}"
    send_with_cc("system", ["medium_long"], total_msg)

def scan_market_job():
    print("[Task] 正在同步市场数据与全盘异动捕捉扫描...")
    # TODO：接入 K线 / REST API，目前执行轻量化测试
    pass

def analyze_medium_long():
    print("[Task] 执行 P1 中长线引擎...")
    pass

def wave_analysis_job():
    print("[Task] 执行 P4 波浪绘制分析...")
    pass

def main():
    print("启动系统...")
    scheduler = BackgroundScheduler()
    scheduler.add_job(system_heartbeat, "interval", hours=6)
    scheduler.add_job(update_top20_job, "cron", hour=0, minute=5, timezone="UTC")
    scheduler.add_job(scan_market_job, "interval", minutes=15)
    
    scheduler.add_job(analyze_medium_long, "interval", hours=4)
    scheduler.add_job(wave_analysis_job, "interval", hours=1)

    scheduler.start()
    
    # 立即获取一次
    update_top20_job()
    send_text("system", "🚀 **全模块引擎已挂载启动 (v2.0)**")
    
    try:
        while True:
            time.sleep(1)
    except:
        pass
    finally:
        scheduler.shutdown()

if __name__ == "__main__":
    main()

