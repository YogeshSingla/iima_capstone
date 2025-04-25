import requests
import subprocess
import time

OLLAMA_URL = "http://localhost:11434"

def check_ollama_running():
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        return response.status_code == 200
    except:
        return False

def start_ollama_daemon():
    print("🚀 Starting Ollama in background...")
    try:
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)  # Give it time to start
        if check_ollama_running():
            print("✅ Ollama is now running.")
            return True
        else:
            print("❌ Failed to start Ollama.")
            return False
    except FileNotFoundError:
        print("❌ 'ollama' command not found. Is it installed?")
        return False

def list_local_models():
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags")
        response.raise_for_status()
        models = response.json().get('models', [])
        return [model['name'] for model in models]
    except Exception as e:
        print(f"⚠️ Error listing models: {e}")
        return []

def select_model(models):
    print("\n📦 Available local models:")
    for idx, model in enumerate(models):
        print(f"{idx + 1}. {model}")
    
    while True:
        try:
            choice = int(input("\n🔢 Select a model by number: "))
            if 1 <= choice <= len(models):
                return models[choice - 1]
            else:
                print("❌ Invalid selection. Try again.")
        except ValueError:
            print("❌ Please enter a number.")

def run_model(model):
    print(f"\n▶️ Running model: {model}")
    try:
        # Start the model in background (non-blocking)
        subprocess.Popen(["ollama", "run", model], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)  # Let it spin up
        return True
    except Exception as e:
        print(f"❌ Failed to run model: {e}")
        return False

def send_query(model, prompt):
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(f"{OLLAMA_URL}/api/generate", json=payload)
        response.raise_for_status()
        return response.json().get('response', '').strip()
    except Exception as e:
        print(f"❌ Error generating response: {e}")
        return None

def main():
    print("🧠 Ollama Local Query Tool (Offline Mode)\n")

    if not check_ollama_running():
        if not start_ollama_daemon():
            return

    models = list_local_models()
    if not models:
        print("❌ No models found. Pull one with `ollama pull <model>` before using this tool.")
        return

    model = select_model(models)

    if not run_model(model):
        print("⚠️ Could not start the model. Exiting.")
        return

    while True:
        prompt = input("\n📝 Enter your prompt (or 'exit' to quit):\n> ")
        if prompt.strip().lower() in ['exit', 'quit']:
            print("👋 Goodbye!")
            break

        response = send_query(model, prompt)
        if response:
            print(f"\n💬 Response:\n{response}")

if __name__ == "__main__":
    main()
