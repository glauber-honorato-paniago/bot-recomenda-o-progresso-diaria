import json
from datetime import datetime, timedelta
from functools import reduce

import pytz

# Defina o fuso horário para Brasília
brasil_tz = pytz.timezone('America/Sao_Paulo')


def is_weekend(date_obj):
    # Verificar se o dia da semana é sábado (6) ou domingo (0)
    return date_obj.weekday() in [5, 6]


def current_sprint(sprint_data):
    current_sprint_ = 1
    sprint_day = datetime.strptime(
        sprint_data['start_work'], '%d/%m/%Y').replace(tzinfo=brasil_tz)
    current_day = datetime.now(brasil_tz).replace(
        hour=1, minute=0, second=0, microsecond=0)

    while True:
        calc_day = sprint_day + timedelta(days=sprint_data['sprint_duration'])
        if calc_day < current_day:
            sprint_day = calc_day
            current_sprint_ += 1
        else:
            break

        # retornando a sprint atual e o dia que a mesma começou

    return (current_sprint_, sprint_day)


def remaining_days_sprint(sprint_data):
    """Função retorna um objeto datetime com os dias restantes para o fim da sprint"""
    current_day = datetime.now(brasil_tz).replace(
        hour=0, minute=0, second=0, microsecond=0)

    finished_days = current_day - current_sprint(sprint_data)[1]
    remaining_days = timedelta(days=sprint_data['sprint_duration']) - finished_days

    return remaining_days


def finished_working_sprint_days(started_sprint_day):
    """Funcao designada para retonar os dias uteis ja finalizados da sprint"""
    current_day = datetime.now(brasil_tz).replace(
        hour=0, minute=0, second=0, microsecond=0)
    working_days = 0

    while started_sprint_day <= current_day:
        started_sprint_day += timedelta(days=1)

        if not is_weekend(started_sprint_day):
            working_days += 1

    return working_days


def get_total_sprint_workload(sprint_data):
    # obtendo a soma de toda a cargoraria das aulas
    return reduce(lambda total, i: total + sum(i), sprint_data.values(), 0)


def get_daily_recomendation(sprint_data, sprint_taks_array):
    # obtendo o numero da sprint atual e os dias uteis da mesma.
    current_sprint_, started_sprint_day = current_sprint(sprint_data)
    sprint_working_days = sprint_data['sprint_working_day']

    sprint_current_data = sprint_taks_array

    # obtendo a carga horaria total da sprint
    total_sprint_hours = get_total_sprint_workload(sprint_taks_array)

    # obtendo carga horaria de aula recomendada (em minutos) por dia
    workload_per_day = total_sprint_hours / sprint_working_days

    # obtendo qual a carga horaria ja deveria ser comprida, visando os dias ja finalizados da sprint
    class_minute_recommend = workload_per_day * \
        finished_working_sprint_days(started_sprint_day)
    # obtendo o numero da aula recomendada a ser comprida ate o presente dia
    # apartir da carga horaria (em minutos) que ja deveria ser comprida.
    # len(value) seria o total de aulas

    acumulator = 0
    for key, value in sprint_current_data.items():
        class_number = 0
        for class_ in value:
            acumulator += class_
            class_number += 1

            if acumulator >= class_minute_recommend:
                total_classes = len(value)
                return (key, class_number, total_classes)


