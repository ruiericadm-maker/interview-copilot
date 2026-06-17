import os
import speech_recognition as sr
from dotenv import load_dotenv
from google import genai

# 1. Carrega a chave de API do arquivo .env
load_dotenv()
CHAVE_API = os.getenv("GEMINI_API_KEY")

# 2. Inicializa o cliente do Gemini com o novo SDK
cliente = genai.Client(api_key=CHAVE_API)

def chamar_gemini(texto_pergunta):
    print("\n🧠 Otimizando respostas rápidas... Aguarde...")
    
    prompt = f"""
    Você é um Copiloto de Entrevistas de Emprego ultrarrápido.
    O candidato ouviu esta pergunta: "{texto_pergunta}"
    
    Seja extremamente conciso para garantir velocidade de geração. Devolva exatamente isto:

    ---
    ### 🎯 TRADUÇÃO DA PERGUNTA
    [Tradução curta aqui]

    ### 🚀 OPÇÃO 1: DIRECT & TECHNICAL (Em Inglês)
    "[Resposta em INGLÊS, máxima de 2 frases, focada em resultados]"
    *(Tradução: [Em português aqui])*

    ### ⚡ OPÇÃO 2: BEHAVIORAL & STORYTELLING (Em Inglês)
    "[Resposta em INGLÊS, máxima de 2 frases, focada em atitude/resolução de problemas]"
    *(Tradução: [Em português aqui])*
    ---
    
    Regra: As respostas em inglês devem ser fáceis de ler dinamicamente. Não use textos longos.
    """
    
    # 🛡️ SISTEMA DE REDE DE SEGURANÇA (FALLBACK)
    modelos_para_tentar = ['gemini-2.5-flash', 'gemini-1.5-flash']
    
    for modelo in modelos_para_tentar:
        try:
            resposta = cliente.models.generate_content(
                model=modelo,
                contents=prompt,
            )
            
            print(f"\n=================== COPILOTO AI ({modelo}) ===================")
            print(resposta.text)
            print("===================================================\n")
            return # Sai da função se der certo
            
        except Exception as e:
            print(f"⚠️ O modelo {modelo} falhou ou está instável. Tentando alternativa...")
            
    print("❌ Erro: Todos os modelos do Gemini falharam devido à alta demanda. Tente novamente em instantes.")
    
def escutar_microfone():
    reconhecedor = sr.Recognizer()
    reconhecedor.pause_threshold = 2.0
    
    with sr.Microphone() as fonte:
        print("\n[Ajustando o ruído de fundo... Faça silêncio por 1 segundo]")
        reconhecedor.adjust_for_ambient_noise(fonte, duration=1)
        
        print("\n🎤 Copiloto Inteligente Ativo! Simule uma pergunta de entrevista em inglês...")
        audio = reconhecedor.listen(fonte)
        
    try:
        print("🤖 Transcrevendo o áudio do entrevistador...")
        texto_transcrito = reconhecedor.recognize_google(audio, language="en-US")
        
        print(f"\n[Entrevistador disse]: {texto_transcrito}")
        
        # Envia a pergunta transcrita para o cérebro do Gemini
        chamar_gemini(texto_transcrito)
        
    except sr.UnknownValueError:
        print("❌ Não entendi o áudio. Tente falar mais perto do microfone.")
    except sr.RequestError as e:
        print(f"❌ Erro no serviço de transcrição: {e}")

if __name__ == "__main__":
    if not CHAVE_API:
        print("❌ Erro: A chave GEMINI_API_KEY não foi encontrada no arquivo .env!")
    else:
        escutar_microfone()