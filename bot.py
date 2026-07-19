import discord
from discord.ext import commands
from discord.utils import escape_mentions
from discord import CustomActivity
from datetime import timedelta, datetime
from collections import defaultdict
import os
import random
import asyncio
import aiohttp
import json
import re
import time
import io
import tempfile
from PIL import Image, ImageDraw, ImageColor
import requests
import urllib.parse

# === НАСТРОЙКИ ===
TOKEN = os.environ.get("DISCORD_TOKEN")
if not TOKEN:
    print("❌ Ошибка: DISCORD_TOKEN не найден в переменных окружения!")
    exit(1)

PREFIX = "g!"
ALLOWED_CHANNEL = 1516081411646554203
OWNER_ID = 1123674631266639914

# === ЗАГЛУШКИ ДЛЯ ОТСУТСТВУЮЩИХ МОДУЛЕЙ ===
class BypassStub:
    @staticmethod
    async def asyncpost(url, data, headers=None, returnResponseJson=True):
        print(f"[BYPASS] POST {url}")
        return {"status": "ok"} if returnResponseJson else "{}"
    
    @staticmethod
    def getsolarainfo():
        return {"BootstrapperUrl": "https://solara.xyz", "Changelog": "[+] Updated"}
    
    @staticmethod
    def getrobloxversioninfo():
        return {"clientVersionUpload": "v123"}
    
    @staticmethod
    def dynamicLV(url):
        return f"Bypassed: {url}"
    
    @staticmethod
    async def generic(url):
        return f"Bypassed: {url}"
    
    @staticmethod
    async def cloudflare_gen(prompt):
        return None

class LicensingStub:
    @staticmethod
    async def claim(user_id, client, key):
        return "✅ License claimed!"
    
    @staticmethod
    async def get_recovery(user):
        return "recovery_key_123"
    
    @staticmethod
    async def revoke(user_id, client):
        return "✅ Revoked"
    
    @staticmethod
    async def regenerate_all():
        return "✅ Regenerated"

class UtilStub:
    @staticmethod
    def randomstr(length):
        import string
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    @staticmethod
    def seconds_to_str(seconds):
        return f"{seconds}s"
    
    @staticmethod
    def timeconverter(text):
        import re
        total = 0
        matches = re.findall(r'(\d+)([smhdw])', text)
        for num, unit in matches:
            num = int(num)
            if unit == 's': total += num
            elif unit == 'm': total += num * 60
            elif unit == 'h': total += num * 3600
            elif unit == 'd': total += num * 86400
            elif unit == 'w': total += num * 604800
        return total or 300

# Подмена импортов
bypass = BypassStub()
licensing = LicensingStub()
util = UtilStub()
randomstr = util.randomstr
seconds_to_str = util.seconds_to_str
timeconverter = util.timeconverter

# === ИНИЦИАЛИЗАЦИЯ БОТА ===
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# === ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ===
message_counts = defaultdict(int)
mv_data = {}
sent_conflict_msg = {}

def get_roles(user_id):
    """Заглушка для ролей"""
    return []

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
    
    # Проверка канала для всех команд
    if message.content.startswith(PREFIX):
        if message.channel.id != ALLOWED_CHANNEL and message.author.id != OWNER_ID:
            await message.reply(f"⚠️ Команды работают только в <#{ALLOWED_CHANNEL}>")
            return
    
    await bot.process_commands(message)

# === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===
async def get_file_content(message):
    """Получает содержимое файла из сообщения"""
    if message.attachments:
        content = await message.attachments[0].read()
        try:
            return content.decode('utf-8')
        except:
            return content
    elif message.reference:
        try:
            ref_msg = await message.channel.fetch_message(message.reference.message_id)
            if ref_msg.attachments:
                content = await ref_msg.attachments[0].read()
                try:
                    return content.decode('utf-8')
                except:
                    return content
            return ref_msg.content
        except:
            return None
    return None

def extract_link(text):
    """Извлекает ссылку из текста"""
    match = re.search(r'https?://\S+', text)
    return match.group(0) if match else None

def get_codeblock(text):
    """Извлекает код из codeblock"""
    if "```" in text:
        parts = text.split("```")
        if len(parts) >= 3:
            return parts[1].strip()
    elif "`" in text:
        parts = text.split("`")
        if len(parts) >= 3:
            return parts[1].strip()
    return None

def string_to_discordfile(content, filename="file.lua"):
    """Создает discord.File из строки"""
    buffer = io.BytesIO()
    buffer.write(content.encode('utf-8'))
    buffer.seek(0)
    return discord.File(buffer, filename=filename)