def get_formated_daily_recomendation():
    def format_recomendation_msg(recomendation):
        if recomendation[2] > 1:
            recomendation_str = f'**"{recomendation[0]}"**, referente à aula **{recomendation[1]}**'
        else:
            recomendation_str = f'**"{recomendation[0]}"**'

        return recomendation_str

    with open('sprint_data.json', 'r', encoding='utf-8') as arquivo:
        sprint_data = json.load(arquivo)
        c_sprint, start_sprint_day = current_sprint(sprint_data)

        sprint_tasks = sprint_data['sprint_data'][f'sprint_{c_sprint}']

        tasks = {}
        optional_taks = {}
        for task, task_value in sprint_tasks.items():
            if task[:10] == '[Opcional]':
                optional_taks[task] = task_value
            else:
                tasks[task] = task_value

        # obtendo a carga horaria total da sprint
        total_hours_of_sprint = get_total_sprint_workload(tasks)
        # obtendo a carga horaria diaria recomendada
        daily_hours_recomendation_tasks = total_hours_of_sprint / \
            sprint_data['sprint_working_day']

        total_hours_of_sprint_with_optional_taks = get_total_sprint_workload(
            {**tasks, **optional_taks})
        daily_hours_recomendation_optional_tasks = total_hours_of_sprint_with_optional_taks / \
            sprint_data['sprint_working_day']

        # bildando recomandacoes
        recomendation = get_daily_recomendation(sprint_data, tasks)
        recomendation_str = format_recomendation_msg(recomendation)

        # se ouver tarefas opcionais aqui que serao adicionadas
        workload_recomendation_str_optional_task, recomendation_str_optional_tasks = None, None
        if optional_taks:
            recomendation_with_optional_tasks = get_daily_recomendation(
                sprint_data, {**tasks, **optional_taks})
            recomendation_with_optional_tasks_str = format_recomendation_msg(
                recomendation_with_optional_tasks)
            workload_recomendation_str_optional_task = f"""
_Caso estiver realizando as **tarefas opcionais**, a ***carga horária diária*** recomendada é de **{round(daily_hours_recomendation_optional_tasks)} minutos.**_
"""
            recomendation_str_optional_tasks = f"""
_Caso estiver realizando as **tarefas opcionais**, é recomendado que você termine o dia de hoje, pelo menos, no curso de {recomendation_with_optional_tasks_str} da trilha._
"""

        # obtendo o dia atual da sprint
        day_now = datetime.now(brasil_tz).replace(
            hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        current_sprint_day = (day_now - start_sprint_day).days + 1

        # obtendo a lista de cursos da sprint
        courses = list(sprint_data['sprint_data'][f'sprint_{c_sprint}'].keys())
        curses_str = ''
        # formatando a lista de cursos em string
        for curse in courses:
            if curse is courses[-2]:
                curses_str += f'**"**{curse}**"** e '

            else:
                curses_str += f'**"**{curse}**"**, '

        recomendation_text = f"""
Na sprint atual, temos um total de **{total_hours_of_sprint} minutos** divididos em **{len(courses)} cursos** ({curses_str[:-2]}).

Portanto, a ***carga horária diária*** recomendada é de **{round(daily_hours_recomendation_tasks)} minutos.**{workload_recomendation_str_optional_task if workload_recomendation_str_optional_task else ''}
*Levando em consideração apenas os **dias úteis** da sprint.*

Hoje é o **{current_sprint_day}º dia** da **Sprint {c_sprint}**, ou seja, a sprint está **{round((current_sprint_day * 100) / sprint_data['sprint_duration'])}% concluida.**
Portanto, é recomendado que você termine o dia de hoje, pelo menos, no curso de {recomendation_str} da trilha.{recomendation_str_optional_tasks if recomendation_str_optional_tasks else ''}

***Tenha uma excelente tarde!***
"""

        return recomendation_text


def get_formated_days_finish_sprint():
    with open('sprint_data.json', 'r', encoding='utf-8') as arquivo:
        sprint_data = json.load(arquivo)
        days_for_finish_sprint = remaining_days_sprint(sprint_data).days - 1

        days_str = 'dias' if days_for_finish_sprint > 1 else 'dia'

        if days_for_finish_sprint == 0:
            days_for_finish_sprint = 'Menos de 1'

        sprint = current_sprint(sprint_data)[0]
        return f"🕗 {days_for_finish_sprint} {days_str} para o final da Sprint {sprint}."
