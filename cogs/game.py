import nextcord
import os
import random
import asyncio
from nextcord.ext import commands
from pathlib import Path
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from PIL import Image, ImageDraw, ImageFont
import io

# Configurações Globais
EMBED_COLOR = 0x2b2d31
ERROR_COLOR = 0xff0000
SUCCESS_COLOR = 0x00ff00
COOLDOWNS = {
    'explorar': 300,
    'minerar': 180,
    'caçar': 240,
    'craft': 120
}
MAX_INVENTORY_SLOTS = 50
XP_PER_LEVEL = 1000

class GameButton(nextcord.ui.Button):
    def __init__(self, label, style, custom_id, emoji=None, disabled=False):
        super().__init__(
            label=label,
            style=style,
            custom_id=custom_id,
            emoji=emoji,
            disabled=disabled
        )

class InventoryView(nextcord.ui.View):
    def __init__(self, cog, user_id, page=0):
        super().__init__(timeout=60)
        self.cog = cog
        self.user_id = user_id
        self.page = page
        self.max_page = (len(self.cog._get_player(user_id)['inventario']) - 1) // 5
        
        self.add_item(GameButton("◀️ Anterior", nextcord.ButtonStyle.grey, "prev_page", disabled=(page == 0)))
        self.add_item(GameButton(f"Página {page+1}", nextcord.ButtonStyle.blurple, "current_page", disabled=True))
        self.add_item(GameButton("▶️ Próxima", nextcord.ButtonStyle.grey, "next_page", disabled=(page >= self.max_page)))

    async def interaction_check(self, interaction: nextcord.Interaction) -> bool:
        return str(interaction.user.id) == self.user_id

class CombatSystem:
    @staticmethod
    def calculate_damage(attacker, defender):
        base_damage = random.randint(attacker['dano_min'], attacker['dano_max'])
        crit_chance = attacker.get('critico', 0) / 100
        if random.random() < crit_chance:
            base_damage *= 2
        defense = defender.get('defesa', 0)
        return max(1, base_damage - defense)

class QuestSystem:
    DAILY_QUESTS = {
        'explorer': {
            'name': 'Explorador Diário',
            'goal': 'Realizar 3 explorações',
            'reward': {'ouro': 150, 'xp': 500},
            'required': 3
        },
        'hunter': {
            'name': 'Caçador de Monstros',
            'goal': 'Derrotar 5 monstros',
            'reward': {'escama_de_dragão': 1, 'xp': 1000},
            'required': 5
        }
    }
    
    ACHIEVEMENTS = {
        'veteran': {
            'name': 'Veterano',
            'goal': 'Alcançar nível 10',
            'reward': {'titulo': '🏆 Veterano', 'ouro': 1000},
            'required': 10
        }
    }

class CraftingSystem:
    RECIPES = {
        'espada_ferro': {
            'materiais': {'minério': 5, 'madeira': 3},
            'resultado': {'espada_ferro': 1},
            'nivel': 2
        },
        'pocao_cura': {
            'materiais': {'ervas': 2, 'agua': 1},
            'resultado': {'pocao_cura': 1},
            'nivel': 1
        }
    }

class MainMenuView(nextcord.ui.View):
    def __init__(self, cog, user_id):
        super().__init__(timeout=60)
        self.cog = cog
        self.user_id = user_id
        
        buttons = [
            ('🎒 Inventário', nextcord.ButtonStyle.blurple, 'inventory'),
            ('⚔️ Combate', nextcord.ButtonStyle.red, 'combat'),
            ('📜 Missões', nextcord.ButtonStyle.green, 'quests'),
            ('⚙️ Perfil', nextcord.ButtonStyle.grey, 'profile'),
            ('🛠️ Craft', nextcord.ButtonStyle.grey, 'craft')
        ]
        
        for label, style, cid in buttons:
            self.add_item(GameButton(label, style, cid))

    async def interaction_check(self, interaction: nextcord.Interaction) -> bool:
        return str(interaction.user.id) == self.user_id

