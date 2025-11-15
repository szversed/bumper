# Discord Bump Reminder Bot

Este é um bot simples para Discord que envia um lembrete automático para "bump" o seu servidor a cada 2 horas, ideal para integração com bots de listagem como o Disboard.

A principal funcionalidade é a **detecção automática de bump**: o bot monitora o canal configurado e, ao detectar a mensagem de sucesso do bump (com a frase "Bump done!" e o emoji 💖), ele redefine o timer de 2 horas, garantindo que o lembrete seja enviado no momento exato.

## 🚀 Configuração e Execução

### 1. Pré-requisitos

*   Python 3.8+
*   Conta de Bot Discord (com as intents `message_content` e `guilds` ativadas)

### 2. Instalação de Dependências

```bash
pip install discord.py
```

### 3. Configuração do Token (Variável de Ambiente)

O bot utiliza a variável de ambiente `TOKEN` para se conectar ao Discord.

**Importante:** Para implantação em serviços de hospedagem como **Railway**, **Heroku** ou **Render**, você deve configurar esta variável diretamente na interface do serviço.

*   **Nome da Variável:** `TOKEN`
*   **Valor da Variável:** O token do seu bot Discord.

Para testar localmente, você pode definir a variável no seu terminal antes de executar o bot:

```bash
export TOKEN="SEU_TOKEN_AQUI"
```

### 4. Execução

Execute o bot a partir do terminal:

```bash
python bump_reminder_bot.py
```

## 🤖 Comandos de Barra

Após iniciar o bot, use os seguintes comandos no seu servidor Discord (apenas administradores podem usá-los):

| Comando | Descrição | Uso |
| :--- | :--- | :--- |
| `/setchannel` | Define o canal onde o lembrete de bump será enviado. | `/setchannel canal:#bump-aqui` |
| `/status` | Mostra o status atual do bot, incluindo o último bump e o tempo restante para o próximo lembrete. | `/status` |

## ⚙️ Como Funciona a Detecção Automática

O bot monitora o canal configurado e procura por mensagens de outros bots que contenham um embed com a frase `"bump done!"` e o emoji `💖` na descrição. Ao encontrar essa combinação, ele assume que o bump foi realizado com sucesso e reinicia o timer de 2 horas.

> **Nota:** Certifique-se de que o bot tem permissão para **ler mensagens** e **enviar mensagens** no canal configurado.
> Certifique-se também de que a **Intent de Conteúdo de Mensagem** (`Message Content Intent`) está ativada nas configurações do seu bot no Portal do Desenvolvedor do Discord.
