import os
import random
import asyncio
import aiohttp
import json

class DiscordSelfBot:
    def __init__(self):
        self.token = os.getenv('TOKEN')
        self.bump_channel_id = '1438084818725244971'  # ID fixo do canal
        self.session = None
        self.headers = {
            'Authorization': self.token,
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    async def start(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        print('Selfbot started!')
        await self.bump_loop()

    async def get_guild_id(self):
        """Obtém o ID da guilda baseado no canal"""
        async with self.session.get(f'https://discord.com/api/v9/channels/{self.bump_channel_id}') as response:
            if response.status == 200:
                data = await response.json()
                return data.get('guild_id')
            return None

    async def execute_bump_command(self):
        """Executa o comando slash /bump do Disboard"""
        guild_id = await self.get_guild_id()
        if not guild_id:
            print("Erro: Não foi possível obter o ID da guilda")
            return False

        # Payload para executar o comando slash
        payload = {
            'type': 2,
            'application_id': '302050872383242240',  # ID do Disboard
            'guild_id': guild_id,
            'channel_id': self.bump_channel_id,
            'session_id': 'random_session_id',  # Pode ser qualquer string
            'data': {
                'version': '11926',  # Versão do comando bump
                'id': '947088344167366698',  # ID do comando bump
                'name': 'bump',
                'type': 1,
                'options': [],
                'application_command': {
                    'id': '947088344167366698',
                    'application_id': '302050872383242240',
                    'version': '11926',
                    'default_permission': True,
                    'default_member_permissions': None,
                    'type': 1,
                    'nsfw': False,
                    'name': 'bump',
                    'description': 'Bump the server',
                    'dm_permission': True,
                    'options': []
                },
                'attachments': []
            }
        }

        url = f'https://discord.com/api/v9/interactions'
        
        try:
            async with self.session.post(url, json=payload) as response:
                if response.status in [200, 204]:
                    print('✅ Bump executado com sucesso!')
                    return True
                else:
                    print(f'❌ Erro ao executar bump: {response.status}')
                    text = await response.text()
                    print(f'Resposta: {text}')
                    return False
        except Exception as e:
            print(f'❌ Erro na requisição: {e}')
            return False

    async def bump_loop(self):
        """Loop principal para executar bumps periodicamente"""
        bump_count = 0
        
        # Primeiro bump imediatamente
        await asyncio.sleep(2)
        await self.execute_bump_command()
        bump_count += 1
        
        while True:
            # Espera 2-3 horas (aleatório) para o próximo bump
            wait_seconds = random.randint(7200, 10800)  # 2-3 horas em segundos
            wait_hours = wait_seconds / 3600
            print(f'⏰ Próximo bump em {wait_hours:.2f} horas...')
            
            await asyncio.sleep(wait_seconds)
            
            bump_count += 1
            print(f'\n--- Tentativa de bump #{bump_count} ---')
            
            success = await self.execute_bump_command()
            
            if success:
                print(f'✅ Bump #{bump_count} realizado com sucesso!')
            else:
                print(f'❌ Falha no bump #{bump_count}')

    async def close(self):
        """Fecha a sessão"""
        if self.session:
            await self.session.close()

async def main():
    bot = DiscordSelfBot()
    try:
        await bot.start()
    except KeyboardInterrupt:
        print('\nParando o bot...')
    finally:
        await bot.close()

if __name__ == "__main__":
    # Verifica se o token está definido
    token = os.getenv('TOKEN')
    
    if not token:
        raise ValueError("❌ Variável de ambiente TOKEN não encontrada!")
    
    print('🚀 Iniciando bot de bump...')
    print(f'� Canal de bump: 1438084818725244971')
    asyncio.run(main())