class CharacterCreationView(nextcord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=120)
        self.cog = cog
        
        options = [
            nextcord.SelectOption(label='Guerreiro', emoji='🛡️', description='Tanque com alta defesa'),
            nextcord.SelectOption(label='Mago', emoji='🔮', description='Dano mágico poderoso'),
            nextcord.SelectOption(label='Ladino', emoji='🗡️', description='Ataques rápidos e críticos')
        ]
        
        self.select = nextcord.ui.Select(
            placeholder='Escolha sua classe...',
            options=options,
            min_values=1,
            max_values=1
        )
        self.select.callback = self.on_select
        self.add_item(self.select)

    async def on_select(self, interaction: nextcord.Interaction):
        player = self.cog._get_player(str(interaction.user.id))
        classe = self.select.values[0]
        
        buffs = self.cog.classes[classe]['buff']
        player.update({
            'classe': classe,
            'hp_max': buffs['hp'],
            'hp': buffs['hp'],
            'dano_min': buffs['dano_min'],
            'dano_max': buffs['dano_max'],
            'defesa': buffs['defesa'],
            'mana_max': buffs.get('mana', 0),
            'mana': buffs.get('mana', 0),
            'habilidades': self.cog.classes[classe]['habilidades']
        })
        
        embed = nextcord.Embed(
            title=f"🎉 Personagem Criado! {self.cog.classes[classe]['emoji']}",
            description=f"**Classe:** {classe}\n**Habilidades:** {', '.join(player['habilidades'])}",
            color=SUCCESS_COLOR
        )
        embed.add_field(name="⚔️ Dano", value=f"{buffs['dano_min']}-{buffs['dano_max']}")
        embed.add_field(name="🛡️ Defesa", value=buffs['defesa'])
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        
        await interaction.response.edit_message(embed=embed, view=None)
        self.cog._save_data()

class CombatSession:
    def __init__(self, cog, player, monster, interaction):
        self.cog = cog
        self.player = player
        self.original_player_hp = player['hp']
        self.monster = monster.copy()
        self.interaction = interaction
        self.message = None
        self.is_active = True

    async def send_initial_message(self):
        embed = self.create_combat_embed()
        view = CombatView(self)
        self.message = await self.interaction.followup.send(embed=embed, view=view)
        return self.message

    def create_combat_embed(self):
        embed = nextcord.Embed(
            title=f"⚔️ Combate contra {self.monster['name']}",
            color=0xFF0000
        )
        embed.add_field(
            name=f"Jogador - {self.interaction.user.display_name}",
            value=f"❤️ HP: {self.player['hp']}/{self.player['hp_max']}\n⚔️ Dano: {self.player['dano_min']}-{self.player['dano_max']}",
            inline=False
        )
        embed.add_field(
            name=f"Monstro - {self.monster['name']}",
            value=f"❤️ HP: {self.monster['hp']}/{self.monster['hp_max']}\n⚔️ Dano: {self.monster['dano_min']}-{self.monster['dano_max']}",
            inline=False
        )
        return embed

    async def process_attack(self):
        # Jogador ataca
        player_damage = CombatSystem.calculate_damage(self.player, self.monster)
        self.monster['hp'] -= player_damage

        # Verifica se o monstro morreu
        if self.monster['hp'] <= 0:
            await self.end_combat(victory=True)
            return

        # Monstro contra-ataca
        monster_damage = CombatSystem.calculate_damage(self.monster, self.player)
        self.player['hp'] -= monster_damage

        # Verifica se o jogador morreu
        if self.player['hp'] <= 0:
            await self.end_combat(victory=False)
            return

        # Atualiza a mensagem
        await self.update_combat_message(player_damage, monster_damage)

    async def process_defend(self):
        # Jogador se defende (reduz dano em 50%)
        player_defense = int(self.player['defesa'] * 1.5)
        monster_damage = max(1, CombatSystem.calculate_damage(self.monster, self.player) - player_defense)
        self.player['hp'] -= monster_damage

        # Atualiza a mensagem
        embed = self.create_combat_embed()
        embed.description = f"🛡️ Você se defendeu! Dano recebido reduzido para {monster_damage}!"
        await self.message.edit(embed=embed)

        if self.player['hp'] <= 0:
            await self.end_combat(victory=False)

    async def process_flee(self):
        chance = random.randint(1, 100)
        if chance > 30:  # 70% de chance de fugir
            self.player['hp'] = self.original_player_hp
            embed = self.create_combat_embed()
            embed.description = "🏃♂️ Você fugiu do combate com sucesso!"
            await self.message.edit(embed=embed, view=None)
            self.is_active = False
        else:
            monster_damage = CombatSystem.calculate_damage(self.monster, self.player)
            self.player['hp'] -= monster_damage
            embed = self.create_combat_embed()
            embed.description = f"🚫 Falha ao fugir! Você recebeu {monster_damage} de dano!"
            await self.message.edit(embed=embed)

            if self.player['hp'] <= 0:
                await self.end_combat(victory=False)

    async def update_combat_message(self, player_damage, monster_damage):
        embed = self.create_combat_embed()
        embed.description = (
            f"⚔️ Você causou **{player_damage}** de dano!\n"
            f"😠 O monstro contra-atacou com **{monster_damage}** de dano!"
        )
        await self.message.edit(embed=embed)

    async def end_combat(self, victory):
        self.is_active = False
        embed = self.create_combat_embed()
        
        if victory:
            # Dar recompensas
            xp = self.monster['xp']
            drops = {}
            for item, drop_info in self.monster['drops'].items():
                if isinstance(drop_info, tuple):
                    drops[item] = random.randint(drop_info[0], drop_info[1])
                else:
                    drops[item] = drop_info
            
            # Atualizar jogador
            self.player['xp'] += xp
            for item, quantity in drops.items():
                self.player['inventario'][item] = self.player['inventario'].get(item, 0) + quantity
            
            # Verificar level up
            await self.cog._update_level(self.player)
            
            embed.description = (
                f"🎉 Vitória! Você ganhou:\n"
                f"XP: {xp}\n"
                f"Drops: {', '.join([f'{k} x{v}' for k, v in drops.items()])}"
            )
            embed.color = 0x00FF00
        else:
            self.player['hp'] = 0
            embed.description = "💀 Você foi derrotado!"
            embed.color = 0x000000

        self.cog._save_data()
        await self.message.edit(embed=embed, view=None)

