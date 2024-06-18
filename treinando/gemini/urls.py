from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    # path('', views.get_users, name='get_all_users'),
    path('scripts', views.listar_scripts, name='listar_todos_scripts'),
    path('cadastrar-script', views.cadastrar_script, name='cadastrar_script'),
    path('editar-script/<int:id>', views.editar_script, name='editar_script'),
    path('excluir-script/<int:id>', views.excluir_script, name='excluir_script'),

    path('pessoas', views.listar_pessoas, name='listar_pessoas'),
    path('cadastrar-pessoa', views.cadastrar_pessoa, name='cadastrar_pessoa'),
    path('editar-pessoa/<int:id>', views.editar_pessoa, name='editar_pessoa'),
    path('excluir-pessoa/<int:id>', views.excluir_pessoa, name='excluir_pessoa'),
    path('pessoas-por-ids', views.listar_pessoas_por_ids, name='listar_pessoas_por_ids'),
    path('pessoas-por-nome', views.listar_pessoas_por_nome, name='listar_pessoas_por_nome'),

    path('indicadores', views.listar_indicadores, name='listar_indicadores'),
    path('cadastrar-indicador', views.cadastrar_indicador, name='cadastrar_indicador'),
    path('editar-indicador/<int:id>', views.editar_indicador, name='editar_indicador'),
    path('excluir-indicador/<int:id>', views.excluir_indicador, name='excluir_indicador'),
    path('indicadores-por-nome', views.listar_indicadores_por_nome, name='listar_indicadores_por_nome'),

    path('visualizar-setores/', views.visualizar_setores, name='visualizar-setores'),
    path('cadastrar-setores', views.cadastrar_setores, name='cadastrar-setores'),
    path('editar-setores/<int:id>', views.editar_setores, name='editar-setores'),
    path('excluir-setores/<int:id>', views.excluir_setores, name='excluir-setores'),


    path('redefinir-senha', views.redefinir_senha, name='redefinir_senha'),
    path('alterar-senha', views.alterar_senha, name='alterar_senha'),
    path('cadastrar-aluno', views.cadastrar_aluno, name='cadastrar-_aluno'),

    path('instituicoes-por-nome', views.listar_instituicoes_por_nome, name='listar_instituicoes_por_nome'),
    path('cursos-por-nome', views.listar_cursos_por_nome, name='listar_cursos_por_nome'),

    path('perguntas', views.create, name='perguntas'),
    path('dashboard', views.dashboard, name='informacoes_dashboard'),

    path('salvar-mensagem', views.salvar_mensagem_coordenador, name='salvar_mensagem_coordenador'),
    path('listar-mensagens-por-aluno', views.listar_mensagens_por_aluno, name='listar_mensagens_por_aluno'),
    path('listar-todos-alunos', views.listar_todos_alunos, name='listar_todos_alunos'),
    # path("chat", views.index, name="index"),
    # path("<str:room_name>/", views.room, name="room"),
    path('mudar-status-bot', views.mudar_status_bot, name='mudar_status_bot'),
    path('verificar-status-bot', views.verificar_status_bot, name='verificar_status_bot'),
    path('gerar-relatorio', views.gerar_relatorio, name='gerar_relatorio')











    # path('inicio', views.listar_informacoes_inicio, name='listar_informacoes_inicio'),


    # path('relatorio', views.gerar_relatorio, name='gerar-relatorio')

]
