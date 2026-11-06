import discord
from discord.ext import commands

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

    # 檢查訊息內容是否包含特定關鍵字
    if "早安" in message.content:
        # 注意：discord.py 標準發送訊息是用 message.channel.send
        await message.channel.send(f"早安呀，{message.author.mention}！今天也要加油！")
    
    # 務必加上這行，否則下方用 @bot.command() 寫的自訂指令會失效！
    await bot.process_commands(message)

# 5. 建立自訂指令：!ping
@bot.command()
async def ping(ctx):
    await ctx.send("Pong! 🏓")

# 6. 建立帶參數的自訂指令：!say [文字]
@bot.command(name="say")
async def say_something(ctx, *, text: str):
    # 刪除使用者傳送的原始指令訊息，並由機器人覆誦
    await ctx.message.delete()
    await ctx.send(f"使用者說：{text}")

# 7. 啟動機器人（請將引號內的文字替換成你的 Bot Token）
bot.run("你的_BOT_TOKEN_貼在這裡")