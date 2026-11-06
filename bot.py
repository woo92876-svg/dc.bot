import os
import random
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from collections import defaultdict
import discord
from discord.ext import commands

# ==================== 1. 建立假網頁伺服器（用來騙過 Render 的 Port 檢測） ====================
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_server():
    # Render 會透過環境變數 PORT 指定連接埠，預設給 10000
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    server.serve_forever()

# 讓網頁伺服器在背景獨立執行，不影響 Discord 機器人
server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()


# ==================== 2. Discord 機器人核心邏輯 ====================
# 追蹤每個使用者的標記記錄：{ user_id: [timestamp1, timestamp2, ...] }
mention_timestamps = defaultdict(list)
# 記錄被暫停服務的使用者：{ user_id: unban_timestamp }
banned_users = {}

# 啟用訊息內容意圖 (Intent)
intents = discord.Intents.default()
intents.message_content = True

# 建立機器人物件，設定指令前綴為 "!"
bot = commands.Bot(command_prefix="!", intents=intents)

# 當機器人成功連線登入時觸發
@bot.event
async def on_ready():
    print(f"機器人已成功登入：{bot.user}")

# 監聽一般聊天訊息（關鍵字自動回覆與防洗版）
@bot.event
async def on_message(message):
    # 避免機器人自己跟自己對話造成無限迴圈
    if message.author == bot.user:
        return

    user_id = message.author.id
    current_time = time.time()

    # 檢查該使用者是否正在被禁言（暫停服務中）
    if user_id in banned_users:
        if current_time < banned_users[user_id]:
            return
        else:
            del banned_users[user_id]
            mention_timestamps[user_id] = []

    # 檢查是否被 @ 標記
    if bot.user in message.mentions:
        mention_timestamps[user_id] = [t for t in mention_timestamps[user_id] if current_time - t < 300]
        mention_timestamps[user_id].append(current_time)

        if len(mention_timestamps[user_id]) >= 5:
            banned_users[user_id] = current_time + 600
            await message.channel.send(f"{message.author.mention} 吵死了！洗版太快，本喵暫停服務你 10 分鐘！ 😾")
            return
        else:
            await message.channel.send(f"{message.author.mention}不要吵本喵！")

    # 檢查訊息內容是否包含特定關鍵字
    if "流行" in message.content:
        await message.channel.send(f"{message.author.mention}有人提到妹子!!")
    
    # 確保自訂指令（如 !抽籤）可以正常運作
    await bot.process_commands(message)

# 抽籤指令
@bot.command(name="抽籤")
async def draw_lots(ctx):
    results = ["大吉", "吉", "平", "凶", "大凶"]
    chosen = random.choice(results)
    await ctx.send(f"🔮 {ctx.author.mention} 抽到的運勢是：**{chosen}**！")


# ==================== 3. 啟動機器人 ====================
token = os.getenv("DISCORD_TOKEN")
if token is None:
    print("錯誤：找不到 DISCORD_TOKEN 環境變數！")
else:
    bot.run(token)