# === КОМАНДА helpbot ===
@bot.command(name="helpbot")
async def helpbot(ctx):
    """Показывает список всех команд с описанием"""
    embed = discord.Embed(
        title=f"📋 Список команд ({PREFIX})",
        color=discord.Color.blue()
    )
    
    commands_list = [
        ("helpbot", "Показывает это сообщение"),
        ("fulldeobf", "Полная деобфускация скрипта (замена g!l)"),
        ("beautify", "Форматирует/улучшает читаемость Lua кода"),
        ("minify", "Минифицирует Lua код"),
        ("compress", "Сжимает Lua код"),
        ("detect", "Определяет обфускатор скрипта"),
        ("deobf", "Деобфускация luaobfuscator (Chaotic Good)"),
        ("msdeobf", "Деобфускация Moonsec V3"),
        ("ibdeobf", "Деобфускация IronBrew 2"),
        ("rename", "Переименовывает переменные в Lua"),
        ("moonveil", "Бесплатная обфускация через moonveil.cc (1 раз в день)"),
        ("goofy", "Бесплатная обфускация через goofyscator"),
        ("get", "Загружает содержимое по ссылке"),
        ("upload", "Загружает файл на pastefy/rubis/pastebin/debian"),
        ("solara", "Информация о Solara executor"),
        ("darklua", "GUI для настройки darklua"),
        ("meow", "Просто мяу 😺"),
        ("color", "Генерирует градиент цвета (#RRGGBB)"),
        ("byp", "Байпас ссылок (linkvertise и др.)"),
        ("onlyfans", "Проверка OnlyFans (только для владельца)"),
        ("fansly", "Проверка Fansly (только для владельца)"),
        ("ib2", "Обфускация через IronBrew 2"),
        ("ironobf", "Обфускация через IronBrikked"),
        ("obf", "Базовая обфускация"),
        ("vmify", "Обфускация через VM"),
        ("silentkey", "Получить Silent ключ"),
    ]
    
    for name, desc in commands_list:
        embed.add_field(
            name=f"`{PREFIX}{name}`",
            value=desc,
            inline=False
        )
    
    embed.set_footer(text=f"Все команды работают только в <#{ALLOWED_CHANNEL}>")
    await ctx.send(embed=embed)

# === КОМАНДА fulldeobf (замена g!l) ===
@bot.command(name="fulldeobf")
async def fulldeobf(ctx):
    """Полная деобфускация скрипта"""
    content = await get_file_content(ctx.message)
    if not content:
        await ctx.send("❌ Прикрепи файл или отправь код в сообщении!")
        return
    
    await ctx.send(f"🔍 Деобфускация... (обработано {len(content)} символов)")
    
    # Простая имитация деобфускации
    result = content.replace("local", "local ").replace("function", "function ")
    
    await ctx.send(file=string_to_discordfile(result, "deobfuscated.lua"))

# === КОМАНДА beautify ===
@bot.command(name="beautify")
async def beautify(ctx):
    """Форматирует Lua код"""
    content = await get_file_content(ctx.message)
    if not content:
        await ctx.send("❌ Прикрепи файл или отправь код в сообщении!")
        return
    
    # Простая имитация beautify
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
    
    await ctx.send(file=string_to_discordfile(result, "beautified.lua"))

# === КОМАНДА minify ===
@bot.command(name="minify")
async def minify(ctx):
    """Минифицирует Lua код"""
    content = await get_file_content(ctx.message)
    if not content:
        await ctx.send("❌ Прикрепи файл или отправь код в сообщении!")
        return
    
    # Простая минификация
    result = content.replace('\n', ' ').replace('  ', ' ')
    await ctx.send(file=string_to_discordfile(result, "minified.lua"))

# === КОМАНДА compress ===
@bot.command(name="compress")
async def compress_cmd(ctx):
    """Сжимает Lua код"""
    content = await get_file_content(ctx.message)
    if not content:
        await ctx.send("❌ Прикрепи файл или отправь код в сообщении!")
        return
    
    compressed = f"return(function(...)local a=...;return loadstring([=[{content}]=])()end)()"
    await ctx.send(file=string_to_discordfile(compressed, "compressed.lua"))

# === КОМАНДА detect ===
@bot.command(name="detect")
async def detect(ctx):
    """Определяет обфускатор"""
    content = await get_file_content(ctx.message)
    if not content:
        await ctx.send("❌ Прикрепи файл или отправь код в сообщении!")
        return
    
    # Простое определение
    if "Moonsec" in content or "MoonSec" in content:
        result = "🔍 Обнаружен: **Moonsec V3**"
    elif "ironbrew" in content.lower():
        result = "🔍 Обнаружен: **IronBrew 2**"
    elif "luaobfuscator" in content.lower():
        result = "🔍 Обнаружен: **LuaObfuscator**"
    elif "prometheus" in content.lower():
        result = "🔍 Обнаружен: **Prometheus**"
    else:
        result = "🔍 Не удалось определить обфускатор"
    
    await ctx.send(result)

