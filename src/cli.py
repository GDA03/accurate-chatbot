import os
import time
import sys
from dotenv import load_dotenv
from rag_pipeline import setup_rag_chain

load_dotenv()

def main():
    print("=" * 50)
    print("🤖 Chatbot RAG - Accurate Online (CLI Version)")
    print("=" * 50)
    
    print("\nMemuat database dan model, harap tunggu...")
    try:
        rag_chain = setup_rag_chain()
        print("✅ Berhasil memuat model dan database!")
    except Exception as e:
        print(f"❌ Gagal memuat RAG pipeline: {e}")
        print("Pastikan Anda sudah menjalankan 'python ingest.py' terlebih dahulu.")
        sys.exit(1)
        
    chat_history = []
    
    print("\nKetik 'exit' atau 'quit' untuk keluar.")
    print("-" * 50)
    
    while True:
        user_query = input("\nAnda: ")
        if user_query.lower() in ['exit', 'quit']:
            print("Sampai jumpa!")
            break
            
        if not user_query.strip():
            continue
            
        print("Bot: [Mencari referensi...]")
        
        try:
            start_time = time.time()
            response = rag_chain.invoke({
                "input": user_query,
                "chat_history": chat_history
            })
            end_time = time.time()
            
            answer = response.get("answer", "Maaf, saya tidak dapat merumuskan jawaban.")
            
            print(f"\nBot: {answer}")
            print(f"\n[⏱️ Latency: {end_time - start_time:.2f} detik]")
            
            from langchain_core.messages import HumanMessage, AIMessage
            chat_history.append(HumanMessage(content=user_query))
            chat_history.append(AIMessage(content=answer))
            
        except Exception as e:
            print(f"❌ Terjadi kesalahan: {e}")

if __name__ == "__main__":
    main()
