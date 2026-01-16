from flask import Flask, request, jsonify
import llama_cpp
from knowledge_base import FACTS

app = Flask(__name__)
model = llama_cpp.Llama("llama-2-7b-chat.Q2_K.gguf")

def get_relevant_facts(query):
    query = query.lower()
    return [f["fact"] for f in FACTS if any(k in query for k in f["keywords"])]

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    prompt = data.get('prompt', '')
    sys_msg = data.get('sys_msg', '')

    facts = get_relevant_facts(prompt)
    if facts:
        sys_msg += f"\n\nUse these facts to answer:\n" + "\n".join(facts)

    full_prompt = f"<s>[INST] <<SYS>>{sys_msg}<</SYS>>{prompt} [/INST]"
    response = model(full_prompt, max_tokens=1000)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
