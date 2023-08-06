# Assistant Fulfillment Helper
Esta biblioteta tem como objetivo facilitar a criação de *webhooks* para os nós de intenção da [Assistente TOTVS](https://produtos.totvs.com/ficha-tecnica/tudo-sobre-o-totvs-carol-assistente/). Com poucas linhas de código, é possivel criar uma regra de negócio customizada em sua própria estrutura de servidor.

## Pré-requisitos:
- [>= Python 3.7](https://www.python.org/downloads/)

## Por onde começar?
Crie um projeto novo e instale o módulo usando PyPI:
```sh
pip install assistant-fulfillment-helper
```

Importe e instancie a classe ``FulfillmentHelper`` para poder definir sua própria regra de negócio. 
```python
from assistant_fulfillment_helper import FulfillmentHelper

fh = FulfillmentHelper()
fh.start() # Inicia um servidor local
```

O código acima irá instanciar o módulo e servirá um Webhook pronto para receber as requisições dos seus nós de intenção da Assistente. Para checar se está tudo certo, abra seu navegador e acesse http://127.0.0.1:5052 (endereço padrão).

O endereço (path) raíz possui dois roteamentos:
- ``GET``: Trás uma mensagem de sucesso com ``http response 200``, e pode ser utilizada como *health check*.
- ``POST``: Iniciará o processamento das [intenções definidas](#definindo-uma-intenção) na sua aplicação. É a chamada que o servidor espera receber da Assistente.

## Definindo uma Intenção
Para definir uma intenção, basta adicionar o decorator ``intent()`` no método que deverá ser o callback para aquela intenção. Uma intenção deverá estar vinculada à um Webhook, o qual é definido no momento da criação do callback. 

Por exemplo:
```python
from assistant_fulfillment_helper import FulfillmentHelper

fh = FulfillmentHelper()

@fh.intent(webhook='pedidos', node='Novo pedido', token='{token}')
def cb_novo_pedido(args):
    """ Sua regra de negócio aqui """
    pass
```

Nesse exemplo, o "Novo pedido" no UI da Assistente deverá estar definido nas configurações do Fullfilment (webhook): ``http://meu-servidor.com.br/pedidos``.

### intent()
O decorator ``intent()`` definirá o callback pra cada intenção em uma lista de intenções dentro de um contexto de webhook. Será efetuado uma chamada para o método declarado como callback toda a vez que o servidor receber uma chamada vinda de um nó da Assistente para a intenção definida.
É possível registrar quantos callback de intenções e webhooks forem necessários, mas apenas um callback é permitido para cada intenção (nó).

**Parâmetros:**
| Parâmetro | Obrigatório? | Tipo | Descrição | 
|-----------|--------------|------|-----------|
| ``webhook`` | Sim | ``Str`` | Path do webhook, para o qual a Assistant requisitará nesse nó |
| ``token`` | Sim | ``Str`` | Token disponibilizado pela Assistente na configuração do Nó de Intenção |
| ``node`` | Sim | ``Str`` | Nome do Nó de Intenção cadastrado na Assistente |
| ``fallback_message`` | Não | ``Str`` | Mensagem padrão de retorno em caso de falha na execução do callback |

## Criando um callback
Na chamada do callback, será passado uma variável do tipo ``Dict`` com alguns argumentos que poderão ser utilizados na regra de negócio como quiser. 
Exemplo de um método para callback de um Nó de Intenção:
```python
from assistant_fulfillment_helper import FulfillmentHelper, FulfillmentHelperResponse

fh = FulfillmentHelper()

@fh.intent(webhook='pedidos', node='Novo pedido', token='{token}')
def cb_novo_pedido(params):
    session = params.get('sessionId')
    message = f"Olá Usuário, nosso id de sessão é: {session}"
    
    return FulfillmentHelperResponse(
        message = message
    )
```

Os parametros passados na chamada do callback são:

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| intent_name | ``Str`` | Nome do nó sendo processado |
| parameters | ``Dict`` | Todos os parametros desse contexto de conversa |
| sessionLog | ``List`` | Lista de ID de sessões até esse ponto da conversa |
| namedQueries | ``Dict`` | Resultados da Named Query (se houver) |
| query | ``Str`` | Query executada (se houver) |
| language | ``Str`` | Idioma da conversa |
| carolOrganization | ``Str`` | Nome da Organização |
| carolEnvironment | ``Str`` | Nome do Ambiente |
| carolOrganizationId | ``Str`` | Id da Organização |
| carolEnvironmentId | ``Str`` | Id do Ambiente |
| sessionId | ``Str`` | Id da sessão da conversa atual |
| isProduction | ``Bool`` | Informa se a convesa está acontecendo em Produção ou Desenvolvimento |
| channelName | ``Str`` | Nome do canal por onde a mensagem chegou |

### Retorno do Callback 
O metodo de callback deve retornar uma classe do tipo ``FulfillmentHelperResponse``, como no [exemplo acima](#criando-um-callback). Essa classe possui os seguintes atributos para retorno:

| Parâmetro | Obrigatório? | Tipo | Descrição | 
|-----------|--------------|------|-----------|
| ``message`` | Sim | ``Str`` | Mensagem que será retornada na conversa |
| ``short_message`` | Não | ``Str`` | Mensagem curta de retorno |
| ``jump_to`` | Não | ``Str`` | Nome do nó para o qual a conversa será direcionada |
| ``options`` | Não | ``List[Str]`` | Lista de opções pré-definidas que aparecerão como botões na resposta |
| ``logout`` | Não | ``Bool`` | Destrói a sessão de usuário na conversa ``(default: False)`` |
| ``parameters`` | Não | ``Dict`` | Parametros que serão adicionados no contexto da conversa |

Exemplo de uso:
```python
@fh.intent(webhook='boas-vindas', node='Boas vindas', token='{token}')
def callback_boas_vindas(params):
    message = f"Olá, o que deseja fazer agora?"
    
    return FulfillmentHelperResponse(
        message = message,
        short_message = "Boas vindas",
        jump_to = "Pedidos",
        options = [
            "Criar Pedido", 
            "Consultar Pedido",
            "Cancelar Pedido"
        ],
        logout = False,
        parameters = { 'onboarding' : True }
    )
```

### Falha do Callback 
Se por algum motivo houver uma excessão na execução do callback, o servidor responderá uma mensagem de fallback padrão para a assistente ("Desculpe, não consegui processar seu pedido no momento."). Essa mensagem pode ser alterada na definição da intenção. 

Por exemplo:
```python
@fh.intent(webhook='login', node='Login', token='{token}', fallback_message='Estamos passando por alguns problemas.')
def callback_login(params):
    resposta = 'lorem'*1/params # raises a TypeError Exception
    
    return FulfillmentHelperResponse(
        message = resposta
    )
```

Na execução desse callback, a excessão `TypeError` será capturada pelo servidor. O qual, por sua vez, retornará para o usuário na Assistente a mensagem de fallback definida para esse callback e o detalhes do erro será disponibilizado no console do servidor. 

## Iniciando um servidor local
Existem diferentes formas de executar o servidor webhook. A biblioteca disponibiliza o método ``start()`` para rodar o servidor diretamente pelo código e o método ``get_app_context()`` para poder executar externamente por outra biblioteca (ex: gunicorn) e executar testes.

### get_app_context()
O método ``get_app_context()`` retornará o contexto do servidor em uma variável, o que é util para executar testes e rodar a aplicação utilizando bibliotecas externas e deixar pronto para receber requisições como um Webhook.

Por exemplo:
```python
fh = FulfillmentHelper()

application = fh.get_app_context()
```

Agora a aplicação pode ser executada com o comando:
```sh
gunicorn my_app
```

> NOTA: nesse exemplo a variável ``application`` poderá ser utilizada por bibliotecas de testes também.

### start()
O método ``start()`` é responsável por iniciar um servidor e deixar pronto para receber requisições como um Webhook. Por esse método, o servidor pode ser configurado passando algumas propriedades no momento da chamada. 

Por exemplo:
```python
fh = FulfillmentHelper()

fh.start(
    debug = True
)
```

As configurações customizáveis para o servidor local são:

| Parâmetro | Obrigatório? | Tipo | Default | Descrição | 
|-----------|--------------|------|---------|-----------|
| ``debug`` | Não | ``Bool`` | ``False`` | O Debug ativo habilita verbosidade e reinicia o servidor em cada alteração de código |
| ``host`` | Não | ``Str`` | ``0.0.0.0`` | Nome ou IP do host local |
| ``port`` | Não | ``Int`` | ``5052`` | Porta do host local |


## Exceções 
Os possíveis erros são tratados pelas exceções da biblioteca. Aqui está a lista das exceções existentes:


| Exceção | Problema | 
|-----------|--------|
| ``DuplicatedIntentNodeException()`` |  Foi tentado adicionar dois métodos de callback para o mesmo Nó de Intenção |
| ``IntentCallbackNotFoundException()`` | O WebHook recebeu uma chamada para um Nó de Intenção indefinido |
| ``IntentResponseInstanceException()`` | O Callback invocado não retornou a classe de resposta esperada (``FulfillmentHelperResponse()``) |
| ``InvalidWebhookTokenException()`` | O WebHook token utilizado na chamada é diferente do token informado no registro do nó |
| ``WebhookNotFoundException()`` | O servidor recebeu uma requisição para um webhook indefinido |

## Executando em ambiente de DEV:
> Dica: Ao invocar o metodo ``start()``, [habilite o Debug](#iniciando-um-servidor-local) para um desenvolvimento mais rápido.

Ao iniciar o webhook local, será necessario disponibilizar a aplicação para fora da sua rede. Para isso recomendamos a utilização de algum software de proxy local, como, por exemplo, o [ngrok](https://ngrok.com/download). Após instalação, execute o comando abaixo em seu terminal para obter a URL pública da sua aplicação. Essa URL poderá ser adicionada como WebHook nas configurações dos seus nós na Assistente para um teste local.

```sh
ngrok http http://127.0.0.1:5052 
```
> NOTA: Informe o host e porta definida na inicialiazação do servidor WebHook.

## Executando com Gunicorn
É possivel executar o servidor do webhook utilizando [Gunicorn](https://gunicorn.org/), uma vez que o contexto da aplicação esteja acessível no arquivo de chamada raíz da sua aplicação. Há duas formas pra obter o contexto da aplicação no seu arquivo.

1. Utilizando o método `get_app_context()`:
```python
from assistant_fulfillment_helper import FulfillmentHelper

fh = FulfillmentHelper()
...

application = fh.get_app_context()
```

2. Importando a `application` (contexto da aplicação) diretamente:
```python
from assistant_fulfillment_helper import FulfillmentHelper, application

fh = FulfillmentHelper()
...
```

Agora é só iniciar o servidor com [Gunicorn](https://gunicorn.org/):
```
gunicorn -w 4 main
```

> NOTA: `main` deve ser o nome do arquivo raíz da sua aplicação, o qual possui o contexto do app acessível (`application`).

## Licença
MIT (LICENSE)
