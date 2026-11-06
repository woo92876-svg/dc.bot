import os
import random
import time
from collections import defaultdict
import discord
from discord.ext import commands

# 追蹤每個使用者的標記記錄：{ user_id: [timestamp1, timestamp2, ...] }
mention_timestamps = defaultdict(list)
# 記錄被暫停服務的使用者：{ user_id: unban_timestamp }
banned_users = {}

# 1. 啟用訊息內容意圖 (Intent)
intents = discord.Intents.default()
intents.message_content = True

# 2. 建立機器人物件，設定指令前綴為 "!"
bot = commands.Bot(command_prefix="!", intents=intents)

# 3. 當機器人成功連線登入時觸發
@bot.event
async def on_ready():
    print(f"機器人已成功登入：{bot.user}")

# 4. 監聽一般聊天訊息（關鍵字自動回覆）
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
            # 還在 10 分鐘懲罰期內，直接忽略他的訊息
            return
        else:
            # 超過 10 分鐘，解除禁言並清空記錄
            del banned_users[user_id]
            mention_timestamps[user_id] = []

    # 檢查是否被 @ 標記
    if bot.user in message.mentions:
        # 清理 5 分鐘（300秒）以前的舊記錄
        mention_timestamps[user_id] = [t for t in mention_timestamps[user_id] if current_time - t < 300]
        
        # 記錄這次的標記時間
        mention_timestamps[user_id].append(current_time)

        # 檢查 5 分鐘內是否達到 5 次以上
        if len(mention_timestamps[user_id]) >= 5:
            # 設為暫停服務 10 分鐘（600秒）後解除
            banned_users[user_id] = current_time + 600
            await message.channel.send(f"{message.author.mention} 吵死了！洗版太快，本喵暫停服務你 10 分鐘！ 😾")
            return
        else:
            await message.channel.send(f"{message.author.mention}不要吵本喵！")

    # 檢查訊息內容是否包含特定關鍵字
    if "流行" in message.content:
        await message.channel.send(f"{message.author.mention}有人提到妹子!!")
    
    # 務必加上這行，否則下方用 @bot.command() 寫的自訂指令會失效！
    await bot.process_commands(message)

# 5. 抽籤指令
@bot.command(name="抽籤")
async def draw_lots(ctx):
    # 定義抽籤的結果選項
    results = ["大吉", "吉", "平", "凶", "大凶"]
    
    # 從選項中隨機挑選一個
    chosen = random.choice(results)
    
    # 回覆給使用者，並標記對方
    await ctx.send(f"🔮 {ctx.author.mention} 抽到的運勢是：**{chosen}**！")

# 6. 從 Render 的環境變數安全讀取 Token（解決 401 錯誤與保護帳號）
token = os.getenv("DISCORD_TOKEN")
if token is None:
    print("錯誤：找不到 DISCORD_TOKEN 環境變數！請到 Render 後台設定。")
else:
    bot.run(token)