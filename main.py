import asyncio
from datetime import datetime, timedelta

import discord
import pytz

import functions

# Defina o fuso horário para Brasília
brasil_tz = pytz.timezone('America/Sao_Paulo')


TOKEN = 'Your bot token'
server_id = 'Your server id'
main_channel_id = 'Your channel id'


class Client(discord.Client):
    def __init__(self) -> None:
        super().__init__(intents=discord.Intents.default())
        server = self.get_guild(server_id)
        channel = server.get_channel(main_channel_id)
        self.manager = Manager(self, channel)
        self.synced = False

    async def on_ready(self):
        # deixando disponiveis todos comandos
        self._start_list_commands_avaliable()

        await self.wait_until_ready()

        # sincronizando a lista de comandos do bot
        if not self.synced:
            await self.tree_commands.sync(guild=discord.Object(id=server_id))
            self.synced = True

        # iniciando o manager
        await self.manager.main_loop()

    def _start_list_commands_avaliable(self):
        self.tree_commands = discord.app_commands.CommandTree(self)

        @self.tree_commands.command(guild=discord.Object(id=server_id), name='status', description='obtem o status do bot.')
        async def status(iteraction):
            await iteraction.response.send_message('bot is working!', ephemeral=False)

        @self.tree_commands.command(guild=discord.Object(id=server_id), name='papagaio', description='retorna o que o usuario digitou.')
        async def papagaio(iteraction, text: str):
            await iteraction.response.send_message(text, ephemeral=False)

    def start_bot_(self):
        self.run(TOKEN)


class Manager:
    def __init__(self, client, channel=None) -> None:
        self.channel = channel
        self.client = client
        self.tasks_completed = 0
        self.daily_tasks = [
            {'time': '13:30', 'next_execution': None, 'name': 'Daily_recomendation',
                'action': self.send_daily_recommendation},
            {'time': '00:00', 'next_execution': None,
                'name': 'change_status', 'action': self.chanche_bot_status}
        ]

    def schedule_task(self, task):
        """Função designada para agendar a proxima execução da tarefa recebida como argumento
        para agendar, é usado como parametro a hora que a tarefa é executada, apartir disso
        a data e hora é agendada no dicionario na chave next_execution como um objeto datetime."""
        def time_has_passed(hour, minute):
            now = datetime.now(brasil_tz)
            reference_time = now.replace(hour=hour, minute=minute, microsecond=0)

            if now >= reference_time:
                return True

        task_date = task['time'].split(':')
        hour, minute = int(task_date[0]), int(task_date[1])

        date_task = datetime.now(brasil_tz)
        # caso a hora e o minuto indicado ja tiver passado, a data agendada sera
        # agendada com o mesmo horario no dia seguinte.
        if time_has_passed(hour, minute):
            date_task += timedelta(days=1)

        time_task = date_task.replace(hour=hour, minute=minute, second=0, microsecond=0)

        # alterando a proxima execucao para a data agendada
        task['next_execution'] = time_task

    async def check_time_execution_tasks(self):
        """Funcao designada para checar se agora é o horario de execucao de 
        uma determinada tarefa, se verdadeiro, a mesma sera executada. caso a tarefa
        não esteja agendada, a funcao para agenda-la sera executada."""
        for task in self.daily_tasks:
            if task['next_execution'] is None:
                self.schedule_task(task)
                continue

            if datetime.now(brasil_tz) >= task['next_execution']:
                # executando a task
                await task['action']()
                # agendando a task novamente
                self.schedule_task(task)
                self.tasks_completed += 1

                # logs
                print(f"task {task['name']} has been completed.")
                print(f'tasks completeds: {self.tasks_completed}')
                print('task lists:', self.daily_tasks)

    async def send_daily_recommendation(self):
        """Funcao designada para enviar a recomendacao diaria da sprint
        no canal do servidor do discord passado como argumento para essa classe."""
        if functions.is_weekend(datetime.now(brasil_tz)):
            return

        date_now = datetime.now(brasil_tz).strftime("%d/%m/%Y")
        recommendation = functions.get_formated_daily_recomendation()

        embed = discord.Embed(
            title=f"🕗 Recomendação de Progresso Diária - {date_now}",
            description=recommendation,
            color=discord.Color(0xFFA500)  # Cor do embed
        )

        # apagando todas as mensagens do canal
        await self.channel.purge()

        # evinado as mensagens diarias
        allowed_mentions = discord.AllowedMentions(roles=True)
        await self.channel.send('Boa tarde <@&1130598673143840769>, como vão?', allowed_mentions=allowed_mentions)
        await self.channel.send(embed=embed)

    async def chanche_bot_status(self):
        """Funcao designada setar o status do bot do discord para quantos dias
        faltam para acabar a sprint"""
        days_for_finish_sprint = functions.get_formated_days_finish_sprint()
        await self.client.change_presence(activity=discord.CustomActivity(
            name=days_for_finish_sprint))

    async def main_loop(self):
        """Função designada para checar acada 10 segundo de forma assincrona
        a função que checa os horarios de execução das tarefas"""
        # setando o status do bot inicial
        await self.chanche_bot_status()
        await self.send_daily_recommendation()

        print('started at:', datetime.now(brasil_tz).strftime("%d/%m/%Y %H:%M:%S"))

        while True:
            await self.check_time_execution_tasks()

            await asyncio.sleep(10)


Client().start_bot_()
