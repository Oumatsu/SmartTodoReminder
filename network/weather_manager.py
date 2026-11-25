import requests

# ---------------- 获取用户城市 ----------------
def get_user_city():
    try:
        url = "http://ip-api.com/json/"
        res = requests.get(url, timeout=5).json()
        return res.get("city", "Beijing")  # 默认北京
    except:
        return "Beijing"

# ---------------- 获取城市天气 ----------------
def get_weather(city):
    try:
        url = f"https://wttr.in/{city}?format=j1"
        res = requests.get(url, timeout=5).json()

        # 今天天气
        today = res["weather"][0]
        avg_temp = today["avgtempC"]
        desc = today["hourly"][0]["weatherDesc"][0]["value"]
        feels = today["hourly"][0]["FeelsLikeC"]

        weather_text = f"{city}  天气：{desc}，平均气温：{avg_temp}°C，体感温度：{feels}°C"
        return weather_text

    except:
        return f"{city} 天气获取失败"
