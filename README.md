# Django - REST API de Todos

## Rotas da aplicação

A aplicação possui rotas básicas de criação e autenticação dos usuários e rotas de criação, listagem, modificação e exclusão de todos. As rotas são:

- **api/register/ :** Rota para criação de usuários (recebe requisições do tipo POST);
- **api/login/ :** Rota para criação de uma token utilizada para receber ou editar os todos (recebe requisições do tipo POST);
- **api/logout/ :** Rota para excluir uma token do banco de dados (recebe requisições do tipo GET);
- **api/todos/ :** Rota para listagem e criação de todos (recebe requisições do tipo GET e POST);
- **api/todos/_id_/ :** Rota para detalhamento, modificação ou exclusão de um todo específico (recebe requisições do tipo GET, POST, PUT, PATCH e DELETE);

## Configuração do ambiente de desenvolvimento

Este tutorial utiliza Python 3.10.4 e Pipenv 2022.5.2

Você pode checar as versões instaladas com:

```console
python --version
pipenv --version
```

Crie uma pasta para a API:

```console
mkdir django-todo-api
cd django-todo-api
```

Crie um novo ambiente de desenvolvimento, um arquivo Pipfile deve ser criado:

```console
pipenv shell
```

Nesse ambiente de desenvolvimento, instale Django e Django Rest Framework. Um arquivo Pipfile.lock será criado detalhando as versões utilizadas. Este tutorial utiliza as versões de django 4.0.4 e djangorestframework 3.13.1.

```console
pipenv install django
pipenv install djangorestframework
```

Inicie um projeto com o nome todoapi. Uma pasta **todoapi** será criada.

```console
django-admin startproject todoapi
cd todoapi
```

Na pasta **todoapi**, inicie uma aplicação de todos:

```console
python manage.py startapp todos
```

No arquivo **/todoapi/settings.py**, adicione as seguintes aplicações:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Linhas adicionadas
    'rest_framework',
    'rest_framework.authtoken',
    'todos'
]
```

Também iremos utilizar as funcionalidades de autenticação e permissões por token para manipulação dos todos. Para isso, acrescente as seguintes linhas ao final do arquivo **/todoapi/settings.py**:

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}

```

## Criação do modelo de Todo

No arquivo **/todos/models.py**, crie uma nova classe (herdeira da classe Models do próprio Django).

```python
class Todo(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField(max_length=1000)
    is_completed = models.BooleanField(default=False)
    owner = models.ForeignKey(
        'auth.User', related_name='todos', on_delete=models.CASCADE)

    class Meta:
        ordering = ['created_at']

```

Os seus atributos são:

```python
created_at = models.DateTimeField(auto_now_add=True)
```

Esta coluna na tabela indicará a data de criação do **todo** e é preenchida automaticamente.

```python
content = models.TextField(max_length=1000)
```

Esta indicará o conteúdo do **todo**. Ela possui um limite de 1000 caracteres.

```python
is_completed = models.BooleanField(default=False)
```

Esta indica se o **todo** está marcado como completo ou não. Ela não precisa ser indicada na criação do **todo** e será automaticamente definida como _false_.

```python
owner = models.ForeignKey('auth.User',related_name='todos', on_delete=models.CASCADE)
```

Por fim, esta indica quem é o proprietário do **todo** com uma _ForeignKey_ (uma relação _ManyToOne_, já que um **todo** pertence a um único usuário e um usuário pode ter vários **todos**).

```python
class Meta:
      ordering = ['created_at']
```

Ao sobrescrever a classe **Meta**, dizemos para o banco de dados que a ordem ao solicitar os **todos** deve ser baseada na data de criação.

## Migração para o banco de dados

Para construir as tabelas do banco de dados, tanto dos **todos** quanto das tabelas de usuários (já inclusas no _djangorestframework_), na pasta do arquivo **manage.py**:

```console
python manage.py makemigrations
python manage.py migrate
```

Você pode verificar pelo Beekeeper-Studio, abrindo o arquivo _/db.sqlite3_ que as tabelas foram criadas.

## Criação de usuários

Primeiramente, vamos escrever o código de criação de usuários e permitir que os mesmos façam login.
Para isso, primeiramente vamos criar um arquivo **serializer.py** na pasta **todos**. Esse código será responsável para transmitir as informações recebidas a partir da requisição HTTP para um formato que seja utilizável em Python. No arquivo, insira:

```python
from django.contrib.auth.models import User
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
```

Por partes:

```python
class Meta:
        model = User
        fields = ['id', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}
```

Sobrescreve a classe Meta, indicando qual é o modelo utilizado do serializer, quais campos serão acessados e define que a senha só pode ser escrita e não lida.

```python
def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
```

Sobrescreve a função de criação de um usuário, recebendo as informações validadas automaticamente, criando um usuário, definindo uma senha e retornando o usuário criado.

Em seguida, no arquivo **/todos/views.py**, vamos adicionar uma função responsável por controlar a criação de um usuário a partir da requisição HTTP recebida:

```python
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from rest_framework import generics

from .serializers import UserSerializer

class UserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
```

Essa classe herda a **CreateAPIView**, uma view que contém o método POST para a criação de uma entidade.

Por fim, no arquivo **urls.py** na pasta do projeto, vamos adicionar a rota de criação de usuário:

```python
from django.urls import path
from todos.views import UserCreate

urlpatterns = [
    path('api/register/', UserCreate.as_view()),
]
```

Após esses passos, você deve ser capaz de criar um novo usuário e visualizá-lo no banco de dados.

## Login de um usuário

Para criar, listar, editar ou deletar **todos**, os usuários precisam estar logados. Para verificar isso, as rotas de **todos** irão solicitar uma token, criada automaticamente pelo _djangorestframework_ quando o usuário faz login.

