# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import io
import numpy as np # Adicionando numpy de volta, embora não usado explicitamente nas funções de IO/Estrutura

st.set_page_config(
    page_title="Ferramenta de Planilhas",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CONSTANTES GLOBAIS ---
COLUNAS_DESEJADAS = [
    'Baixa', 'Emissão', 'Cheq/Doc', 'Natureza', 'Histórico', 'Histórico.1',
    'Centro de Responsabilidade', 'Fornecedor (CNPJ + Nome)', 'Débito'
]

mapeamento_bancos = {
    '422-6': '3313',
    '558-4': '3314'
    # Adicione novas correspondências aqui conforme necessário.
}


@st.cache_data
def to_excel_bytes(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Planilha')
    processed_data = output.getvalue()
    return processed_data


@st.cache_data
def tratar_planilha_individual(uploaded_file):
    """
    Função de Tratamento com retorno de dicionário para DEBUG em caso de falha.
    """
    nome_arquivo = uploaded_file.name
    
    # 1. TENTATIVA DE LEITURA
    try:
        df = pd.read_excel(io.BytesIO(uploaded_file.getvalue()),
                           header=6,
                           dtype={'Baixa': str},
                           engine='openpyxl')
    except Exception as e:
        return {'status': 'Leitura Falhou', 'erro': str(e)}

    # 2. VERIFICAÇÃO INICIAL E LIMPEZA
    if df.empty or len(df) < 2:
        return {'status': 'Vazio ou Curto', 'colunas': list(df.columns)}
    
    df = df.iloc[1:].reset_index(drop=True)

    # 3. VERIFICAÇÃO DE ESTRUTURA E MESCLAGEM
    try:
        # Tenta acessar as colunas pelos índices esperados
        col_baixa_real = df.columns[1]
        col_hist_1 = df.columns[9]
        col_hist_2 = df.columns[10]
        col_fornecedor = df.columns[13]
        colunas_para_mesclar = [col_hist_1, col_hist_2, col_fornecedor]
    except IndexError:
        # FALHA MAIS PROVÁVEL ACONTECE AQUI
        return {'status': 'IndexError (Mesclagem)', 'colunas_lidas': list(df.columns), 'total_colunas': len(df.columns)}

    # (RESTANTE DA LÓGICA DE TRATAMENTO)
    df_tratado = df.copy()
    last_valid_index = -1
    
    for index, row in df_tratado.iterrows():
        baixa_val = row[col_baixa_real]
        is_main_line = pd.notna(baixa_val) and bool(str(baixa_val).strip())

        if is_main_line:
            last_valid_index = index
        elif last_valid_index != -1:
            for col in colunas_para_mesclar:
                if pd.notna(row[col]):
                    texto_continuacao = str(row[col]).strip()
                    valor_atual = df_tratado.at[last_valid_index, col]
                    
                    if pd.isna(valor_atual):
                        df_tratado.at[last_valid_index, col] = texto_continuacao
                    else:
                        df_tratado.at[last_valid_index, col] = str(valor_atual) + ' ' + texto_continuacao

    df_filtrado = df_tratado.dropna(subset=[col_baixa_real]).reset_index(drop=True)

    # 4. SELEÇÃO FINAL
    try:
        # Tenta selecionar a coluna de Débito (índice 18)
        indices_das_colunas_corretas = [1, 2, 4, 5, 9, 10, 12, 13, 18]
        df_final = df_filtrado.iloc[:, indices_das_colunas_corretas].copy()
    except IndexError:
        # SEGUNDO PONTO DE FALHA PROVÁVEL (Se o índice 18 não existir)
        return {'status': 'IndexError (Seleção Final)', 'colunas_lidas': list(df_filtrado.columns), 'total_colunas': len(df_filtrado.columns)}


    df_final.columns = COLUNAS_DESEJADAS
    nome_sugerido = nome_arquivo.replace('.xlsx', '_tratada.xlsx')
    
    return df_final, nome_sugerido


def consolidar_planilhas_tratadas(lista_de_dicionarios):
    lista_com_banco = []
    
    if not lista_de_dicionarios:
        return None

    for item in lista_de_dicionarios:
        df_temp = item['df'].copy()               
        nome_arquivo = item['nome_sugerido']      
        codigo_final_banco = None

        for chave_busca, codigo_banco in mapeamento_bancos.items():
            if chave_busca in nome_arquivo:
                codigo_final_banco = codigo_banco
                break

        if codigo_final_banco is None:
            codigo_padrao = nome_arquivo.split(' ')[0].split('_')[0]
            st.info(f"ℹ️ Mapeamento não encontrado para **{nome_arquivo}**. Usando código padrão: **'{codigo_padrao}'**")
            codigo_final_banco = codigo_padrao
        
        df_temp['Banco'] = codigo_final_banco
        lista_com_banco.append(df_temp)

    df_consolidado = pd.concat(lista_com_banco, ignore_index=True)

    colunas_finais = COLUNAS_DESEJADAS + ['Banco']
    df_consolidado = df_consolidado.reindex(columns=colunas_finais)

    return df_consolidado

# --- INTERFACE STREAMLIT PRINCIPAL ---

st.title("🗂️ Ferramenta de Planilhas Bancárias Automatizada")
st.markdown("Use as abas abaixo para processar seus arquivos em duas etapas.")

tab1, tab2 = st.tabs(["🧹 Limpar Planilha Individual", "🧩 Consolidar Várias Planilhas"])

if 'dataframes_tratados' not in st.session_state:
    st.session_state.dataframes_tratados = []

with tab1:
    st.header("Fase 1: Limpar (Mesclar Linhas Quebradas)")
    st.markdown("""
        **Passo 1:** Selecione as planilhas originais (.xlsx). O script irá mesclar as linhas quebradas e padronizar as colunas.
        """)

    uploaded_files_fase1 = st.file_uploader(
        "**Selecione as PLANILHAS ORIGINAIS para tratar:**",
        type="xlsx",
        accept_multiple_files=True,
        key="uploader_fase1"
    )

    if uploaded_files_fase1:
        if st.button("▶️ Iniciar Tratamento de Todos os Arquivos", type="primary"):
            st.session_state.dataframes_tratados = [] 
            st.markdown("---")
            st.subheader("Resultados do Tratamento:")
            
            progress_bar = st.progress(0, text="Processando arquivos...")
            
            for i, uploaded_file in enumerate(uploaded_files_fase1):
                progress_bar.progress((i + 1) / len(uploaded_files_fase1), 
                                      text=f"Processando: {uploaded_file.name}")
                
                resultado = tratar_planilha_individual(uploaded_file)
                
                # --- LÓGICA DE TRATAMENTO DE RETORNO E DEBUG ---
                if isinstance(resultado, tuple):
                    # Sucesso: Retornou (df_tratado, nome_sugerido)
                    df_tratado, nome_sugerido = resultado
                    
                    st.session_state.dataframes_tratados.append({
                        'df': df_tratado,
                        'nome_original': uploaded_file.name,
                        'nome_sugerido': nome_sugerido
                    })
                    
                    st.success(f"✅ Arquivo **{uploaded_file.name}** tratado e pronto para consolidação. (Nome sugerido: `{nome_sugerido}`) ") 
                
                elif isinstance(resultado, dict):
                    # Falha: Retornou o dicionário de debug
                    st.error(f"❌ Falha no tratamento de: **{uploaded_file.name}**")
                    st.subheader(f"Detalhes do Erro em {uploaded_file.name}:")
                    
                    if 'total_colunas' in resultado:
                        # Erro de estrutura (IndexError)
                        st.error(f"Erro: Tentativa de acessar uma coluna que não existe no ponto: **{resultado['status']}**")
                        st.warning(f"O Streamlit (servidor) só encontrou **{resultado['total_colunas']}** colunas. O script precisa de pelo menos 19 (índice 18 + 1).")
                        st.code(f"Colunas Lidas Pelo Servidor:\n{resultado['colunas_lidas']}")
                        st.info("💡 **Ajuste Necessário:** Você precisa revisar os índices [1, 2, 4, 5, 9, 10, 12, 13, 18] no código, pois o servidor está lendo menos colunas do que o seu PC.")
                    elif 'erro' in resultado:
                        # Erro de Leitura (Exception na leitura inicial)
                        st.error(f"Erro de Leitura/I/O: {resultado['erro']}")
                        st.warning("Verifique se o arquivo está corrompido ou se o formato é estritamente XLSX.")
                
                else:
                    # Falha: Retorno None (Caso de Vazio ou Curto)
                    st.error(f"❌ Falha no tratamento de: **{uploaded_file.name}**. (Arquivo Vazio/Curto ou Formato Inválido)")

            progress_bar.empty()
            if st.session_state.dataframes_tratados:
                st.success(f"🎉 **{len(st.session_state.dataframes_tratados)}** arquivos tratados com sucesso e transferidos para a Fase 2.")
            else:
                 st.warning("Nenhum arquivo pôde ser tratado com sucesso.")
    else:
        st.info("Aguardando o upload dos arquivos originais.")

with tab2:
    st.header("Fase 2: Consolidar (Unir e Adicionar Código de Banco)")
    st.markdown("""
        **Passo 2:** Esta fase unirá todos os arquivos que foram tratados com sucesso na **Fase 1** e adicionará o código de banco baseado no nome do arquivo.
        """)
    
    if st.session_state.dataframes_tratados:
        num_arquivos = len(st.session_state.dataframes_tratados)
        st.success(f"✔️ **{num_arquivos}** planilhas tratadas prontas para consolidação.")
        
        nomes = [item['nome_sugerido'] for item in st.session_state.dataframes_tratados]
        st.caption("Arquivos a serem consolidados (pelo nome sugerido):")
        st.code('\n'.join(nomes))
        
        st.markdown("---")
        
        if st.button("🚀 Consolidar e Gerar Arquivo Final", key="btn_consolidar", type="primary"):
            with st.spinner("Consolidando e adicionando códigos de banco..."):
                df_consolidado = consolidar_planilhas_tratadas(st.session_state.dataframes_tratados)

            if df_consolidado is not None:
                st.subheader("Resultado Final Consolidado")
                st.dataframe(df_consolidado, use_container_width=True)

                st.download_button(
                    label="📥 Baixar Planilha Consolidada",
                    data=to_excel_bytes(df_consolidado),
                    file_name="Consolidado_Bancos.xlsx",
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    key='download_consolidado_final'
                )
                st.balloons()
                st.success("🥳 Consolidação concluída! Arquivo pronto para download.")
            else:
                st.error("❌ Falha na consolidação dos arquivos.")
    else:
        st.warning("Nenhuma planilha tratada encontrada. Por favor, complete a **Fase 1** na aba ao lado.")

st.markdown("---")
st.caption("Desenvolvido com Streamlit e Pandas.")