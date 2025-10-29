# 🗂️ Ferramenta de Tratamento e Consolidação de Planilhas Bancárias

Esta aplicação Streamlit automatiza o processo de limpeza (mesclagem de linhas quebradas) e consolidação de múltiplas planilhas bancárias (arquivos Excel no formato XLSX), adicionando automaticamente o código do banco baseado no nome do arquivo.

## 🔗 Acesso Rápido

| Ambiente | Link |
| :--- | :--- |
| **Aplicação Online** | **[automatizar_dossie][https://automatizarjuncao.streamlit.app/]** |

## ✨ Funcionalidades

A aplicação está dividida em duas fases organizadas em abas, refletindo o fluxo de trabalho necessário:

1.  **🧹 Limpar Planilha Individual (Fase 1):**
      * Carrega arquivos XLSX no formato de extrato bancário.
      * **Corrige** automaticamente linhas que foram quebradas (por exemplo, quando o histórico ou fornecedor continuam na linha seguinte).
      * Filtra e padroniza as colunas de saída.
2.  **🧩 Consolidar Várias Planilhas (Fase 2):**
      * Une todos os arquivos tratados na Fase 1 em uma única planilha mestra.
      * Adiciona a coluna `Banco` com o código correspondente, utilizando um mapeamento definido no código (ex: `422-6` → `3313`).

## 🚀 Como Usar a Aplicação

Siga estas duas etapas simples para processar seus arquivos:

### Passo 1: Limpar os Arquivos (Aba "🧹 Limpar Planilha Individual")

1.  **Acesse a Aba:** Clique na primeira aba: **"🧹 Limpar Planilha Individual"**.
2.  **Selecione os Arquivos:** Clique em "Selecione as PLANILHAS ORIGINAIS para tratar" e escolha todos os seus arquivos XLSX originais.
3.  **Inicie:** Clique no botão **`▶️ Iniciar Tratamento de Todos os Arquivos`**.
4.  **Verifique:** O sistema irá processar cada arquivo individualmente, mesclando as linhas quebradas. Uma mensagem de sucesso (`✅`) confirmará que o arquivo foi tratado e está pronto para a próxima fase.

### Passo 2: Consolidar os Dados (Aba "🧩 Consolidar Várias Planilhas")

1.  **Acesse a Aba:** Clique na segunda aba: **"🧩 Consolidar Várias Planilhas"**.
2.  **Confirme:** A aba mostrará quantos arquivos tratados da Fase 1 estão prontos para a consolidação.
3.  **Consolide:** Clique no botão **`🚀 Consolidar e Gerar Arquivo Final`**.
4.  **Baixe:** Após o processamento, um novo DataFrame consolidado será exibido. Clique em **`📥 Baixar Planilha Consolidada`** para salvar o arquivo final (`Consolidado_Bancos.xlsx`) no seu computador.

-----

## 💻 Instalação e Execução Local (Para Desenvolvedores)

Se preferir rodar a aplicação localmente no seu computador, siga os passos abaixo:

### Pré-requisitos

Você precisará ter o Python instalado (versão 3.8 ou superior).

### 1\. Clonar o Repositório (ou Salvar o Arquivo)

Se estiver usando Git:

```bash
git clone [LINK DO SEU REPOSITÓRIO]
cd [NOME DO SEU REPOSITÓRIO]
```

Se você só tem o arquivo `app.py`, salve-o em um diretório vazio.

### 2\. Criar e Ativar o Ambiente Virtual

É uma boa prática usar um ambiente virtual:

```bash
# Cria o ambiente virtual
python3 -m venv .venv 

# Ativa o ambiente virtual (Linux/macOS)
source .venv/bin/activate

# Ativa o ambiente virtual (Windows PowerShell)
.venv\Scripts\Activate.ps1
```

### 3\. Instalar as Dependências

Instale as bibliotecas necessárias. Crie um arquivo `requirements.txt` com o seguinte conteúdo e use `pip install`:

**`requirements.txt`:**

```
streamlit
pandas
openpyxl
numpy
```

**Instalação:**

```bash
pip install -r requirements.txt
```

### 4\. Executar a Aplicação

Inicie a aplicação Streamlit:

```bash
streamlit run app.py
```

A aplicação abrirá automaticamente no seu navegador padrão.