Para isso, nas **urlpatterns** do arquivo **urls.py**, vamos adicionar:

```python
from django.urls import path
from todos.views import UserCreate
# Nova linha
from rest_framework.authtoken import views

urlpatterns = [
    path('api/register/', UserCreate.as_view()),
    # Nova linha
    path('api/login/', views.obtain_auth_token),
]
```

Agora, enviando uma solicitação do tipo POST para a rota **api/login/** contendo um **username** e **password**, a resposta será uma token para autenticar o usuário.

## Logout de um usuário

O _djangorestframework_ não tem uma **view** específica para logout de um usuário. Para isso, no arquivo **todos/views.py** vamos adicionar:

```python
# Novas importações
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status

class Logout(APIView):
    def get(self, request, format=None):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)
```

E no arquivo **urls.py** vamos adicionar uma rota de logout:

```python
# Nova importação
from todos.views import Logout, UserCreate

urlpatterns = [
    path('api/register/', UserCreate.as_view()),
    path('api/login/', views.obtain_auth_token),
    # Nova linha
    path('api/logout/', Logout.as_view()),
]
```

Para efetuar o logout, a solicitação enviada para tal rota deve conter um Header com o título Authorization e seu conteúdo deve ser 'Token {token fornecida}', por exemplo:

```
Token 6fa09af86d73d66a5e6f15123577cb3edf9224a7
```

## Serializer dos todos

Os serializers em Django permitem que dados complexos como querysets e instâncias de modelos sejam convertidos para tipos utilizados por Python que, por sua vez, serão renderizados em JSON ou XML.

No arquivo **serializers.py**, adicione as seguintes linhas:

```python
# Nova importação
from .models import Todo

# Novo serializer
class TodoSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Todo
        fields = ['id', 'content', 'is_completed', 'owner', 'created_at']
```

Esse serializer herda a classe ModelSerializer, que utiliza um modelo já existente, no caso o modelo **Todo**. No entanto, adicionamos um novo campo, chamado **owner**, que será usado para indicar o criador do todo. Na classe **Meta** indicamos o modelo utilizado e os campos que podem ser repassados pelo serializer.

## Criação e listagem dos todos

Primeiramente iremos criar uma view que permite que o usuário crie um todo e que visualize todos seus todos. Essa view será acessada pela rota **api/todos/**, permitindo os métodos GET e POST.

A view herda a classe **ListCreateAPIView** que possui as funcionalidades listadas acima. A view é iniciada da seguinte forma:

```python
# Novas importações
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Todo
from .serializers import TodoSerializer, UserSerializer

# Nova view
class TodoList(generics.ListCreateAPIView):

    queryset = Todo.objects.all()
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated]
```

Essa view utiliza o queryset de todos todos (que serão filtrados nas requisições), o serializer criado anteriormente e uma permission_class que exige que o usuário esteja autenticado. O primeiro método criado será a criação de um todo. Vamos sobrescrever a função **post** da classe **ListCreateAPIView**, adicionando à classe **TodoList**:

```python
def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=request.user)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
```

A primeira parte dessa função aciona o serializer para verificar se os dados da requisição estão corretos. A segunda parte envia a resposta com o todo criado.

Já o método **get** é responsável por sobrescrever a **queryset**, filtrando apenas os todos do usuário autenticado e retornando os encontrados:

```python
def get(self, request):
        queryset = Todo.objects.filter(owner=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
```

Por fim, precisamos adicionar essa view a uma rota da aplicação:

```python

from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken import views
# Nova importação
from todos.views import Logout, TodoList, UserCreate

urlpatterns = [
    path('api/login/', views.obtain_auth_token),
    path('api/logout/', Logout.as_view()),
    path('api/register/', UserCreate.as_view()),
    # Nova rota
    path('api/todos/', TodoList.as_view()),
    ,

]
```

## Criação, edição e exclusão de um todo específico

Para tal finalidade, utilizaremos a classe **RetrieveUpdateDestroyAPIView**. Novamente definimos a **queryset** e o **serializer**, porém adicionamos uma nova propriedade chamada **permission_classes** que contém apenas uma classe chamada **UserIsOwner**, que verifica se o usuário solicitando tal operação é o proprietário do todo.

```python
# Nova importação
from .permissions import UserIsOwner

# Nova view
class TodoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer
    permission_classes = [UserIsOwner]
```

Para utilizarmos tal permissão, criamos um arquivo na pasta **todos** chamado **permissions.py**:

```python
from rest_framework import permissions

class UserIsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.owner == request.user:
            return True
        return False
```

A classe **UserIsOwner** herda da classe **BasePermission** e sobrescreve o método **has_object_permission**, retornando **True** caso o usuário da requisição seja o proprietário do objeto.

Por fim, para criar uma rota para tais métodos, editamos o arquivo **urls.py**:

```python
from django.urls import include, path
from rest_framework.authtoken import views
# Nova importação
from todos.views import Logout, TodoDetail, TodoList, UserCreate

urlpatterns = [
    path('api/login/', views.obtain_auth_token),
    path('api/logout/', Logout.as_view()),
    path('api/register/', UserCreate.as_view()),
    path('api/todos/', TodoList.as_view()),
    # Nova rota
    path('api/todos/<int:pk>/', TodoDetail.as_view()),
]
```

Nessa rota, **\<int:pk\>** refere-se ao **id** do todo. Para acessar essa e a rota **api/todos/**, devemos enviar, no header da requisição, a token gerada no início da sessão da mesma forma que fizemos no logout.

Dessa forma uma API (bem) básica de todos estará concluída!
