# Assistente Virtual UTFPR

Chatbot institucional baseado em FAQ para atendimento aos servidores da UTFPR.

---

## Como rodar localmente

**1. Criar e ativar o ambiente virtual**

> Requer [Anaconda](https://www.anaconda.com/download) ou Miniconda instalado.

```bash
conda create -n faq-chatbot python=3.11 -y
conda activate faq-chatbot
```

**2. Instalar as dependências**
```bash
pip install -r requirements.txt
```

**3. Configurar o `.env`**
```
GROQ_API_KEY=sua_chave_aqui -> se cadastra no groq e cria uma api key pra você
PATH_DATA=data/ -> aqui voce coloca o seu caminho até a pasta data ex: C:/Users/seu_usuário/.../data/
```

**4. Indexar o FAQ na pasta "data"** (rode uma vez, e sempre que atualizar o PDF)
```bash
python store_index.py
```

**5. Subir o servidor**
```bash
python app.py
```

Acesse em: `http://localhost:8080`

---

Para instruções de deploy em servidor, consulte o arquivo [DEPLOY.md](DEPLOY.md).
