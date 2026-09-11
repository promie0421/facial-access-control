Facial Access Control



Este projeto nasceu a partir de uma ideia desenvolvida para o Jovens Cientistas Cariocas (JCC).



A proposta inicial era criar um projeto que unisse programação, reconhecimento facial e segurança em algo que pudesse sair do computador e, futuramente, se transformar em um protótipo físico funcional.



Foi a partir disso que surgiu a ideia deste sistema de controle de acesso: uma câmera identifica a pessoa que está tentando entrar, compara seu rosto com os usuários cadastrados e decide se o acesso deve ou não ser autorizado.



O projeto está sendo desenvolvido inicialmente como parte das atividades do JCC, começando pelo software e pelos testes realizados em notebook antes da construção e integração com o hardware.



Mas o JCC é apenas o ponto de partida do projeto.



Quando o período de desenvolvimento relacionado ao Jovens Cientistas Cariocas chegar ao fim, pretendo continuar trabalhando no sistema de forma independente, adicionando novas funcionalidades, melhorando o reconhecimento, realizando mais testes e, principalmente, avançando para a construção do protótipo físico.



Por isso, este repositório também serve para acompanhar a evolução do projeto ao longo do tempo.



O projeto ainda está em desenvolvimento.



&#x20;A ideia



O funcionamento que quero chegar é mais ou menos este:



`text

Pessoa se aproxima

&#x20;       ↓

Câmera captura o rosto

&#x20;       ↓

InsightFace detecta o rosto

&#x20;       ↓

ArcFace gera o embedding

&#x20;       ↓

Sistema compara com as pessoas cadastradas

&#x20;       ↓

&#x20;  ┌─────────────┐

&#x20;  │ Encontrou?  │

&#x20;  └──────┬──────┘

&#x20;       Sim│Não

&#x20;          │

&#x20;    Autoriza    Nega

&#x20;     acesso     acesso



Também pretendo adicionar autenticação por PIN de 6 dígitos como alternativa para quem não quiser ou não puder utilizar reconhecimento facial.



A parte física ainda não faz parte desta versão. Futuramente quero integrar o sistema com algo como ESP32/Raspberry Pi, relé e uma fechadura eletrônica.



\## O que já funciona



Até o momento consegui implementar e testar:



\* captura da webcam com OpenCV;

\* detecção facial em tempo real;

\* geração de embeddings faciais;

\* cadastro de uma pessoa usando múltiplas amostras do rosto;

\* armazenamento dos embeddings no SQLite;

\* reconhecimento facial 1:N;

\* rejeição de pessoas não cadastradas;

\* confirmação do reconhecimento por múltiplos frames;

\* registro de tentativas de acesso;

\* estrutura inicial da interface gráfica com Tkinter.



Nos primeiros testes, o sistema conseguiu reconhecer corretamente a pessoa cadastrada e rejeitar uma pessoa que não estava no banco.



Esses testes ainda são pequenos e não significam que o threshold atual esteja calibrado para uso real.



\## Tecnologias



O projeto está sendo desenvolvido em Python e atualmente utiliza:



\* Python 3.12

\* OpenCV

\* InsightFace

\* ONNX Runtime

\* NumPy

\* SQLite

\* Argon2

\* Tkinter



Para reconhecimento facial estou utilizando o pacote `buffalo\_l` do InsightFace, com detecção facial e embeddings ArcFace.



A inferência atualmente roda somente em CPU.



\## Como o reconhecimento funciona



Durante o cadastro são coletadas várias amostras do rosto da pessoa.



Para cada amostra, o InsightFace gera um embedding facial de 512 dimensões. Esses vetores são convertidos para `float32` e armazenados como BLOB no SQLite.



Durante o reconhecimento:



```text

Webcam

&#x20; ↓

Detecção facial

&#x20; ↓

Embedding do rosto

&#x20; ↓

Comparação por similaridade de cosseno

&#x20; ↓

Embeddings cadastrados

&#x20; ↓

Melhor correspondência

&#x20; ↓

AUTHORIZED\_FACE / UNKNOWN\_FACE

