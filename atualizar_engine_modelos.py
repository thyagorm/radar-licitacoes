with open("services/edital_engine.py", "r", encoding="utf-8") as f:
    code = f.read()

# Substitui modelos antigos pelos modelos ativos da sua conta
code = code.replace(
    'modelos_candidatos = ["gemini-3.6-flash", "gemini-2.0-flash", "gemini-1.5-flash"]',
    'modelos_candidatos = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-3.6-flash"]'
)

with open("services/edital_engine.py", "w", encoding="utf-8") as f:
    f.write(code)

print("✅ services/edital_engine.py atualizado com os modelos suportados!")
