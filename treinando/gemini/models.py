from django.db import models

# Create your models here.
class Pergunta(models.Model):
    id = models.AutoField(primary_key = True)
    user = models.CharField(max_length=100)
    pergunta = models.CharField(max_length=200)
    resposta = models.TextField(blank = True, editable=False)
    
    def __str__(self):
        return self.pergunta

class Instituicao(models.Model):
    id = models.AutoField(primary_key = True)
    nome = models.CharField(max_length = 255)

    def __str__(self):
        return self.nome

class Curso(models.Model):
    id = models.AutoField(primary_key = True)
    nome = models.CharField(max_length = 255)

    def __str__(self):
        return self.nome

class Coordenador(models.Model):
    id = models.AutoField(primary_key = True)
    nome = models.CharField(max_length = 255)
    senha = models.CharField(max_length = 30)
    email = models.CharField(max_length = 50, unique=True)
    instituicao = models.ForeignKey(Instituicao, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    tipoAcesso = models.CharField(max_length = 255, default = 'coordenador', editable=False)

class Aluno(models.Model):
    id = models.AutoField(primary_key = True)
    nome = models.CharField(max_length = 255)
    senha = models.CharField(max_length = 30)
    email = models.CharField(max_length = 50, unique=True)
    instituicao = models.ForeignKey(Instituicao, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    tipoAcesso = models.CharField(max_length = 255, default = 'aluno', editable=False)

class Script(models.Model):
    id = models.AutoField(primary_key = True)
    nome = models.CharField(max_length = 100)
    descricao = models.CharField(max_length = 5000)
    id_coordenador = models.ForeignKey(Coordenador, on_delete=models.DO_NOTHING, null = True)


class Pessoa(models.Model):
    id = models.AutoField(primary_key = True)
    nome = models.CharField(max_length = 255)
    email = models.CharField(max_length = 255)
    id_coordenador = models.ForeignKey(Coordenador, on_delete=models.DO_NOTHING, null = True)


    def __str__(self):
        return (self.nome)

class Setor(models.Model):
    id = models.AutoField(primary_key = True)
    nome = models.CharField(max_length = 150)
    pessoas = models.ManyToManyField(Pessoa, related_name = "pessoas")
    id_coordenador = models.ForeignKey(Coordenador, on_delete=models.DO_NOTHING, null = True)

class Indicador(models.Model):
    id = models.AutoField(primary_key = True)
    nome = models.CharField(max_length = 100)
    descricao = models.CharField(max_length = 1000)
    id_coordenador = models.ForeignKey(Coordenador, on_delete=models.DO_NOTHING, null = True)
    status = models.BooleanField(default=True)

class Relatorio(models.Model):
    id = models.AutoField(primary_key = True)
    data_inicial = models.DateField()
    data_final = models.DateField()
    indicadores = models.ManyToManyField(Indicador)

class Conversa(models.Model):
    id = models.AutoField(primary_key = True)
    id_indicador = models.ForeignKey(Indicador, on_delete=models.DO_NOTHING,  null = True)
    status = models.BooleanField(default=True)
    id_coordenador = models.ForeignKey(Coordenador, on_delete=models.DO_NOTHING, null = True)
    data_hora = models.DateTimeField(auto_now_add=True)



class Mensagem(models.Model):
    id = models.AutoField(primary_key = True)
    texto_mensagem = models.CharField(max_length = 10000)
    data_hora = models.DateTimeField()
    id_aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, null = True)
    id_coordenador = models.ForeignKey(Coordenador, on_delete=models.CASCADE, null = True)
    quem_enviou = models.CharField(max_length = 255)
    id_conversa = models.ForeignKey(Conversa, on_delete=models.DO_NOTHING,  null = True)



class ControleBot(models.Model):
    bot_pode_responder = models.BooleanField(default=True)
    id_aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, null = True)