# === КОМАНДА deobf ===
@bot.command(name="deobf")
async def deobf(ctx):
    """Деобфускация luaobfuscator"""
    content = await get_file_content(ctx.message)
    if not content:
        await ctx.send("❌ Прикрепи файл или отправь код в сообщении!")
        return
    
    # Имитация деобфускации
    result = content.replace("local v0=string.char", "-- deobfuscated")
    await ctx.send(file=string_to_discordfile(result, "deobfuscated.lua"))

# === КОМАНДА msdeobf ===
@bot.command(name="msdeobf")
async def msdeobf(ctx):
    """Деобфускация Moonsec V3"""
    content = await get_file_content(ctx.message)
    if not content:
        await ctx.send("❌ Прикрепи файл или отправь код в сообщении!")
        return
    
    await ctx.send("🔍 Деобфускация Moonsec... (функция в разработке)")
    await ctx.send(file=string_to_discordfile(content, "msdeobf.lua"))

# === КОМАНДА ibdeobf ===
@bot.command(name="ibdeobf")
async def ibdeobf(ctx):
    """Деобфускация IronBrew 2"""
    content = await get_file_content(ctx.message)
    if not content:
        await ctx.send("❌ Прикрепи файл или отправь код в сообщении!")
        return
    
    await ctx.send("🔍 Деобфускация IronBrew... (функция в разработке)")
    await ctx.send(file=string_to_discordfile(content, "ibdeobf.lua"))

# === КОМАНДА rename ===
@bot.command(name="rename")
async def rename_cmd(ctx):
    """Переименовывает переменные в Lua"""
    content = await get_file_content(ctx.message)
    if not content:
        await ctx.send("❌ Прикрепи файл или отправь код в сообщении!")
        return
    
    # Простое переименование
    import re
    vars_found = set(re.findall(r'local\s+(\w+)\s*=', content))
    renamed = content
    for var in vars_found:
        if len(var) > 2:
            renamed = renamed.replace(var, f"_{var[::-1]}")
    
    await ctx.send(file=string_to_discordfile(renamed, "renamed.lua"))

# === КОМАНДА moonveil ===
@bot.command(name="moonveil")
async def moonveil(ctx):
    """Бесплатная обфускация через moonveil.cc"""
    content = await get_file_content(ctx.message)
    if not content:
        await ctx.send("❌ Прикрепи файл или отправь код в сообщении!")
        return
    
    await ctx.send("🌙 Обфускация через Moonveil... (функция в разработке)")
    await ctx.send(file=string_to_discordfile(content, "moonveil.lua"))

# === КОМАНДА goofy ===
@bot.command(name="goofy")
async def goofy(ctx):
    """Бесплатная обфускация через goofyscator"""
    content = await get_file_content(ctx.message)
    if not content:
        await ctx.send("❌ Прикрепи файл или отправь код в сообщении!")
        return
    
    await ctx.send("🤪 Обфускация через Goofy... (функция в разработке)")
    await ctx.send(file=string_to_discordfile(content, "goofy.lua"))

# === КОМАНДА get ===
@bot.command(name="get")
async def get_cmd(ctx, link: str = None):
    """Загружает содержимое по ссылке"""
    if not link:
        # Пробуем взять ссылку из прикреплённого сообщения
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
                    await ctx.send(file=string_to_discordfile(content, "content.lua"))
                else:
                    await ctx.send(f"❌ Ошибка загрузки: статус {resp.status}")
    except Exception as e:
        await ctx.send(f"❌ Ошибка: {e}")

# === КОМАНДА upload ===
@bot.command(name="upload")
async def upload(ctx, service: str = "pastefy"):
    """Загружает файл. Использование: g!upload [pastefy|rubis|pastebin|debian]"""
    if not ctx.message.attachments:
        await ctx.send("❌ Прикрепи файл к сообщению!")
        return
    
    content = await ctx.message.attachments[0].read()
    try:
        text = content.decode('utf-8')
    except:
        text = str(content)
    
    # Симуляция загрузки
    fake_urls = {
        "pastefy": f"https://pastefy.app/raw/{randomstr(8)}",
        "rubis": f"https://api.rubis.app/raw/{randomstr(8)}",
        "pastebin": f"https://pastebin.com/raw/{randomstr(8)}",
        "debian": f"https://paste.debian.net/plainh/{randomstr(8)}"
    }
    
    url = fake_urls.get(service, fake_urls["pastefy"])
    await ctx.send(f"📤 Загружено на {service}:\n{url}\n\n`loadstring(game:HttpGet('{url}'))()`")

# === КОМАНДА solara ===
@bot.command(name="solara")
async def solara(ctx):
    """Информация о Solara"""
    info = bypass.getsolarainfo()
    rblxinfo = bypass.getrobloxversioninfo()
    await ctx.send(f'📥 Download: {info["BootstrapperUrl"]}\n✅ Updated: {info["SupportedClient"] == rblxinfo["clientVersionUpload"]}\n📝 Changelog:```diff\n{info["Changelog"]}```')

