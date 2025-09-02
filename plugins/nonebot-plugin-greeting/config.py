from typing import List

# 定时时间，支持多个时间，格式为 HH:MM
greeting_scheduler_times = ["07:00", "23:00"]

# 不需要发送的群号列表（黑名单）
greeting_blacklist_groups = [12345678, 87654321]  # 请替换为实际不需要发送的群号

# API URL
image_api_url = "https://api.lolimi.cn/API/image-zw/api.php"

# 请求超时时间（秒）
request_timeout = 10

# 消息模板
morning_message = "早安喵w\n愿大家拥有美好的一天~"
evening_message = "晚安喵w\n祝大家好梦~"