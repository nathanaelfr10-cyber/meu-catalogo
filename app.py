import streamlit as st
import pandas as pd
from thefuzz import process
import google.generativeai as genai
from duckduckgo_search import DDGS

# O sistema vai pegar a chave da IA de forma segura nas configurações do site
CHAVE_DA_IA = st.secrets["GEMINI_API_KEY"]

genai.configure(api_key=CHAVE_DA_IA)
model = genai.GenerativeModel('gemini-2.0-flash
def buscar_imagem_online(termo_da_peca):
    try:
        with DDGS() as ddgs:
            resultados = [r for r in ddgs.images(termo_da_peca, max_results=1)]
            if resultados:
                return resultados[0]['image']
    except:
        pass
    return "https://via.placeholder.com/300?text=Imagem+Nao+Encontrada"

st.set_page_config(page_title="Catálogo Inteligente", layout="centered")
st.title("📦 Catálogo Inteligente com Busca Online")

st.markdown("---")
arquivo_postado = st.file_uploader("1️⃣ Anexe sua planilha Excel aqui (.xlsx)", type=["xlsx"])

if arquivo_postado:
    df = pd.read_excel(arquivo_postado)
    st.success("Planilha carregada com sucesso!")
    
    termo_busca = st.text_input("2️⃣ Digite o nome ou especificação da peça que procura:")
    
    if termo_busca:
        # Pega a coluna de descrições da planilha
        lista_descricoes = df['Descricao'].tolist()
        resultado_proximo, score = process.extractOne(termo_busca, lista_descricoes)
        dados_peca = df[df['Descricao'] == resultado_proximo].iloc[0]
        
        if score > 40: # Margem de aceitação da busca
            if score == 100:
                st.subheader(f"✅ Item Encontrado: {dados_peca['Descricao']}")
                if 'Codigo' in df.columns:
                    st.caption(f"Código Interno: {dados_peca['Codigo']}")
                
                with st.spinner("Buscando imagem na internet..."):
                    url_foto = buscar_imagem_online(resultado_proximo)
                st.image(url_foto, width=350)
                
            else:
                st.subheader("⚠️ Item exato não encontrado. Sugestão próxima:")
                st.markdown(f"**Item no estoque:** {resultado_proximo} *(Compatibilidade: {score}%)*")
                
                with st.spinner("Buscando imagem da peça sugerida..."):
                    url_foto = buscar_imagem_online(resultado_proximo)
                st.image(url_foto, width=350)
                
                with st.spinner("Analisando diferenças técnicas com IA..."):
                    prompt = (f"O usuário buscou por '{termo_busca}', mas não temos. "
                              f"O mais próximo no estoque é '{resultado_proximo}'. "
                              f"Explique de forma técnica, muito curta e direta (máximo 2 linhas), qual a provável "
                              f"diferença prática entre o que ele pediu e o que temos.")
                    resposta_ia = model.generate_content(prompt)
                
                st.info(f"**Por que não é igual?**\n{resposta_ia.text}")
        else:
            st.error("Nenhum item parecido foi encontrado na sua planilha.")
