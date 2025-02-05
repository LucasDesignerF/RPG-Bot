## ⚠️ ATENÇÃO: Bot em desenvolvimento, algumas funções podem nao funcionar ou crashar... Aguarde ara atualizações...


# 🎮 **RPG Bot - Um Jogo de Aventura no Discord**

![Banner do Projeto](https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT15K7gtB6JksmMHKe9gzixx-ODND3bS2kNDQ&s)  

---

## 📜 **Sobre o Projeto**

O **RPG Bot** é um jogo de aventura interativo desenvolvido para servidores do Discord. Inspirado em jogos de RPG clássicos, ele permite que os usuários criem personagens, explorem mundos mágicos, lutem contra monstros, completem missões e muito mais! Com uma interface amigável e interativa, o bot oferece uma experiência imersiva diretamente no Discord.

✨ **Principais características:**
- **Criação de Personagem**: Escolha entre classes como Guerreiro, Mago ou Ladino.
- **Exploração**: Encontre recursos valiosos ao explorar áreas desconhecidas.
- **Combate**: Lute contra monstros poderosos e ganhe recompensas.
- **Inventário**: Gerencie seus itens e equipamentos.
- **Missões**: Complete desafios e receba prêmios exclusivos.
- **Configurações Personalizadas**: Ajuste suas preferências de jogo.

---

## 🛠️ **Como Funciona**

### 1. **Criando seu Personagem**
Ao iniciar sua jornada, você precisará criar um personagem. Use o comando `/rpg iniciar` e escolha entre as seguintes classes:

| Classe      | Descrição                          | Habilidades                     |
|-------------|------------------------------------|----------------------------------|
| 🛡️ Guerreiro | Tanque com alta defesa            | Defesa Total, Golpe Poderoso    |
| 🔮 Mago      | Dano mágico poderoso              | Bola de Fogo, Cura Arcana       |
| 🗡️ Ladino    | Ataques rápidos e críticos        | Ataque Furtivo, Envenenar       |


---

### 2. **Explorando o Mundo**
Use o comando `/rpg explorar` para encontrar recursos como ouro, madeira e minério. Esses itens são essenciais para fabricar equipamentos e progredir no jogo.

🔥 **Exemplo de Recompensas:**
- 💰 Ouro
- 🪵 Madeira
- ⚒️ Minério

⚠️ **Atenção:** Há um cooldown para evitar explorações excessivas!

---

### 3. **Combate Contra Monstros**
Enfrente monstros poderosos usando o comando `/rpg combate`. Derrote inimigos como:
- 👹 Goblin
- 🐉 Dragão
- 🐺 Lobo

Ganhe XP, ouro e itens raros ao vencer batalhas!


---

### 4. **Gerenciando Seu Inventário**
Verifique seus itens e equipamentos usando o comando `/rpg status`. Aqui você pode ver:
- ❤️ HP (Pontos de Vida)
- 🔵 Mana (Pontos de Magia)
- 💰 Ouro
- 🎒 Inventário

---

### 5. **Menu Principal**
Acesse o menu principal com `/rpg menu` para navegar rapidamente entre as opções do jogo:
- 🎒 Inventário
- ⚔️ Combate
- 🏰 Missões
- ⚙️ Configurações


---

## 🚀 **Como Instalar e Usar**

### 1. **Requisitos**
Antes de começar, certifique-se de ter o seguinte instalado:
- Python 3.8+
- Bibliotecas necessárias (`nextcord`, `numpy`, etc.)

```bash
pip install -r requirements.txt
```

### 2. **Configuração**
1. Clone o repositório:
   ```bash
   git clone https://github.com/LucasDesignerF/RPG-Bot.git
   cd rpg-bot
   ```

2. Configure o arquivo `.env` com o token do seu bot:
   ```
   DISCORD_TOKEN=seu_token_aqui
   TESTING_GUILD_ID=seu_guild_id_aqui
   ```

3. Execute o bot:
   ```bash
   python bot.py
   ```

---

## 📊 **Estrutura do Código**

O projeto está organizado em módulos para facilitar a manutenção:

```
├── cogs/
│   └── game.py          # Sistema principal do RPG
├── data/
│   └── players.json     # Armazena dados dos jogadores
├── requirements.txt     # Dependências do projeto
├── bot.py               # Arquivo principal do bot
└── README.md            # Documentação do projeto
```

---

## 🌟 **Funcionalidades Futuras**

Estamos planejando adicionar ainda mais funcionalidades ao jogo:
- 🏆 Sistema de Ranking
- 🏔️ Novas áreas para explorar
- 🧙‍♂️ NPCs (Personagens Não Jogáveis)
- 🎯 Eventos sazonais
- 🛡️ Guildas e Clãs

---

## 🤝 **Contribuições**

Adoraríamos contar com sua ajuda para melhorar o **RPG Bot**! Se você deseja contribuir, siga estas etapas:
1. Faça um fork do repositório.
2. Crie uma branch para sua feature:
   ```bash
   git checkout -b feature/nova-funcionalidade
   ```
3. Envie um Pull Request com suas alterações.

---

## 📜 **Licença**

Este projeto está sob a licença [MIT](LICENSE). Sinta-se à vontade para usá-lo e modificá-lo conforme necessário.

---

## 📸 **Capturas de Tela**

Aqui estão algumas capturas de tela do jogo em ação:

1. **Tela de Criação de Personagem**  
   ![Criação de Personagem](https://via.placeholder.com/600x400)

2. **Exploração**  
   ![Exploração](https://via.placeholder.com/600x400)

3. **Combate**  
   ![Combate](https://via.placeholder.com/600x400)

4. **Menu Principal**  
   ![Menu Principal](https://via.placeholder.com/600x400)

---

## 📞 **Contato**

Se tiver dúvidas ou sugestões, entre em contato:
- **Discord**: lrfortes
- **GitHub**: [Lucas Designer](https://github.com/LucasDesignerF)
- **Email**: ofc.rede@gmail.com

---

🎉 **Divirta-se jogando e contribuindo para o RPG Bot!** 🎉

