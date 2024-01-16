
# Bot de Recomendação Diária para Sprint (Scrum)
Apresentação:
O Bot de Recomendação Diária foi projetado para enviar mensagens diárias de progresso em um servidor e canal específicos no Discord, conforme programado. Embora tenha aplicações para o gerenciamento de atividades diárias, como estudos e programação, seu propósito central é fornecer orientações diárias para uma sprint, dentro do contexto da metodologia Scrum, mas pode ser alterado facilmente para o contexto desejado alterando a mensagem de recomedação diaria no arquivo __functions.py__.

# Funcionalidades:
## Recomendação de Progresso Diária:
Todos os dias úteis, no horário especificado (por padrão, 13:30 - horário de Brasília), o bot enviará uma recomendação diária de progresso da sprint. Essa recomendação é calculada com base na carga horária total da sprint, seu andamento atual e inclui sugestões específicas de cursos, aulas ou tarefas a serem abordadas no dia. As sugestões são adaptadas à carga horária da sprint, proporcionando uma orientação personalizada para o desenvolvimento diário.

## Contador para a Conclusão da Sprint:
O bot também oferece uma funcionalidade para visualizar quantos dias faltam para a conclusão da sprint atual diretamente na barra de status. Isso permite uma gestão eficiente do tempo, ajudando a manter o foco na consecução dos objetivos da sprint.

Este bot é uma ferramenta valiosa para equipes que seguem a metodologia Scrum, oferecendo uma abordagem estruturada para o acompanhamento diário do progresso e incentivando uma rotina disciplinada de estudos e desenvolvimento.

# Como Utilizar:
- Defina o servidor e canal específicos no Discord para receber as recomendações diárias.
Horário de Envio.
- As recomendações serão enviadas todos os dias úteis às 13:30 (horário de Brasília). Ajuste conforme necessário.
- Configuração das Tarefas da Sprint:

Configure os dados das tarefas no arquivo __sprint_data.json__, como a duração de cada sprint, a data de início, os dias úteis e as tarefas planejadas.
Ao configurar as tarefas da sprint, certifique-se de inserir corretamente o número da sprint, por exemplo: sprint_1, sprint_2, ... Isso é essencial para o funcionamento adequado do bot.

Cada tarefa deve ser listada como um item dentro do array correspondente à sua sprint. A duração de cada tarefa é configurada em minutos dentro do array específico dessa tarefa. Se a tarefa envolver um curso ou microtarefa com várias aulas ou etapas, cada aula ou microtarefa pode ter sua duração adicionada ao array correspondente. Dessa forma, além da tarefa recomendada para o dia, também são geradas sugestões de aula ou microtarefa recomendada para o dia.

Caso a tarefa inicie com __[Opcional]__, serão geradas duas recomendações diárias. Uma conterá as recomendações não opcionais, enquanto a outra incluirá as recomendações opcionais calculadas.