from flask import Flask, request, jsonify, make_response, render_template
import requests
import json

app = Flask(__name__)

# 模擬的電影資料庫
movies = [
    {"title": "玩具總動員", "length": 81, "rating": "普遍級", "picture": "https://example.com/toy1.jpg", "showDate": "1995-11-22"},
    {"title": "玩具總動員2", "length": 92, "rating": "普遍級", "picture": "https://example.com/toy2.jpg", "showDate": "1999-11-24"},
    {"title": "玩具總動員3", "length": 103, "rating": "普遍級", "picture": "https://example.com/toy3.jpg", "showDate": "2010-06-18"},
    {"title": "玩具總動員4", "length": 100, "rating": "普遍級", "picture": "https://example.com/toy4.jpg", "showDate": "2019-06-21"},
    {"title": "阿凡達", "length": 162, "rating": "保護級", "picture": "https://example.com/avatar.jpg", "showDate": "2009-12-18"},
]

# 首頁 - 顯示說明
@app.route("/")
def home():
    return """
    <h1>Dialogflow Webhook 伺服器</h1>
    <p>✅ 服務正常運作中</p>
    <p>📌 Webhook 網址：<code>/webhook</code></p>
    <p>💬 聊天測試頁面：<a href='/webdemo'>/webdemo</a></p>
    <h2>測試指令：</h2>
    <ul>
        <li>片名是玩具總動員</li>
        <li>片名是阿凡達</li>
        <li>片長是120分鐘</li>
    </ul>
    """

# 聊天測試頁面
@app.route("/webdemo")
def webdemo():
    return render_template("webdemo.html")

# Dialogflow Webhook 端點
@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json(force=True)
    action = req["queryResult"]["action"]
    
    if action == "MovieDetail":
        filmq = req["queryResult"]["parameters"].get("filmq")
        keyword = req["queryResult"]["parameters"].get("any")
        
        reply_text = f"🎬 您要查詢電影的 {filmq}，關鍵字是：{keyword}\n\n"
        
        # 查詢片名
        if filmq == "片名":
            found_movies = [m for m in movies if keyword in m["title"]]
            
            if found_movies:
                for m in found_movies:
                    reply_text += f"📽️ 片名：{m['title']}\n"
                    reply_text += f"⏱️ 片長：{m['length']} 分鐘\n"
                    reply_text += f"🔞 分級：{m['rating']}\n"
                    reply_text += f"📅 上映日期：{m['showDate']}\n"
                    reply_text += f"🖼️ 海報：{m['picture']}\n"
                    reply_text += "-" * 30 + "\n"
            else:
                reply_text += "❌ 很抱歉，目前無符合這個關鍵字的相關電影喔"
        
        # 查詢片長
        elif filmq == "片長":
            reply_text += f"⏰ 您想查詢片長為 {keyword} 的電影\n\n"
            # 嘗試提取數字（例如 "120分鐘" -> 120）
            import re
            numbers = re.findall(r'\d+', keyword)
            if numbers:
                target_length = int(numbers[0])
                found_movies = [m for m in movies if abs(m["length"] - target_length) <= 10]
                
                if found_movies:
                    reply_text += f"找到片長接近 {target_length} 分鐘的電影：\n\n"
                    for m in found_movies:
                        reply_text += f"📽️ {m['title']}（{m['length']} 分鐘）\n"
                else:
                    reply_text += "❌ 沒有找到片長接近的電影"
            else:
                reply_text += "❌ 請輸入數字，例如：120分鐘"
        
        else:
            reply_text += "🤔 我還不知道怎麼查詢這個項目"
    
    elif action == "CityWeather":
        city = req["queryResult"]["parameters"].get("city")
        
        # 模擬天氣資料（真實 API 需要申請 token）
        weather_data = {
            "臺中市": {"weather": "晴時多雲", "rain": 20, "temp": "22-28"},
            "臺北市": {"weather": "陰短暫雨", "rain": 60, "temp": "18-24"},
            "新北市": {"weather": "陰短暫雨", "rain": 65, "temp": "18-23"},
            "桃園市": {"weather": "多雲", "rain": 30, "temp": "19-25"},
            "臺南市": {"weather": "晴時多雲", "rain": 10, "temp": "23-30"},
            "高雄市": {"weather": "晴", "rain": 5, "temp": "24-31"},
        }
        
        if city in weather_data:
            w = weather_data[city]
            reply_text = f"🌤️ {city}的天氣是{w['weather']}，降雨機率：{w['rain']}%，溫度：{w['temp']}度"
        else:
            reply_text = f"❌ 找不到 {city} 的天氣資訊，請輸入六都之一"
    
    else:
        reply_text = "🤖 我是電影聊天機器人，你可以問我：\n- 片名是XXX\n- 片長是120分鐘"
    
    return make_response(jsonify({"fulfillmentText": reply_text}))

# 簡易聊天 API（給 webdemo 用）
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    
    # 簡單的關鍵字比對（模擬 Dialogflow）
    if "片名" in user_message and "是" in user_message:
        keyword = user_message.split("是")[-1].strip()
        found_movies = [m for m in movies if keyword in m["title"]]
        
        if found_movies:
            reply = f"找到 {len(found_movies)} 部電影：\n"
            for m in found_movies:
                reply += f"• {m['title']}（{m['length']}分鐘）\n"
        else:
            reply = f"找不到包含「{keyword}」的電影"
    
    elif "天氣" in user_message:
        reply = "請告訴我城市名稱，例如：台中天氣"
    
    else:
        reply = "你可以試試看問我：片名是玩具總動員"
    
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True)
