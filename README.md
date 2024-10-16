
# Análise de Movimento para Salto Unipodal

Este projeto foi desenvolvido para analisar dados de cinemática de salto unipodal usando arquivos de ângulos e marcadores de movimento. O script processa os dados, aplica filtragem e calcula várias métricas biomecânicas relacionadas ao salto, como a distância do salto, o tempo aéreo e as amplitudes articulares.

## Requisitos

Antes de executar o script, é necessário instalar os pacotes Python necessários.

### Instalação dos Pacotes

Execute o seguinte comando no diretório do projeto para instalar as dependências a partir do arquivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

Isso instalará as seguintes bibliotecas:
- `pandas`
- `numpy`
- `matplotlib`
- `scipy`

## Arquivos de Entrada

Os arquivos de entrada incluem:

- **Arquivo de Ângulos (.mot)**: Contém os dados de ângulos articulares (ex.: quadril, joelho, tornozelo).
- **Arquivo de Marcadores (.trc)**: Contém os dados de posições dos marcadores (ex.: ponta do pé, calcanhar).

### Fonte dos Arquivos

Esses arquivos devem ser baixados da plataforma **OpenCap**. Você pode acessar a plataforma aqui: [OpenCap](https://opencap.ai).

### Estrutura dos Arquivos

- **.mot**: Deve conter os ângulos articulares por frame, com dados a partir da linha 12.
- **.trc**: Deve conter as posições dos marcadores, com dados a partir da linha 7.

## Configuração dos Caminhos

No script, é necessário configurar os caminhos corretos para os arquivos baixados do OpenCap:

- `FILE_PATH_ANGLES`: Caminho para o arquivo `.mot` (ângulos articulares).
- `FILE_PATH_MARKER`: Caminho para o arquivo `.trc` (posições dos marcadores).

Certifique-se de ajustar essas variáveis para apontar para os locais corretos no seu sistema de arquivos.

## Como Usar

### Configurar Entradas

No script, configure as constantes de entrada para refletir o nome do paciente, a tentativa e a perna utilizada. As principais variáveis a serem ajustadas incluem:

- `NAME`: Nome do paciente.
- `TRIAL`: Número ou identificação do teste.
- `LEG`: Qual perna está sendo utilizada (opções: `'Direita'` ou `'Esquerda'`).
- `FILE_OUTPUT`: Caminho onde os arquivos de saída serão salvos.
- `FILE_PATH_ANGLES`, `FILE_NAME_ANGLES`: Caminho e nome do arquivo `.mot`.
- `FILE_PATH_MARKER`, `FILE_NAME_MARKER`: Caminho e nome do arquivo `.trc`.

### Executar o Script

Uma vez configuradas as entradas, você pode executar o script com o comando:

```bash
python salto_unipodal.py
```

### Saídas

O script gera dois tipos de saídas:

1. **Arquivo Excel** (`.xlsx`): Contém as seguintes métricas biomecânicas:
   - **Distância do salto**
   - **Tempo aéreo**
   - **Diferença máxima de altura pélvica**
   - **Amplitudes articulares** (pré e pós-salto)

2. **Gráfico** (`.png`): Um gráfico mostrando a posição vertical da ponta do pé e calcanhar ao longo do tempo, destacando momentos importantes como o **despregue** e o **retorno ao solo**.

Os arquivos de saída são salvos no diretório especificado por `FILE_OUTPUT`.

## Exemplo de Saídas

- **Arquivo Excel**: `Borba_Direita_Teste1_Resultados.xlsx`
- **Gráfico**: `Borba_Direita_Teste1_Grafico.png`

## Exemplo em Vídeo

[![Assista ao Vídeo](https://img.youtube.com/vi/-e--PE_sNUE/0.jpg)](https://youtube.com/shorts/pyeYdNVvqdg)

Clique na imagem acima para assistir ao vídeo.


## Contato

Desenvolvido por Edilson Borba  
E-mail: [borba.edi@gmail.com](mailto:borba.edi@gmail.com)
