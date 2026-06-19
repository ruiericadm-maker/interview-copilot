import os
import streamlit as st
import speech_recognition as sr
from dotenv import load_dotenv
from google import genai
from google.genai import types  # Importação crucial para os tipos de dados corretos

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Interview Copilot Pro V4",
    page_icon="⚡",
    layout="wide"
)

# Estilo CSS personalizado para a interface
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; }
    .question-box { 
        background-color: #1E1E24; 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 6px solid #FF4B4B; 
        margin-bottom: 15px; 
        color: #FFFFFF !important;
        font-size: 1.1rem;
    }
    .question-box b { color: #FF4B4B !important; }
    .error-box {
        background-color: #442222;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #FF4B4B;
        color: #FFDADA;
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Carrega as variáveis de ambiente e inicializa o cliente do Gemini
load_dotenv()
CHAVE_API = os.getenv("GEMINI_API_KEY")
cliente = genai.Client(api_key=CHAVE_API) if CHAVE_API else None

# Inicialização dos estados da sessão (Session State)
if "last_question" not in st.session_state:
    st.session_state.last_question = ""
if "last_response" not in st.session_state:
    st.session_state.last_response = "Aguardando a primeira pergunta..."

# PROMPT DO SISTEMA: Regras de negócio e perfil do Eric isolados
PROMPT_SISTEMA = """Você é um Copiloto de Entrevista Profissional. Seu dever absoluto é gerar uma resposta em formato Markdown estrito contendo exatamente DUAS seções estruturadas. Não ignore nenhuma seção e não pare de escrever até fechar os parênteses da tradução.

PERFIL DO CANDIDATO:
- Nome: Eric
- Experiência: 4.5 anos na major fintech company como Especialista, liderando projetos piloto e treinando equipes operacionais.
- Educação: Estudante de Análise e Desenvolvimento de Sistemas (ADS) na UNINTER. Conhecimentos práticos em SQL Server, Python, AWS e Java.

Você deve estruturar seu output exatamente com os dois títulos abaixo:

### TRADUÇÃO
[Traduza a pergunta do entrevistador para o português de forma direta]

### TECH AND FINTECH EXPERIENCE
[Escreva uma resposta em inglês com exatamente 3 frases completas usando o método STAR (Situation, Action, Result). Use vocabulário simples de nível elementar/intermediário. Conecte o problema com sua liderança na Stone Co., gestão de equipes ou análise de dados. Logo abaixo, adicione a tradução exata dessa resposta para o português entre parênteses]
"""

def chamar_gemini_via_texto(pergunta_entrevistador):
    """Função de backup para processar o texto digitado manualmente"""
    if not cliente:
        return "⚠️ Erro: GEMINI_API_KEY não configurada no arquivo .env."
    try:
        palavras = pergunta_entrevistador.split()
        pergunta_limpa = " ".join([v for i, v in enumerate(palavras) if i == 0 or v != palavras[i-1]])

        resposta = cliente.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"PERGUNTA DO ENTREVISTADOR: {pergunta_limpa}",
            config={
                'system_instruction': PROMPT_SISTEMA,
                'temperature': 0.2,
                'max_output_tokens': 1000
            }
        )
        return resposta.text
    except Exception as e:
        erro_msg = str(e)
        if "429" in erro_msg or "RESOURCE_EXHAUSTED" in erro_msg:
            return "🔴 **ERRO DE COTA (429):** Limite atingido. Aguarde 30 segundos e tente novamente."
        return f"Erro no processamento de texto: {erro_msg}"


# --- INTERFACE GRÁFICA (STREAMLIT) ---
st.title("🎤 Interview Copilot Otimizado")
st.caption("Arquitetura Blindada - Separação de Contexto por Instrução de Sistema.")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📡 Controle")
    
    if st.button("🎤 CAPTURAR AGORA", use_container_width=True, type="primary"):
        reconhecedor = sr.Recognizer()
        
        # Ajustes de sensibilidade para capturar frases completas sem cortes precoces
        reconhecedor.energy_threshold = 100  
        reconhecedor.dynamic_energy_threshold = False  
        reconhecedor.pause_threshold = 2.0  # Espera 2 segundos de silêncio para garantir o fim da pergunta
        reconhecedor.phrase_threshold = 0.3
        
        with st.spinner("🎧 Ouvindo o entrevistador..."):
            try:
                with sr.Microphone() as fonte:
                    reconhecedor.adjust_for_ambient_noise(fonte, duration=0.5)
                    audio = reconhecedor.listen(fonte, timeout=None, phrase_time_limit=25)
                
                with st.spinner("🧠 Processando áudio na velocidade máxima..."):
                    # Extrai os bytes do áudio diretamente da memória
                    dados_wav = audio.get_wav_data(convert_rate=16000, convert_width=2)
                    
                    # CORREÇÃO DA VALIDAÇÃO: Criando a estrutura estrita de Part que o Pydantic exige
                    audio_part = types.Part.from_bytes(
                        data=dados_wav,
                        mime_type="audio/wav"
                    )
                    
                    # Envia usando o objeto tipado correto
                    resposta = cliente.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[
                            audio_part,
                            "Ouça o áudio da pergunta do entrevistador, transcreva-a internamente e responda seguindo estritamente as instruções de formato do sistema."
                        ],
                        config={
                            'system_instruction': PROMPT_SISTEMA,
                            'temperature': 0.1,
                            'max_output_tokens': 1000
                        }
                    )
                    
                    st.session_state.last_question = "🎙️ Áudio capturado e enviado com sucesso!"
                    st.session_state.last_response = resposta.text
                    st.rerun()
                        
            except Exception as e:
                erro_msg = str(e)
                if "429" in erro_msg or "RESOURCE_EXHAUSTED" in erro_msg:
                    st.session_state.last_response = "🔴 **ERRO DE COTA (429):** Limite atingido. Tente novamente em instantes."
                    st.rerun()
                else:
                    st.error(f"❌ Erro no processamento: {erro_msg}")

    st.markdown("---")
    pergunta_manual = st.text_area("Backup Manual (Texto):", height=80)
    if st.button("🚀 ENVIAR TEXTO", use_container_width=True):
        if pergunta_manual:
            st.session_state.last_question = pergunta_manual
            st.session_state.last_response = chamar_gemini_via_texto(pergunta_manual)
            st.rerun()

with col2:
    st.subheader("💡 Respostas")
    
    if st.session_state.last_question:
        st.markdown(f'<div class="question-box"><b>Interviewer:</b><br><i>"{st.session_state.last_question}"</i></div>', unsafe_allow_html=True)
    
    if "429" in st.session_state.last_response or "RESOURCE_EXHAUSTED" in st.session_state.last_response or "ERRO DE COTA" in st.session_state.last_response:
        st.markdown(f'<div class="error-box">{st.session_state.last_response}</div>', unsafe_allow_html=True)
    else:
        with st.container():
            st.markdown(st.session_state.last_response)
    
    st.markdown("")
    if st.button("🗑️ Limpar"):
        st.session_state.last_question = ""
        st.session_state.last_response = "Aguardando a primeira pergunta..."
        st.rerun()