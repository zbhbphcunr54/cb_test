import requests
import yaml
import os

# 读取配置
config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

print("config:", config)
WEBHOOKS = config.get('notify', {}).get('webhooks', {})

def send_text(group: str, content: str):
    """推送 markdown 文字消息到指定群"""
    webhook_url = WEBHOOKS.get(group)
    if not webhook_url or "YOUR_KEY" in webhook_url:
        print(f"[Warn] {group} Webhook 未配置, 消息: {content[:20]}...")
        return

    payload = {
        "msgtype": "markdown",
        "markdown": {"content": content}
    }
    try:
        response = requests.post(webhook_url, json=payload, timeout=5)
        response.raise_for_status()
    except Exception as e:
        print(f"[Error] 推送消息到 {group} 失败: {e}")

def send_to_all(content: str):
    """推送到所有群（风控告警等紧急消息）"""
    for group in WEBHOOKS:
        send_text(group, content)

def send_with_cc(primary_group: str, cc_groups: list, content: str):
    """推送到主群 + 抄送到其他群"""
    send_text(primary_group, content)
    for group in cc_groups:
        send_text(group, f"> **[抄送自 {primary_group} 群]**\n\n{content}")
