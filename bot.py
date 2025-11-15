import os
import json
from datetime import datetime, timedelta
import discord
from discord.ext import commands, tasks
from discord import app_commands
CONFIG_FILE = "config_bump.json"
DEFAULT_INTERVAL_HOURS = 2
def load_config():
    
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {"channel_id": None, "last_bump": None}
def save_config(config):
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)
config = load_config()
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents)
def is_admin():
    
    async def predicate(interaction: discord.Interaction):
        if interaction.user.guild_permissions.administrator:
            return True
        await interaction.response.send_message("🚫 Você precisa ser um administrador para usar este comando.", ephemeral=True)
        return False
    return app_commands.check(predicate)
@bot.event
async def on_message(message: discord.Message):
    
    global config
    if not message.author.bot or not message.embeds:
        await bot.process_commands(message)
        return
    embed = message.embeds[0]
    channel_id = config.get("channel_id")
    if channel_id and message.channel.id == channel_id:
        description = embed.description.lower() if embed.description else ""
        if "bump done!" in description and "💖" in embed.description:
            config["last_bump"] = datetime.now().isoformat()
            save_config(config)
            print(f"✅ Bump do Disboard detectado no canal {message.channel.name}. Timer redefinido.")
            try:
                await message.channel.send("✅ Timer de bump redefinido automaticamente!", delete_after=5)
            except Exception:
                pass
    await bot.process_commands(message)
@bot.event
async def on_ready():
    
    print(f"✅ {bot.user} online!")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Sincronizei {len(synced)} comandos de barra.")
    except Exception as e:
        print(f"❌ Erro ao sincronizar comandos: {e}")
    if not bump_reminder_loop.is_running():
        bump_reminder_loop.start()
        print("🔁 Loop de lembrete de bump iniciado.")
@tasks.loop(minutes=1)
async def bump_reminder_loop():
    
    global config
    channel_id = config.get("channel_id")
    last_bump_str = config.get("last_bump")
    if not channel_id:
        return
    if last_bump_str:
        last_bump = datetime.fromisoformat(last_bump_str)
        next_bump_time = last_bump + timedelta(hours=DEFAULT_INTERVAL_HOURS)
    else:
        next_bump_time = datetime.now() - timedelta(minutes=1)
    if datetime.now() >= next_bump_time:
        channel = bot.get_channel(channel_id)
        if channel:
            try:
                embed = discord.Embed(
                    title="⏰ HORA DE DAR BUMP!",
                    description="O servidor está pronto para ser 'bumpado' novamente. Use o comando de bump do seu bot de listagem (ex: `/bump`).",
                    color=discord.Color.blue()
                )
                await channel.send(embed=embed)
                config["last_bump"] = datetime.now().isoformat()
                save_config(config)
                print(f"✅ Lembrete de bump enviado para o canal {channel.name}.")
            except discord.Forbidden:
                print(f"❌ Erro: Não tenho permissão para enviar mensagens no canal {channel_id}.")
            except Exception as e:
                print(f"❌ Erro ao enviar lembrete de bump: {e}")
        else:
            print(f"❌ Erro: Canal com ID {channel_id} não encontrado. Removendo da configuração.")
            config["channel_id"] = None
            save_config(config)
@bot.tree.command(name="setchannel", description="Define o canal onde o lembrete de bump será enviado.")
@app_commands.describe(canal="O canal de texto para o lembrete de bump.")
@is_admin()
async def set_channel(interaction: discord.Interaction, canal: discord.TextChannel):
    
    global config
    config["channel_id"] = canal.id
    config["last_bump"] = datetime.now().isoformat()
    save_config(config)
    embed = discord.Embed(
        title="✅ Canal de Bump Configurado",
        description=f"O lembrete de bump será enviado no canal {canal.mention} a cada {DEFAULT_INTERVAL_HOURS} horas.",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)
@bot.tree.command(name="status", description="Mostra o status atual do lembrete de bump.")
@is_admin()
async def status(interaction: discord.Interaction):
    
    channel_id = config.get("channel_id")
    last_bump_str = config.get("last_bump")
    if channel_id:
        channel = bot.get_channel(channel_id)
        channel_name = channel.mention if channel else f"ID não encontrado: {channel_id}"
        if last_bump_str:
            last_bump = datetime.fromisoformat(last_bump_str)
            next_bump_time = last_bump + timedelta(hours=DEFAULT_INTERVAL_HOURS)
            time_until_next = next_bump_time - datetime.now()
            if time_until_next.total_seconds() < 0:
                next_bump_status = "Pronto para enviar (atrasado)"
            else:
                hours, remainder = divmod(int(time_until_next.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                next_bump_status = f"Faltam {hours}h {minutes}m"
        else:
            next_bump_status = "Aguardando o primeiro envio."
        embed = discord.Embed(
            title="📊 Status do Lembrete de Bump",
            color=discord.Color.gold()
        )
        embed.add_field(name="Canal Configurado", value=channel_name, inline=False)
        embed.add_field(name="Último Lembrete", value=last_bump.strftime("%d/%m/%Y %H:%M:%S") if last_bump_str else "Nenhum", inline=True)
        embed.add_field(name="Próximo Lembrete", value=next_bump_status, inline=True)
    else:
        embed = discord.Embed(
            title="❌ Lembrete de Bump Desativado",
            description="Use `/setchannel` para configurar o canal de lembrete.",
            color=discord.Color.red()
        )
    await interaction.response.send_message(embed=embed, ephemeral=True)
if __name__ == "__main__":
    token = os.getenv("TOKEN")
    if not token:
        print("❌ Variável de ambiente TOKEN não encontrada.")
        print("Defina TOKEN no ambiente e rode novamente.")
    else:
        bot.run(token)
