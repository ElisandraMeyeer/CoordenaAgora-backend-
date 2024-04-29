
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView
from django.core.mail import send_mail
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from .serializers import PerguntaSerializer, UsuarioSerializer, PessoaSerializer, SetorSerializer, IndicadorSerializer
from django.views.decorators.csrf import csrf_exempt
from .models import Pergunta, Script, Usuario, Pessoa, Setor, Indicador
import google.generativeai as genai
from .serializers import ScriptsSerializer
from rest_framework.decorators import api_view, action
import random

# Create your views here.

GOOGLE_API_KEY = "AIzaSyCLOvpQv7soejToFewHRrAWRaUkUVYQu3g"
profissionais = [
    {
        "nome": "Roberto Medeira",
        "profissao": "Coordenador do curso de informática",
        "curso": "Informática",
        "profissão": "Desenvolvedor"
    }
]

#---------------------------------------------INTEGRAÇÃO COM A GEMINI--------------------------------------------#


@api_view(['POST'])
@csrf_exempt
def create(request):
    serializer = PerguntaSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    user = request.data.get('user')
    pergunta_txt = request.data.get('pergunta')
    pergunta = serializer.instance

    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    chat = model.start_chat(history=[])
    # Você é o Chatbot customizado da empresa CoordenaAgora, a partir de agora você irá responder perguntas
    # com x informações, e caso sejam mandados prompt que não sejam relacionados a área da educação você
    # irá responder: "desculpe, sou um bot usado apenas para a resolução de problemas acadêmicos", obs isso inclui
    # perguntas que não tem haver com problemas como histórico escolar, encaminhamento, agendamento, comunicar ao
    # coordenador etc

    scripts = Script.objects.all()
    serialized_data = []
    for script in scripts:
        serializer = ScriptsSerializer(script)
        serialized_data.append(serializer.data)

    descricoes = [item['descricao'] for item in serialized_data] 
    descricoes.append("Caso você não consiga realizar o atendimento por conta própria, realize um agendamento")

    chat.send_message(descricoes)
    resposta = chat.send_message(pergunta_txt)


    if resposta.candidates[0].content.parts[
        0].text != "" and "desculpe, sou um bot usado apenas para a resolução de problemas acadêmicos" not in \
        resposta.candidates[0].content.parts[0].text:
        pergunta.resposta = resposta.candidates[0].content.parts[0].text

        if "encami" in pergunta.resposta.lower():
            for index in profissionais:
                print(index["nome"])
                if index['nome'] in pergunta.resposta:
                    email = request.data.get('email')
                    if Usuario.objects.filter(email=email).exists():
                        tema = 'Encaminhamento realizado para você para os dias x/y/2024'
                        msg = f'Um encaminhamento foi realizado para você para o atendimento do usuário {request.data.get("user")} nos dias x/y/2024, por favor entre em contato quando possível'
                        remetente = "ads.senac.tcs@gmail.com"
                        send_mail(assunto, mensagem, remetente, recipient_list=[email,'ads.senac.tcs@gmail.com'])
                        return Response({'mensagem': "O encaminhamento foi realizado com sucesso!"}, status=status.HTTP_201_CREATED)

            return Response({'mensagem': 'Ocorreu um erro ao realizar o encaminhamento, peço desculpas'}, status = status.HTTP_400_BAD_REQUEST)
            
        if "agend" in pergunta.resposta.lower():
            for index in profissionais:
                if index['nome'] in pergunta.resposta:
                    email = request.data.get('email')
                    if Usuario.objects.filter(email=email).exists():
                        tema = 'Reunião agendada para você para os dias x/y/2024'
                        msg = f'Um agendamento foi realizado para você para o atendimento do usuário {request.data.get("user")} no dia x/y/2024 as 18:00'
                        remetente = "ads.senac.tcs@gmail.com"
                        send_mail(assunto, mensagem, remetente, recipient_list=[email,'ads.senac.tcs@gmail.com'])
                        return Response({'mensagem': "O agendamento foi realizado com sucesso!"}, status=status.HTTP_201_CREATED)

            return Response({'mensagem': 'Ocorreu um erro ao realizar o agendamento, peço desculpas'}, status = status.HTTP_400_BAD_REQUEST)

        return Response({'mensagem': resposta.candidates[0].content.parts[0].text}, status=status.HTTP_201_CREATED)

    return Response({'mensagem': 'Erro ao fazer a pergunta'}, status=status.HTTP_201_CREATED)

#---------------------------------------------REDEFINIR SENHA--------------------------------------------#

@api_view(['POST'])
def redefinir_senha(request):
    if request.method == 'POST':
        email = request.data.get('email')
        if (Usuario.objects.filter(email=email).exists()):
            codigo = gerar_codigo_verificacao()
            enviar_codigo_por_email(email, codigo)
            return Response(codigo, status=status.HTTP_201_CREATED)
        return Response("Usuário não encontrado", status=status.HTTP_400_BAD_REQUEST)
    return Response("Não foi possível enviar o código de verificação", status=status.HTTP_400_BAD_REQUEST)

def gerar_codigo_verificacao():
    return str(random.randint(10000000, 99999999))

def enviar_codigo_por_email(email, codigo):
    assunto = 'Código de verificação para redefinição de senha'
    mensagem = f'Seu código de verificação é: {codigo}'
    remetente = "ads.senac.tcs@gmail.com"
    send_mail(assunto, mensagem,remetente, recipient_list=[email,'ads.senac.tcs@gmail.com'])