```



Atualmente o sistema utiliza a melhor similaridade encontrada entre as amostras cadastradas de cada usuário.



O threshold ainda é experimental e será calibrado com uma quantidade maior de testes.



\## Estrutura atual



```text

access-control/

│

├── app.py

├── config/

│   └── settings.py

│

├── modules/

│   ├── authentication.py

│   ├── camera.py

│   ├── database.py

│   ├── face\_detection.py

│   ├── face\_engine.py

│   ├── face\_recognition.py

│   ├── logs.py

│   └── registration.py

│

├── ui/

│   ├── main\_window.py

│   ├── registration\_screen.py

│   ├── users\_screen.py

│   ├── camera\_view\_screen.py

│   ├── recognition\_test\_screen.py

│   ├── logs\_screen.py

│   └── settings\_screen.py

│

├── teste\_camera.py

├── teste\_deteccao.py

├── teste\_cadastro.py

├── teste\_reconhecimento.py

├── requirements.txt

└── requirements-lock.txt

```



Os scripts `teste\_\*.py` estão sendo usados durante o desenvolvimento para validar cada parte separadamente antes de integrá-la à interface principal.



\## Executando o projeto



Crie um ambiente virtual:



```bash

python -m venv venv

```



No Windows:



```bash

venv\\Scripts\\activate

```



Instale as dependências:



```bash

pip install -r requirements.txt

```



E execute:



```bash

python app.py

```



Na primeira utilização do InsightFace pode ser necessário baixar os modelos utilizados pelo projeto.



\## Dados biométricos



O banco de dados local \*\*não é versionado neste repositório\*\*.



```text

database/\*.db

```



está incluído no `.gitignore`.



Isso é proposital, já que o banco pode conter embeddings faciais das pessoas cadastradas.



Fotos brutas dos usuários também não são armazenadas no banco.



\## Próximos passos



Ainda quero implementar:



\* integração das funcionalidades com a interface Tkinter;

\* tela de usuários cadastrados;

\* visualização da câmera dentro da interface;

\* tela de reconhecimento;

\* autenticação alternativa por PIN;

\* gerenciamento de usuários;

\* visualização dos logs;

\* configuração do threshold pela aplicação;

\* testes mais completos de falsos positivos e falsos negativos;

\* liveness/anti-spoofing;

\* integração com hardware;

\* acionamento de uma fechadura eletrônica.



\## Status



Em desenvolvimento



O sistema ainda é um protótipo e não deve ser considerado pronto para utilização em um ambiente real de segurança.



O desenvolvimento está sendo feito de forma incremental: cada parte é implementada e testada separadamente antes de ser integrada ao restante do sistema.



A primeira fase do projeto está ligada ao \*\*Jovens Cientistas Cariocas\*\*, mas o encerramento dessa atividade não representa o encerramento deste projeto. A intenção é continuar seu desenvolvimento posteriormente, expandindo tanto o software quanto a parte física do sistema.

## Limitações de segurança conhecidas

A versão atual do sistema realiza reconhecimento facial, mas ainda não possui um mecanismo completo de detecção de vivacidade (liveness detection).

Durante os testes, foi identificado que uma fotografia de uma pessoa cadastrada exibida na tela de um celular pode ser reconhecida pelo sistema. Isso ocorre porque o reconhecimento facial atual verifica a similaridade entre o rosto apresentado à câmera e os dados biométricos cadastrados, mas ainda não confirma se o rosto pertence a uma pessoa fisicamente presente diante da câmera.

Essa limitação é conhecida e está sendo tratada na próxima etapa do desenvolvimento.

### Próxima etapa: Anti-Spoofing

O projeto deverá adicionar uma camada de liveness/anti-spoofing separada do reconhecimento de identidade. Entre os testes e mecanismos planejados estão:

- detecção de sinais de presença real ao longo de vários frames;
- desafios aleatórios de interação;
- análise de movimentos e características faciais;
- testes contra fotografias exibidas em celulares;
- testes contra vídeos previamente gravados.

A autorização de acesso deverá ocorrer somente quando a identidade facial e a verificação de vivacidade forem aprovadas.

Por enquanto, esta versão deve ser considerada um protótipo experimental e não deve ser utilizada como único mecanismo de segurança para controle de acesso físico.


