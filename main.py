import nextcord
import os
import asyncio
import logging
from dotenv import load_dotenv
from nextcord.ext import commands
import json
from pathlib import Path

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Carrega as variáveis do .env
load_dotenv()

# Configuração de intents
intents = nextcord.Intents.all()

# Instância do bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Função para carregar cogs dinamicamente
def carregar_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                bot.load_extension(f"cogs.{filename[:-3]}")
                logging.info(f"✔️ Cog '{filename[:-3]}' carregada com sucesso!")
            except Exception as e:
                logging.error(f"❌ Erro ao carregar a cog '{filename[:-3]}': {e}")

# Evento de inicialização do bot
@bot.event
async def on_ready():
    logging.info(f"✅ Bot conectado como {bot.user}")
    logging.info(f"🔗 Servidores: {len(bot.guilds)}")
    logging.info("📂 Cogs carregadas:")
    for extension in bot.extensions:
        logging.info(f" - {extension}")
    
    # Criar JSON inicial
    criar_json("data/exemplo.json", {"exemplo": {"nome": "bot", "status": "ativo"}})
    
    # Iniciar loop de presença
    bot.loop.create_task(change_status())

# Função para criar um arquivo .json com dados iniciais
def criar_json(nome_arquivo, dados):
    caminho_arquivo = Path(nome_arquivo)
    if caminho_arquivo.exists():
        logging.warning(f"⚠️ O arquivo '{nome_arquivo}' já existe. Nenhuma alteração realizada.")
        return
    try:
        with open(nome_arquivo, 'w') as f:
            json.dump(dados, f, indent=4)
        logging.info(f"📂 Arquivo '{nome_arquivo}' criado com sucesso!")
    except Exception as e:
        logging.error(f"❌ Erro ao criar o arquivo '{nome_arquivo}': {e}")

# Alternar status do bot a cada 5 segundos
async def change_status():
    statuses = [
        nextcord.Game("Code Runner 🔥"),
        nextcord.Game("by Rede Gamer 🚀"),
        nextcord.Game("Desenvolvido por Lucas Dev 🛠️")
    ]
    while True:
        for status in statuses:
            await bot.change_presence(activity=status)
            await asyncio.sleep(5)

# Comando Slash /ping
@bot.slash_command(description="Responde com Pong!", guild_ids=[int(os.getenv("GUILD_ID"))])
async def ping(interaction: nextcord.Interaction):
    await interaction.response.send_message("Pong! 🏓")

# Carregar cogs antes de iniciar o bot
carregar_cogs()

# Iniciar o bot
logging.info("🔧 Bot iniciando... 🚀")
bot.run(os.getenv("TOKEN"))
