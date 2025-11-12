import os
import random
import asyncio
import aiohttp
import json

class DiscordSelfBot:
    def __init__(self):
        self.token = os.getenv('TOKEN')  # Token do Railway
        self.guild_id = '1438084818725244971'  # ID fixo do servidor
        self.bump_channel_id = None  # Será definido automaticamente
        self.session = None
        self.headers = {
            'Authorization': self.token,
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    async def start(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        print('🤖 Selfbot iniciado!')
        
        # Testa a conexão primeiro
        if await self.test_connection():
            print('✅ Token válido!')
            await self.find_and_setup_channel()
        else:
            print('❌ Token inválido ou erro de conexão')

    async def test_connection(self):
        """Testa a conexão com a API do Discord"""
        try:
            async with self.session.get('https://discord.com/api/v9/users/@me') as response:
                if response.status == 200:
                    user_data = await response.json()
                    print(f"👤 Conectado como: {user_data['username']}#{user_data['discriminator']}")
                    return True
                else:
                    print(f"❌ Erro de autenticação: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
            return False

    async def get_guild_channels(self):
        """Busca todos os canais do servidor"""
        try:
            url = f'https://discord.com/api/v9/guilds/{self.guild_id}/channels'
            async with self.session.get(url) as response:
                if response.status == 200:
                    channels = await response.json()
                    return channels
                else:
                    print(f"❌ Erro ao buscar canais: {response.status}")
                    return []
        except Exception as e:
            print(f"❌ Erro ao buscar canais: {e}")
            return []

    async def find_and_setup_channel(self):
        """Encontra e configura o canal de bump automaticamente"""
        print(f'\n🔍 Procurando canais no servidor {self.guild_id}...')
        
        channels = await self.get_guild_channels()
        
        if not channels:
            print('❌ Não foi possível encontrar canais no servidor')
            return
        
        # Filtra apenas canais de texto
        text_channels = [ch for ch in channels if ch.get('type') == 0]
        
        if not text_channels:
            print('❌ Nenhum canal de texto encontrado no servidor')
            return
        
        print(f'\n📋 Canais disponíveis no servidor:')
        print('=' * 50)
        
        for i, channel in enumerate(text_channels, 1):
            channel_name = channel.get('name', 'Unknown')
            channel_id = channel.get('id')
            print(f'{i}. #{channel_name} (ID: {channel_id})')
        
        print('=' * 50)
        
        # Tenta encontrar um canal com nome sugerindo "bump" ou "disboard"
        suggested_channels = []
        for channel in text_channels:
            channel_name = channel.get('name', '').lower()
            if any(word in channel_name for word in ['bump', 'disboard', 'bot', 'commands', 'geral', 'general']):
                suggested_channels.append(channel)
        
        if suggested_channels:
            # Usa o primeiro canal sugerido automaticamente
            self.bump_channel_id = suggested_channels[0]['id']
            channel_name = suggested_channels[0]['name']
            print(f'\n✅ Canal selecionado automaticamente: #{channel_name}')
            print('💡 Dica: Se quiser outro canal, modifique o código')
            await self.bump_loop()
        else:
            # Se não encontrar canal sugerido, usa o primeiro canal
            self.bump_channel_id = text_channels[0]['id']
            channel_name = text_channels[0]['name']
            print(f'\n✅ Usando o primeiro canal disponível: #{channel_name}')
            print('💡 Dica: Se quiser outro canal, modifique o código')
            await self.bump_loop()

    async def execute_bump_command(self):
        """Executa o comando slash /bump do Disboard"""
        if not self.bump_channel_id:
            print('❌ Canal não configurado!')
            return False

        payload = {
            'type': 2,
            'application_id': '302050872383242240',  # ID do Disboard
            'guild_id': self.guild_id,  # ID do servidor
            'channel_id': self.bump_channel_id,  # ID do canal
            'session_id': f'session_{random.randint(1000, 9999)}',
            'data': {
                'version': '11926',
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
                    return False
        except Exception as e:
            print(f'❌ Erro na requisição: {e}')
            return False

    async def bump_loop(self):
        """Loop principal para executar bumps periodicamente"""
        bump_count = 0
        
        print(f'\n🚀 Iniciando loop de bump:')
        print(f'🏠 Servidor: {self.guild_id}')
        print(f'📝 Canal: {self.bump_channel_id}')
        print('⏰ Bumps automáticos a cada 2-3 horas\n')
        
        # Primeiro bump imediatamente
        bump_count += 1
        print(f'--- Tentativa de bump #{bump_count} ---')
        success = await self.execute_bump_command()
        
        if success:
            print(f'✅ Bump #{bump_count} realizado com sucesso!')
        else:
            print(f'❌ Falha no bump #{bump_count}')
        
        while True:
            # Espera 2-3 horas (aleatório) para o próximo bump
            wait_seconds = random.randint(7200, 10800)  # 2-3 horas em segundos
            wait_hours = wait_seconds / 3600
            print(f'⏰ Próximo bump em {wait_hours:.2f} horas...\n')
            
            await asyncio.sleep(wait_seconds)
            
            bump_count += 1
            print(f'--- Tentativa de bump #{bump_count} ---')
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
        print('\n👋 Parando o bot...')
    finally:
        await bot.close()

if __name__ == "__main__":
    token = os.getenv('TOKEN')
    
    if not token:
        raise ValueError("❌ Variável de ambiente TOKEN não encontrada no Railway!")
    
    print('🎮 Discord Bump Bot - Setup Automático')
    asyncio.run(main())