@api_view(['PUT'])
def alterar_senha(request):
    if request.method == 'PUT':
        email = request.data.get('email')
        senha = request.data.get('senha')  # Obtenha a senha dos dados da solicitação

        try:
            usuario = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            return Response("Usuário não encontrado", status=status.HTTP_404_NOT_FOUND)

        dados = {'usuario': usuario.usuario, 'senha': senha}
        serializer = UsuarioSerializer(usuario, data=dados)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response("Método de solicitação inválido", status=status.HTTP_405_METHOD_NOT_ALLOWED)


#-------------------------------------------------LOGIN------------------------------------------------#

class UsuarioViewSet(viewsets.ViewSet):
    serializer_class = UsuarioSerializer

    @action(detail=False, methods=['post'])
    def login(self, request):
        usuario = request.data.get("usuario")
        senha = request.data.get("senha")
        if (Usuario.objects.filter(usuario=usuario, senha=senha).exists()):
            return Response({'resultado': True}, status=status.HTTP_200_OK)
        else:
            return Response({'resultado': False}, status=status.HTTP_404_NOT_FOUND)

#-------------------------------------------------SCRIPTS------------------------------------------------#


@api_view(['GET'])
def listar_scripts(request):

    if request.method == 'GET':
        scripts = Script.objects.all()  # Get all objects in User's database (It returns a queryset)

        serializer = ScriptsSerializer(scripts,
                                       many=True)  # Serialize the object data into json (Has a 'many' parameter cause it's a queryset)

        return Response(serializer.data)  # Return the serialized data

    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def cadastrar_script(request):
    if request.method == 'POST':
        serializer = ScriptsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def editar_script(request, id):
    try:
        id = Script.objects.get(id=id)
    except Script.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = ScriptsSerializer(id, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def excluir_script(request, id):
    try:
        id = Script.objects.get(id=id)
    except Script.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        id.delete();
        return Response(status=status.HTTP_204_NO_CONTENT)




#-----------------------------------------------PESSOAS------------------------------------------------#


@api_view(['GET'])
def listar_pessoas(request):
    if request.method == 'GET':
        pessoas = Pessoa.objects.all()  # Get all objects in User's database (It returns a queryset)

        serializer = PessoaSerializer(pessoas,
                                      many=True)  # Serialize the object data into json (Has a 'many' parameter cause it's a queryset)

        return Response(serializer.data)  # Return the serialized data

    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def cadastrar_pessoa(request):
    if request.method == 'POST':
        serializer = PessoaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def listar_pessoas_por_ids(request):
    if request.method == 'GET':
        ids_list = request.GET.getlist('ids[]', [])  # Get the list of IDs from the query parameters
        pessoas = Pessoa.objects.filter(id__in=ids_list)
        serializer = PessoaSerializer(pessoas, many=True)
        return Response(serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def listar_pessoas_por_nome(request):
    if request.method == 'GET':
        nome_filtro = request.GET.get('nome', '')  # Obtém o parâmetro 'nome' da query string
        pessoas = Pessoa.objects.filter(nome__icontains=nome_filtro)  # Filtra as pessoas com base no nome fornecido
        serializer = PessoaSerializer(pessoas, many=True)
        return Response(serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def editar_pessoa(request, id):
    try:
        id = Pessoa.objects.get(id=id)
    except Pessoa.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = PessoaSerializer(id, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def excluir_pessoa(request, id):
    try:
        id = Pessoa.objects.get(id=id)
    except Pessoa.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        id.delete();
        return Response(status=status.HTTP_204_NO_CONTENT)


#--------------------------------------------INDICADORES------------------------------------------------#



@api_view(['GET'])
def listar_indicadores(request):
    if request.method == 'GET':
        indicadores = Indicador.objects.all()  # Get all objects in User's database (It returns a queryset)

        serializer = IndicadorSerializer(indicadores,
                                         many=True)  # Serialize the object data into json (Has a 'many' parameter cause it's a queryset)

        return Response(serializer.data)  # Return the serialized data

    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def cadastrar_indicador(request):
    if request.method == 'POST':
        serializer = IndicadorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def listar_indicadores_por_nome(request):
    if request.method == 'GET':
        nome_filtro = request.GET.get('nome', '')
        indicadores = Indicador.objects.filter(nome__icontains=nome_filtro)
        serializer = IndicadorSerializer(indicadores, many=True)
        return Response(serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def editar_indicador(request, id):
    try:
        id = Indicador.objects.get(id=id)
    except Indicador.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = IndicadorSerializer(id, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def excluir_indicador(request, id):
    try:
        id = Indicador.objects.get(id=id)
    except Indicador.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        id.delete();
        return Response(status=status.HTTP_204_NO_CONTENT)


#------------------------------------------------SETORES------------------------------------------------#


@api_view(['GET'])
def visualizar_setores(request):

    if request.method == 'GET':
        scripts = Setor.objects.all()  # Get all objects in User's database (It returns a queryset)

        serializer = SetorSerializer(scripts, many=True)  # Serialize the object data into json (Has a 'many' parameter cause it's a queryset)

        return Response(serializer.data)  # Return the serialized data

    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def cadastrar_setores(request):
    if request.method == 'POST':
        serializer = SetorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def editar_setores(request, id):
    try:
        id = Setor.objects.get(id=id)
    except Setor.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = SetorSerializer(id, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def excluir_setores(request, id):
    try:
        id = Setor.objects.get(id=id)
    except Setor.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        id.delete();
        return Response(status=status.HTTP_204_NO_CONTENT)


# @api_view(['GET'])
# def listar_informacoes_inicio(request):

    # fazer depois com que essa rota retorne o número de conversas
    # e número de conversas sobre determinado assunto

