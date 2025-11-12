import os
import random
import asyncio
import aiohttp
import json
import time

class DiscordSelfBot:
    def __init__(self):
        self.token = os.getenv('TOKEN')  # Token do Railway
        self.guild_id = '1438084818725244971'  # ID fixo do servidor
        self.bump_channel_id = None  # Será definido automaticamente
        self.session = None
        self.disboard_command_version = None  # Versão será buscada dinamicamente
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
        else:
            # Se não encontrar canal sugerido, usa o primeiro canal
            self.bump_channel_id = text_channels[0]['id']
            channel_name = text_channels[0]['name']
            print(f'\n✅ Usando o primeiro canal disponível: #{channel_name}')
            print('💡 Dica: Se quiser outro canal, modifique o código')
        
        # Testa ambiente antes de iniciar o loop
        print(f'\n🔧 Configurando ambiente...')
        await self.test_channel_permissions()
        await self.get_disboard_commands_info()
        await self.bump_loop()

    def _generate_session_id(self):
        """Gera um session_id mais realista"""
        return f"{random.randint(10000000000000000, 99999999999999999)}"

    async def get_disboard_commands_info(self):
        """Busca informações atualizadas dos comandos do Disboard"""
        print('🔍 Buscando comandos atualizados do Disboard...')
        
        # Método 1: Buscar comandos do servidor
        url = f'https://discord.com/api/v9/guilds/{self.guild_id}/applications/302050872383242240/commands'
        
        try:
            async with self.session.get(url) as response:
                print(f'📡 Status do comando: {response.status}')
                if response.status == 200:
                    commands = await response.json()
                    print('✅ Comandos do Disboard disponíveis:')
                    for cmd in commands:
                        print(f"  - {cmd['name']} (ID: {cmd['id']}, Versão: {cmd.get('version', 'N/A')})")
                        if cmd['name'] == 'bump':
                            self.disboard_command_version = cmd.get('version')
                            print(f'🎯 Versão do comando bump encontrada: {self.disboard_command_version}')
                    return True
                else:
                    print(f'❌ Não foi possível buscar comandos: {response.status}')
                    return await self.get_global_disboard_commands()
        except Exception as e:
            print(f'❌ Erro ao buscar comandos: {e}')
            return await self.get_global_disboard_commands()

    async def get_global_disboard_commands(self):
        """Busca comandos globais do Disboard como fallback"""
        print('🔄 Buscando comandos globais do Disboard...')
        url = 'https://discord.com/api/v9/applications/302050872383242240/commands'
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    commands = await response.json()
                    print('✅ Comandos globais do Disboard:')
                    for cmd in commands:
                        print(f"  - {cmd['name']} (ID: {cmd['id']}, Versão: {cmd.get('version', 'N/A')})")
                        if cmd['name'] == 'bump':
                            self.disboard_command_version = cmd.get('version')
                            print(f'🎯 Versão global do comando bump: {self.disboard_command_version}')
                    return True
                else:
                    print(f'❌ Erro em comandos globais: {response.status}')
                    return False
        except Exception as e:
            print(f'❌ Erro em comandos globais: {e}')
            return False

    async def execute_bump_command(self):
        """Executa o comando slash /bump do Disboard com versão dinâmica"""
        if not self.bump_channel_id:
            print('❌ Canal não configurado!')
            return False

        # Se não temos a versão, tenta buscar novamente
        if not self.disboard_command_version:
            print('🔄 Buscando versão do comando...')
            await self.get_disboard_commands_info()

        # Usa versão padrão se não conseguir buscar
        version = self.disboard_command_version or "11926"

        payload = {
            'type': 2,
            'application_id': '302050872383242240',  # ID do Disboard
            'guild_id': self.guild_id,
            'channel_id': self.bump_channel_id,
            'session_id': self._generate_session_id(),
            'data': {
                'id': '947088344167366698',  # ID do comando bump
                'name': 'bump',
                'type': 1,
                'options': [],
                'version': version
            },
            'nonce': str(int(time.time() * 1000))
        }

        print(f'📤 Enviando bump com versão: {version}')
        url = 'https://discord.com/api/v9/interactions'
        
        try:
            async with self.session.post(url, json=payload) as response:
                print(f'📡 Status da resposta: {response.status}')
                
                if response.status in [200, 204]:
                    print('✅ Bump executado com sucesso!')
                    return True
                else:
                    # Tenta ler a resposta de erro
                    try:
                        error_text = await response.text()
                        error_data = json.loads(error_text)
                        print(f'❌ Erro detalhado: {error_data}')
                        
                        # Se for erro de versão, tenta atualizar
                        if error_data.get('code') == 50035:
                            print('🔄 Erro de versão, atualizando comandos...')
                            await self.get_disboard_commands_info()
                    except:
                        print(f'❌ Erro ao executar bump: {response.status}')
                    return False
        except Exception as e:
            print(f'❌ Erro na requisição: {e}')
            return False

    async def test_channel_permissions(self):
        """Testa se tem permissão no canal"""
        print(f'🔍 Testando permissões no canal...')
        url = f'https://discord.com/api/v9/channels/{self.bump_channel_id}'
        
        try:
            async with self.session.get(url) as response:
                print(f'📡 Status do teste de canal: {response.status}')
                if response.status == 200:
                    channel_data = await response.json()
                    print(f'✅ Canal #{channel_data.get("name")} acessível')
                    return True
                else:
                    print(f'❌ Sem acesso ao canal: {response.status}')
                    return False
        except Exception as e:
            print(f'❌ Erro ao testar canal: {e}')
            return False

    async def bump_loop(self):
        """Loop principal corrigido para executar bumps periodicamente"""
        bump_count = 0
        
        print(f'\n🚀 Iniciando loop de bump:')
        print(f'🏠 Servidor: {self.guild_id}')
        print(f'📝 Canal: {self.bump_channel_id}')
        print('⏰ Bumps automáticos a cada 2-3 horas\n')
        
        while True:
            bump_count += 1
            print(f'--- Tentativa de bump #{bump_count} ---')
            success = await self.execute_bump_command()
            
            if success:
                print(f'✅ Bump #{bump_count} realizado com sucesso!')
                # Espera 2-3 horas (aleatório) para o próximo bump
                wait_seconds = random.randint(7200, 10800)  # 2-3 horas em segundos
                wait_hours = wait_seconds / 3600
                print(f'⏰ Próximo bump em {wait_hours:.2f} horas...\n')
                await asyncio.sleep(wait_seconds)
            else:
                print(f'❌ Falha no bump #{bump_count}')
                # Em caso de erro, espera menos tempo e tenta atualizar versão
                print('🔄 Atualizando informações do comando...')
                await self.get_disboard_commands_info()
                print('⏰ Aguardando 10 minutos antes da próxima tentativa...')
                await asyncio.sleep(600)

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
    except Exception as e:
        print(f'❌ Erro crítico: {e}')
    finally:
        await bot.close()

if __name__ == "__main__":
    token = os.getenv('TOKEN')
    
    if not token:
        raise ValueError("❌ Variável de ambiente TOKEN não encontrada no Railway!")
    
    print('🎮 Discord Bump Bot - Setup Automático')
    print('🔄 Versão com Busca Dinâmica de Comandos')
    asyncio.run(main())
