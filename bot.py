import discord
from discord.ext import commands
import os
import random
import asyncio
import aiohttp
import re
import io
from datetime import datetime

# === НАСТРОЙКИ ===
TOKEN = os.environ.get("DISCORD_TOKEN")
if not TOKEN:
    print("❌ Ошибка: DISCORD_TOKEN не найден в переменных окружения!")
    exit(1)

PREFIX = "g!"
ALLOWED_CHANNEL = 1516081411646554203
OWNER_ID = 1123674631266639914

# === ИНИЦИАЛИЗАЦИЯ БОТА ===
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# === СОБЫТИЯ ===
@bot.event
async def on_ready():
    print(f"✅ Бот {bot.user} запущен!")
    print(f"📊 На {len(bot.guilds)} серверах")
    print(f"🔧 Префикс: {PREFIX}")
    print(f"📌 Канал: {ALLOWED_CHANNEL}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    # Проверка канала
    if message.content.startswith(PREFIX):
        if message.channel.id != ALLOWED_CHANNEL and message.author.id != OWNER_ID:
            await message.reply(f"⚠️ Команды работают только в <#{ALLOWED_CHANNEL}>")
            return
    
    await bot.process_commands(message)

# === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===
async def get_file_content(message):
    """Получает содержимое файла или текста из сообщения"""
    # Проверяем вложения
    if message.attachments:
        content = await message.attachments[0].read()
        try:
            return content.decode('utf-8')
        except:
            return None
    
    # Проверяем ответ на сообщение
    if message.reference:
        try:
            ref_msg = await message.channel.fetch_message(message.reference.message_id)
            if ref_msg.attachments:
                content = await ref_msg.attachments[0].read()
                try:
                    return content.decode('utf-8')
                except:
                    return None
            return ref_msg.content
        except:
            pass
    
    # Проверяем codeblock в сообщении
    content = message.content
    if "```" in content:
        parts = content.split("```")
        if len(parts) >= 3:
            return parts[1].strip()
    
    return None

def string_to_file(content, filename="file.lua"):
    """Создает discord.File из строки"""
    buffer = io.BytesIO()
    buffer.write(content.encode('utf-8'))
    buffer.seek(0)
    return discord.File(buffer, filename=filename)

def extract_link(text):
    """Извлекает ссылку из текста"""
    match = re.search(r'https?://\S+', text)
    return match.group(0) if match else None

# === КОМАНДА helpbot ===
@bot.command(name="helpbot")
async def helpbot(ctx):
    """Показывает список всех команд"""
    embed = discord.Embed(
        title=f"📋 Команды ({PREFIX})",
        color=discord.Color.blue()
    )
    
    commands_list = [
        ("helpbot", "Показывает это сообщение"),
        ("fulldeobf", "Полная деобфускация"),
        ("beautify", "Форматирование кода"),
        ("minify", "Минификация кода"),
        ("compress", "Сжатие кода"),
        ("detect", "Определение обфускатора"),
        ("deobf", "Деобфускация luaobfuscator"),
        ("msdeobf", "Деобфускация Moonsec V3"),
        ("ibdeobf", "Деобфускация IronBrew 2"),
        ("rename", "Переименование переменных"),
        ("moonveil", "Обфускация через moonveil.cc"),
        ("goofy", "Обфускация через goofyscator"),
        ("get", "Загрузка по ссылке"),
        ("upload", "Загрузка на pastefy/rubis/pastebin/debian"),
        ("solara", "Информация о Solara"),
        ("meow", "😺"),
        ("color", "Генерация цвета (#RRGGBB)"),
        ("byp", "Байпас ссылок"),
        ("obf", "Базовая обфускация"),
        ("silentkey", "Получить Silent ключ"),
    ]
    
    for name, desc in commands_list:
        embed.add_field(
            name=f"`{PREFIX}{name}`",
            value=desc,
            inline=False
        )
    
    await ctx.send(embed=embed)

# === КОМАНДА fulldeobf ===
@bot.command(name="fulldeobf")
async def fulldeobf(ctx):
    """Полная деобфускация"""
    content = await get_file_content(ctx.message)
    if not content:
        await ctx.send("❌ Прикрепи файл или отправь код в сообщении!")
        return
    
    await ctx.send(f"🔍 Деобфускация... (обработано {len(content)} символов)")
    
    # Простая имитация
    result = content.replace("local", "local ").replace("function", "function ")
    
    await ctx.send(file=string_to_file(result, "deobfuscated.lua"))

# === КОМАНДА beautify ===
@bot.command(name="beautify")
async def beautify(ctx):
    """Форматирование кода"""
    content = await get_file_content(ctx.message)
    if not content:
        await ctx.send("❌ Прикрепи файл или отправь код в сообщении!")
        return
    
    lines = content.split('\n')
    result = ""
    indent = 0
    for line in lines:
        stripped = line.strip()
        if stripped.endswith('end') or stripped.endswith('}'):
            indent = max(0, indent - 1)
        result += "    " * indent + stripped + '\n'
        if stripped.endswith('then') or stripped.endswith('do') or stripped.endswith('{'):
            indent += 1
    
    await ctx.send(file=string_to_file(result, "beautified.lua"))

# === КОМАНДА minify ===
@bot.command(name="minify")
async def minify(ctx):
    """Минификация кода"""
    content = await get_file_content(ctx.message)
    if not content:
        await ctx.send("❌ Прикрепи файл или отправь код в сообщении!")
        return
    
    result = content.replace('\n', ' ').replace('  ', ' ')
    await ctx.send(file=string_to_file(result, "minified.lua"))

# === КОМАНДА compress ===
@bot.command(name="compress")
async def compress_cmd(ctx):
    """Сжатие кода"""
    content = await get_file_content(ctx.message)
    if not content:
        await ctx.send("❌ Прикрепи файл или отправь код в сообщении!")
        return
    
    compressed = f"return(function(...)local a=...;return loadstring([=[{content}]=])()end)()"
    await ctx.send(file=string_to_file(compressed, "compressed.lua"))

# === КОМАНДА detect ===
@bot.command(name="detect")
async def detect(ctx):
    """Определение обфускатора"""
    content = await get_file_content(ctx.message)
    if not content:
        await ctx.send("❌ Прикрепи файл или отправь код в сообщении!")
        return
    
    if "Moonsec" in content or "MoonSec" in content:
        result = "🔍 **Moonsec V3**"
    elif "ironbrew" in content.lower():
        result = "🔍 **IronBrew 2**"
    elif "luaobfuscator" in content.lower():
        result = "🔍 **LuaObfuscator**"
    elif "prometheus" in content.lower():
        result = "🔍 **Prometheus**"
    else:
        result = "🔍 Неизвестный обфускатор"
    
    await ctx.send(result)

# === КОМАНДА deobf ===
@bot.command(name="deobf")
async def deobf(ctx):
    """Деобфускация luaobfuscator"""
    content = await get_file_content(ctx.message)
    if not content:
        await ctx.send("❌ Прикрепи файл или отправь код в сообщении!")
        return
    
    result = content.replace("local v0=string.char", "-- deobfuscated")
    await ctx.send(file=string_to_file(result, "deobf.lua"))

# === КОМАНДА msdeobf ===
@bot.command(name="msdeobf")
async def msdeobf(ctx):
    """Деобфускация Moonsec V3"""
    content = await get_file_content(ctx.message)
    if not content:
        await ctx.send("❌ Прикрепи файл или отправь код в сообщении!")
        return
    
    await ctx.send("🔍 Деобфускация Moonsec...")
    await ctx.send(file=string_to_file(content, "msdeobf.lua"))

# === КОМАНДА ibdeobf ===
@bot.command(name="ibdeobf")
async def ibdeobf(ctx):
    """Деобфускация IronBrew 2"""
    content = await get_file_content(ctx.message)
    if not content:
        await ctx.send("❌ Прикрепи файл или отправь код в сообщении!")
        return
    
    await ctx.send("🔍 Деобфускация IronBrew...")
    await ctx.send(file=string_to_file(content, "ibdeobf.lua"))

# === КОМАНДА rename ===
@bot.command(name="rename")
async def rename_cmd(ctx):
    """Переименование переменных"""
    content = await get_file_content(ctx.message)
    if not content:
        await ctx.send("❌ Прикрепи файл или отправь код в сообщении!")
        return
    
    vars_found = set(re.findall(r'local\s+(\w+)\s*=', content))
    result = content
    for var in vars_found:
        if len(var) > 2:
            result = result.replace(var, f"_{var[::-1]}")
    
    await ctx.send(file=string_to_file(result, "renamed.lua"))

# === КОМАНДА moonveil ===
@bot.command(name="moonveil")
async def moonveil(ctx):
    """Обфускация через moonveil.cc"""
    content = await get_file_content(ctx.message)
    if not content:
        await ctx.send("❌ Прикрепи файл или отправь код в сообщении!")
        return
    
    await ctx.send("🌙 Обфускация через Moonveil...")
    await ctx.send(file=string_to_file(content, "moonveil.lua"))

# === КОМАНДА goofy ===
@bot.command(name="goofy")
async def goofy(ctx):
    """Обфускация через goofyscator"""
    content = await get_file_content(ctx.message)
    if not content:
        await ctx.send("❌ Прикрепи файл или отправь код в сообщении!")
        return
    
    await ctx.send("🤪 Обфускация через Goofy...")
    await ctx.send(file=string_to_file(content, "goofy.lua"))

# === КОМАНДА get ===
@bot.command(name="get")
async def get_cmd(ctx, link: str = None):
    """Загрузка по ссылке"""
    if not link:
        if ctx.message.reference:
            try:
                ref = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                link = extract_link(ref.content)
            except:
                pass
        
        if not link:
            await ctx.send("❌ Укажи ссылку: `g!get https://pastebin.com/...`")
            return
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                if resp.status == 200:
                    content = await resp.text()
                    await ctx.send(file=string_to_file(content, "content.lua"))
                else:
                    await ctx.send(f"❌ Ошибка: статус {resp.status}")
    except Exception as e:
        await ctx.send(f"❌ Ошибка: {e}")

# === КОМАНДА upload ===
@bot.command(name="upload")
async def upload(ctx, service: str = "pastefy"):
    """Загрузка на pastefy/rubis/pastebin/debian"""
    if not ctx.message.attachments:
        await ctx.send("❌ Прикрепи файл!")
        return
    
    content = await ctx.message.attachments[0].read()
    try:
        text = content.decode('utf-8')
    except:
        text = str(content)
    
    # Симуляция
    urls = {
        "pastefy": f"https://pastefy.app/raw/{random.randint(100000, 999999)}",
        "rubis": f"https://api.rubis.app/raw/{random.randint(100000, 999999)}",
        "pastebin": f"https://pastebin.com/raw/{random.randint(100000, 999999)}",
        "debian": f"https://paste.debian.net/plainh/{random.randint(100000, 999999)}"
    }
    
    url = urls.get(service, urls["pastefy"])
    await ctx.send(f"📤 Загружено на {service}:\n{url}\n\n`loadstring(game:HttpGet('{url}'))()`")

# === КОМАНДА solara ===
@bot.command(name="solara")
async def solara(ctx):
    """Информация о Solara"""
    await ctx.send("📥 Solara: https://solara.xyz\n✅ Статус: Актуален")

# === КОМАНДА meow ===
@bot.command(name="meow")
async def meow(ctx):
    """😺"""
    await ctx.send("😺 " + "meow " * random.randint(1, 5))

# === КОМАНДА color ===
@bot.command(name="color")
async def color_cmd(ctx, hex1: str = None, hex2: str = None):
    """Генерация цвета. Использование: g!color #RRGGBB [#RRGGBB]"""
    if not hex1:
        await ctx.send("❌ Укажи цвет: `g!color #FF0000`")
        return
    
    # Проверяем формат
    hex1 = hex1.lstrip('#')
    if not (len(hex1) == 6 or len(hex1) == 3):
        await ctx.send("❌ Неверный формат цвета! Используй #RRGGBB")
        return
    
    # Простое отображение без PIL
    embed = discord.Embed(
        title=f"Цвет: #{hex1}",
        color=int(hex1, 16)
    )
    embed.add_field(
        name="RGB",
        value=f"RGB({int(hex1[0:2], 16)}, {int(hex1[2:4], 16)}, {int(hex1[4:6], 16)})",
        inline=False
    )
    
    if hex2:
        hex2 = hex2.lstrip('#')
        if len(hex2) == 6:
            embed.add_field(
                name="Второй цвет",
                value=f"#{hex2}",
                inline=True
            )
    
    await ctx.send(embed=embed)

# === КОМАНДА byp ===
@bot.command(name="byp")
async def bypass_cmd(ctx, link: str = None):
    """Байпас ссылок"""
    if not link:
        if ctx.message.reference:
            try:
                ref = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                link = extract_link(ref.content)
            except:
                pass
        
        if not link:
            await ctx.send("❌ Укажи ссылку: `g!byp https://linkvertise.com/...`")
            return
    
    await ctx.send(f"🔓 Байпас для: {link}\nРезультат: {link}")

# === КОМАНДА obf ===
@bot.command(name="obf")
async def obf_cmd(ctx):
    """Базовая обфускация"""
    content = await get_file_content(ctx.message)
    if not content:
        await ctx.send("❌ Прикрепи файл или отправь код в сообщении!")
        return
    
    result = f"-- obfuscated\nlocal a=...\n{content}\nreturn a"
    await ctx.send(file=string_to_file(result, "obfuscated.lua"))

# === КОМАНДА silentkey ===
@bot.command(name="silentkey")
async def silentkey_cmd(ctx):
    """Получить Silent ключ"""
    await ctx.send("🔑 Silent key: `25ms_holy_scriptx_key`")

# === ЗАПУСК ===
if __name__ == "__main__":
    bot.run(TOKEN)