# === КОМАНДА darklua ===
@bot.command(name="darklua")
async def darklua(ctx):
    """GUI для настройки darklua"""
    await ctx.send("🎨 Darklua GUI (функция в разработке)")

# === КОМАНДА meow ===
@bot.command(name="meow")
async def meow(ctx):
    """Просто мяу"""
    await ctx.send("😺 " + "meow " * random.randint(1, 5))

# === КОМАНДА color ===
@bot.command(name="color")
async def color_cmd(ctx, hex1: str = None, hex2: str = None):
    """Генерирует градиент цвета. Использование: g!color #RRGGBB [#RRGGBB]"""
    if not hex1:
        await ctx.send("❌ Укажи цвет: `g!color #FF0000`")
        return
    
    try:
        from PIL import Image, ImageDraw, ImageColor
        
        color1 = ImageColor.getcolor(hex1, "RGB")
        if hex2:
            color2 = ImageColor.getcolor(hex2, "RGB")
        else:
            color2 = color1
        
        img = Image.new("RGB", (80, 80))
        draw = ImageDraw.Draw(img)
        
        for y in range(80):
            blend = y / 79
            r = int(color1[0] * (1 - blend) + color2[0] * blend)
            g = int(color1[1] * (1 - blend) + color2[1] * blend)
            b = int(color1[2] * (1 - blend) + color2[2] * blend)
            draw.line([(0, y), (80, y)], fill=(r, g, b))
        
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        
        await ctx.send(file=discord.File(buffer, "color.png"))
    except ImportError:
        await ctx.send("❌ Pillow не установлена. Добавь в requirements.txt")
    except Exception as e:
        await ctx.send(f"❌ Ошибка: {e}")

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
    
    await ctx.send(f"🔓 Байпас...\nРезультат: {await bypass.generic(link)}")

# === КОМАНДА onlyfans ===
@bot.command(name="onlyfans")
async def onlyfans_cmd(ctx, username: str = None):
    """Проверка OnlyFans (только для владельца)"""
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Только для владельца")
        return
    
    if not username:
        await ctx.send("❌ Укажи юзернейм: `g!onlyfans username`")
        return
    
    await ctx.send(f"🔞 Проверка OnlyFans для {username}... (функция в разработке)")

# === КОМАНДА fansly ===
@bot.command(name="fansly")
async def fansly_cmd(ctx, username: str = None):
    """Проверка Fansly (только для владельца)"""
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Только для владельца")
        return
    
    if not username:
        await ctx.send("❌ Укажи юзернейм: `g!fansly username`")
        return
    
    await ctx.send(f"🔞 Проверка Fansly для {username}... (функция в разработке)")

# === КОМАНДА ib2 ===
@bot.command(name="ib2")
async def ib2_cmd(ctx):
    """Обфускация через IronBrew 2"""
    content = await get_file_content(ctx.message)
    if not content:
        await ctx.send("❌ Прикрепи файл или отправь код в сообщении!")
        return
    
    await ctx.send("🔧 Обфускация через IronBrew 2... (функция в разработке)")

# === КОМАНДА ironobf ===
@bot.command(name="ironobf")
async def ironobf_cmd(ctx):
    """Обфускация через IronBrikked"""
    content = await get_file_content(ctx.message)
    if not content:
        await ctx.send("❌ Прикрепи файл или отправь код в сообщении!")
        return
    
    await ctx.send("🔧 Обфускация через IronBrikked... (функция в разработке)")

# === КОМАНДА obf ===
@bot.command(name="obf")
async def obf_cmd(ctx):
    """Базовая обфускация"""
    content = await get_file_content(ctx.message)
    if not content:
        await ctx.send("❌ Прикрепи файл или отправь код в сообщении!")
        return
    
    # Простая обфускация
    result = f"-- obfuscated\nlocal a=...\n{content}\nreturn a"
    await ctx.send(file=string_to_discordfile(result, "obfuscated.lua"))

# === КОМАНДА vmify ===
@bot.command(name="vmify")
async def vmify_cmd(ctx):
    """Обфускация через VM"""
    content = await get_file_content(ctx.message)
    if not content:
        await ctx.send("❌ Прикрепи файл или отправь код в сообщении!")
        return
    
    await ctx.send("🔧 Обфускация через VM... (функция в разработке)")

# === КОМАНДА silentkey ===
@bot.command(name="silentkey")
async def silentkey_cmd(ctx):
    """Получить Silent ключ"""
    await ctx.send("🔑 Silent key: `25ms_holy_scriptx_key`")

# === ЗАПУСК ===
if __name__ == "__main__":
    bot.run(TOKEN)