class CombatView(nextcord.ui.View):
    def __init__(self, session):
        super().__init__(timeout=30)
        self.session = session

    async def interaction_check(self, interaction: nextcord.Interaction) -> bool:
        return interaction.user.id == self.session.interaction.user.id

    @nextcord.ui.button(label="⚔️ Atacar", style=nextcord.ButtonStyle.red)
    async def attack(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if not self.session.is_active:
            return
            
        await self.session.process_attack()
        await interaction.response.defer()

    @nextcord.ui.button(label="🛡️ Defender", style=nextcord.ButtonStyle.grey)
    async def defend(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if not self.session.is_active:
            return
            
        await self.session.process_defend()
        await interaction.response.defer()

    @nextcord.ui.button(label="🏃♂️ Fugir", style=nextcord.ButtonStyle.grey)
    async def flee(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if not self.session.is_active:
            return
            
        await self.session.process_flee()
        await interaction.response.defer()

class GameCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_path = Path("data/players.json")
        self._ensure_directories()
        self.players = self._load_data()
        
        self.classes = {
            'Guerreiro': {
                'buff': {'hp': 200, 'dano_min': 15, 'dano_max': 25, 'defesa': 20},
                'emoji': '🛡️',
                'habilidades': ['Defesa Total', 'Golpe Poderoso']
            },
            'Mago': {
                'buff': {'hp': 120, 'dano_min': 20, 'dano_max': 40, 'defesa': 10, 'mana': 150},
                'emoji': '🔮',
                'habilidades': ['Bola de Fogo', 'Cura Arcana']
            },
            'Ladino': {
                'buff': {'hp': 150, 'dano_min': 25, 'dano_max': 35, 'defesa': 15, 'critico': 15},
                'emoji': '🗡️',
                'habilidades': ['Ataque Furtivo', 'Envenenar']
            }
        }
        
        self.monsters = {
            'Goblin': {'name': 'Goblin', 'level': 5, 'hp': 80, 'hp_max': 80, 'dano_min': 8, 'dano_max': 12, 
                      'xp': 150, 'drops': {'ouro': (5, 15)}, 'defesa': 5},
            'Dragão': {'name': 'Dragão', 'level': 20, 'hp': 500, 'hp_max': 500, 'dano_min': 30, 'dano_max': 50,
                      'xp': 1000, 'drops': {'escama_de_dragão': 1}, 'defesa': 20},
            'Lobo': {'name': 'Lobo', 'level': 3, 'hp': 50, 'hp_max': 50, 'dano_min': 5, 'dano_max': 10,
                    'xp': 80, 'drops': {'pele_de_lobo': 1}, 'defesa': 3}
        }

    def _ensure_directories(self):
        self.data_path.parent.mkdir(exist_ok=True)

    def _load_data(self) -> Dict[str, Any]:
        try:
            return json.loads(self.data_path.read_text())
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_data(self):
        self.data_path.write_text(json.dumps(self.players, indent=4))

    def _get_player(self, user_id: str) -> Dict[str, Any]:
        if user_id not in self.players:
            self.players[user_id] = {
                'nome': None,
                'level': 1,
                'xp': 0,
                'ouro': 100,
                'hp_max': 100,
                'hp': 100,
                'mana_max': 0,
                'mana': 0,
                'inventario': {},
                'classe': None,
                'cooldowns': {},
                'skills': {
                    'combate': 1,
                    'exploração': 1,
                    'crafting': 1
                },
                'equipamentos': {
                    'arma': None,
                    'armadura': None
                },
                'quests': {
                    'daily': {},
                    'achievements': {}
                },
                'titulo': None,
                'ultima_diaria': None
            }
        return self.players[user_id]

    async def _update_level(self, player):
        while player['xp'] >= (player['level'] * XP_PER_LEVEL):
            player['xp'] -= (player['level'] * XP_PER_LEVEL)
            player['level'] += 1
            player['hp_max'] += 10
            player['hp'] = player['hp_max']
            if player['classe'] == 'Mago':
                player['mana_max'] += 20
                player['mana'] = player['mana_max']

    async def _show_inventory(self, interaction: nextcord.Interaction, page=0):
        player = self._get_player(str(interaction.user.id))
        items = list(player['inventario'].items())
        total_pages = (len(items) - 1) // 5
        
        embed = nextcord.Embed(
            title=f"🎒 Inventário de {interaction.user.display_name}",
            color=EMBED_COLOR
        )
        
        for i in range(page*5, min((page+1)*5, len(items))):
            item, quantity = items[i]
            embed.add_field(name=f"📦 {item.title()}", value=f"Quantidade: {quantity}", inline=False)
        
        embed.set_footer(text=f"Página {page+1}/{total_pages+1} • Slots: {len(items)}/{MAX_INVENTORY_SLOTS}")
        await interaction.response.edit_message(embed=embed, view=InventoryView(self, str(interaction.user.id), page))

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"✅ RPG System loaded! Players: {len(self.players)}")

    @nextcord.slash_command(name="rpg", description="Main RPG system")
    async def rpg(self, interaction: nextcord.Interaction):
        pass

    @rpg.subcommand(description="Inicia sua jornada no RPG!")
    async def iniciar(self, interaction: nextcord.Interaction):
        await interaction.response.defer()
        player = self._get_player(str(interaction.user.id))
        
        if player['classe']:
            embed = nextcord.Embed(title="❌ Personagem já criado!", color=ERROR_COLOR)
            return await interaction.followup.send(embed=embed)
        
        embed = nextcord.Embed(title="🎮 Bem-vindo ao RPG!", color=EMBED_COLOR)
        embed.set_image(url="https://i.imgur.com/rV7QZAW.png")
        await interaction.followup.send(embed=embed, view=CharacterCreationView(self))

    @rpg.subcommand(description="Mostra seu status completo")
    async def status(self, interaction: nextcord.Interaction):
        await interaction.response.defer()
        player = self._get_player(str(interaction.user.id))
        
        embed = nextcord.Embed(
            title=f"{player['titulo'] or ''} {interaction.user.display_name}",
            color=EMBED_COLOR
        )
        
        if player['classe']:
            embed.description = (
                f"**Classe:** {player['classe']} {self.classes[player['classe']]['emoji']}\n"
                f"**Level:** {player['level']}\n"
                f"**XP:** {player['xp']}/{player['level'] * XP_PER_LEVEL}"
            )
            
            embed.add_field(name="❤️ HP", value=f"{player['hp']}/{player['hp_max']}")
            if player['classe'] == 'Mago':
                embed.add_field(name="🔵 Mana", value=f"{player['mana']}/{player['mana_max']}")
            
            embed.add_field(name="💰 Ouro", value=player['ouro'], inline=False)
            
            equipamentos = "\n".join([f"{k}: {v or 'Nenhum'}" for k, v in player['equipamentos'].items()])
            embed.add_field(name="⚔️ Equipamentos", value=equipamentos, inline=False)
            
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
        else:
            embed.description = "❌ Você ainda não criou seu personagem!\nUse `/rpg iniciar` para começar!"
        
        await interaction.followup.send(embed=embed)

    @rpg.subcommand(description="Abre o menu principal do jogo")
    async def menu(self, interaction: nextcord.Interaction):
        await interaction.response.defer()
        embed = nextcord.Embed(title="🎮 Menu Principal", color=EMBED_COLOR)
        await interaction.followup.send(embed=embed, view=MainMenuView(self, str(interaction.user.id)))

    @commands.Cog.listener()
    async def on_interaction(self, interaction: nextcord.Interaction):
        if not interaction.data.get('custom_id'):
            return
            
        user_id = str(interaction.user.id)
        player = self._get_player(user_id)
        
        # Inventário
        if interaction.data['custom_id'] == 'inventory':
            await self._show_inventory(interaction)
            
        # Sistema completo de missões
        elif interaction.data['custom_id'] == 'quests':
            embed = nextcord.Embed(title="📜 Missões Ativas", color=EMBED_COLOR)
            # Adicionar lógica de missões
            await interaction.response.send_message(embed=embed)
            
        # Sistema de crafting
        elif interaction.data['custom_id'] == 'craft':
            embed = nextcord.Embed(title="🛠️ Crafting", color=EMBED_COLOR)
            # Adicionar lógica de crafting
            await interaction.response.send_message(embed=embed)
            
        # Paginação do inventário
        elif interaction.data['custom_id'] in ['prev_page', 'next_page']:
            current_page = int(interaction.message.embeds[0].footer.text.split()[1].split('/')[0]) - 1
            new_page = current_page - 1 if interaction.data['custom_id'] == 'prev_page' else current_page + 1
            await self._show_inventory(interaction, new_page)

    @rpg.subcommand(description="Explora áreas em busca de recursos")
    async def explorar(self, interaction: nextcord.Interaction):
        user_id = str(interaction.user.id)
        player = self._get_player(user_id)
        await interaction.response.defer()
        
        # Verificação de cooldown
        if datetime.now() < player['cooldowns'].get('explorar', datetime.min):
            remaining = player['cooldowns']['explorar'] - datetime.now()
            embed = nextcord.Embed(title="⏳ Cooldown Ativo!", color=ERROR_COLOR)
            embed.description = f"Você pode explorar novamente em {remaining.seconds//60} minutos"
            return await interaction.followup.send(embed=embed)
        
        # Lógica de exploração
        rewards = {
            'ouro': random.randint(20, 50),
            'madeira': random.randint(1, 5),
            'minério': random.randint(1, 3),
            'ervas': random.randint(1, 2)
        }
        
        # Adicionar recompensas
        for item, qtd in rewards.items():
            player['inventario'][item] = player['inventario'].get(item, 0) + qtd
        
        # Atualizar cooldown
        player['cooldowns']['explorar'] = datetime.now() + timedelta(seconds=COOLDOWNS['explorar'])
        self._save_data()
        
        # Embed de resultado
        embed = nextcord.Embed(title="🌲 Exploração Bem Sucedida!", color=SUCCESS_COLOR)
        for item, qtd in rewards.items():
            embed.add_field(name=f"🗃️ {item.title()}", value=f"x{qtd}", inline=True)
        embed.set_footer(text=f"Próxima exploração em {COOLDOWNS['explorar']//60} minutos")
        await interaction.followup.send(embed=embed)

    @rpg.subcommand(description="Luta contra monstros")
    async def combate(self, interaction: nextcord.Interaction):
        user_id = str(interaction.user.id)
        player = self._get_player(user_id)
        await interaction.response.defer()
        
        if player['hp'] <= 0:
            embed = nextcord.Embed(title="⚠️ Você está inconsciente!", description="Use uma poção de cura ou espere regenerar vida.", color=ERROR_COLOR)
            return await interaction.followup.send(embed=embed)

        # Escolher monstro baseado no level do jogador
        available_monsters = [m for m in self.monsters.values() if m['level'] <= player['level'] + 2]
        if not available_monsters:
            available_monsters = list(self.monsters.values())
            
        monster = random.choice(available_monsters).copy()
        monster['hp'] = monster['hp_max']  # Reset HP para cada combate

        session = CombatSession(self, player, monster, interaction)
        await session.send_initial_message()

def setup(bot):
    bot.add_cog(GameCog(bot))