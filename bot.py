import os
import random
import asyncio
import aiohttp
import json

class DiscordSelfBot:
    def __init__(self):
        self.token = os.getenv('TOKEN')  # Token do Railway
        self.guild_id = '1438084818725244971'  # ID fixo do servidor
        self.bump_channel_id = None  # Será definido via comando
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
            await self.setup_channel()
        else:
            print('❌ Token inválido ou erro de conexão')

    async def setup_channel(self):
        """Configura o canal de bump interativamente"""
        print('\n🎯 Configuração do Canal de Bump')
        print('Para encontrar o ID do canal:')
        print('1. Ative o Modo Desenvolvedor no Discord')
        print('2. Clique com botão direito no canal → "Copiar ID"')
        print('3. Cole o ID abaixo\n')
        
        while not self.bump_channel_id:
            try:
                channel_id = input('📥 Digite o ID do canal: ').strip()
                
                # Validação básica do ID
                if channel_id.isdigit() and len(channel_id) >= 17:
                    self.bump_channel_id = channel_id
                    print(f'✅ Canal configurado: {channel_id}')
                    await self.bump_loop()
                else:
                    print('❌ ID inválido. Tente novamente.')
                    
            except (KeyboardInterrupt, EOFError):
                print('\n👋 Saindo...')
                break
            except Exception as e:
                print(f'❌ Erro: {e}')

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
            'session_id': 'random_session_id_123',
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
        
        print(f'\n🚀 Iniciando loop de bump no servidor: {self.guild_id}')
        print('⏰ Bumps automáticos a cada 2-3 horas\n')
        
        while True:
            bump_count += 1
            print(f'--- Tentativa de bump #{bump_count} ---')
            
            success = await self.execute_bump_command()
            
            if success:
                print(f'✅ Bump #{bump_count} realizado com sucesso!')
            else:
                print(f'❌ Falha no bump #{bump_count}')
            
            # Espera 2-3 horas (aleatório) para o próximo bump
            wait_seconds = random.randint(7200, 10800)  # 2-3 horas em segundos
            wait_hours = wait_seconds / 3600
            print(f'⏰ Próximo bump em {wait_hours:.2f} horas...\n')
            
            await asyncio.sleep(wait_seconds)

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
    
    print('🎮 Discord Bump Bot')
    print('🏠 Servidor: 1438084818725244971')
    asyncio.run(main())
