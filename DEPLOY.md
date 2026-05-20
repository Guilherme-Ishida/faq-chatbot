# Guia de Deploy — Assistente Virtual UTFPR

---

## Requisitos do Servidor

- Python 3.11
- Mínimo de 1 GB de RAM
- Acesso à internet (necessário para baixar o modelo de embeddings na primeira execução e para chamadas à API do Groq)
- Porta 8080 liberada na rede interna (ou outra de preferência)

---

## 1. Clonar o Repositório

```bash
git clone <url-do-repositorio>
cd <nome-da-pasta>
```

---

## 2. Criar e Ativar o Ambiente Virtual

```bash
python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

---

## 3. Instalar as Dependências

```bash
pip install -r requirements.txt
```

> Na primeira execução, o modelo de embeddings `all-MiniLM-L6-v2` (~90 MB) será baixado automaticamente. O servidor precisa de acesso à internet nesse momento. Nas execuções seguintes o modelo é carregado do cache local.

---

## 4. Configurar as Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```
GROQ_API_KEY=sua_chave_aqui
PATH_DATA=data/
```

- `GROQ_API_KEY`: chave da API Groq — obtida em console.groq.com (plano gratuito disponível)
- `PATH_DATA`: caminho para a pasta onde estão os PDFs do FAQ

---

## 5. Indexar o FAQ

Rode o script de indexação para popular o banco vetorial com os pares de pergunta e resposta do PDF:

```bash
python store_index.py
```

O terminal deve exibir:
```
Pares Q&A extraídos: XX
Total indexado no ChromaDB: XX
```

> Este passo gera a pasta `chroma_db/` na raiz do projeto. Deve ser executado novamente sempre que o arquivo `FAQ.pdf` for atualizado.

---

## 6. Subir o Servidor em Produção

Para produção, utilize o **Gunicorn** no lugar do servidor de desenvolvimento do Flask, fazendo bind apenas no localhost:

```bash
pip install gunicorn
gunicorn -w 1 -b 127.0.0.1:8080 app:app
```

> Use `-w 1` (1 worker) para evitar conflitos com o modelo de embeddings carregado em memória.
> Nunca faça bind em `0.0.0.0` diretamente — use o Nginx como proxy reverso (veja seção abaixo).

---

### 6.1. Configurar Nginx como Proxy Reverso com HTTPS

Instale o Nginx e o Certbot (Let's Encrypt):

```bash
sudo apt install nginx certbot python3-certbot-nginx
```

Obtenha o certificado TLS:

```bash
sudo certbot --nginx -d seu-dominio.utfpr.edu.br
```

Crie o arquivo de configuração do Nginx:

```bash
sudo nano /etc/nginx/sites-available/assistente-utfpr
```

Cole o conteúdo abaixo (ajuste o domínio):

```nginx
server {
    listen 80;
    server_name seu-dominio.utfpr.edu.br;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name seu-dominio.utfpr.edu.br;

    ssl_certificate /etc/letsencrypt/live/seu-dominio.utfpr.edu.br/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seu-dominio.utfpr.edu.br/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Ative o site e reinicie o Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/assistente-utfpr /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

O sistema estará disponível em:
```
https://seu-dominio.utfpr.edu.br
```

---

## 7. Manter o Servidor Rodando (Linux)

Para manter o processo ativo mesmo após fechar o terminal, utilize o `systemd`.

Crie o arquivo de serviço:
```bash
sudo nano /etc/systemd/system/assistente-utfpr.service
```

Cole o conteúdo abaixo (ajuste os caminhos conforme necessário):
```ini
[Unit]
Description=Assistente Virtual UTFPR
After=network.target

[Service]
User=www-data
WorkingDirectory=/caminho/para/o/projeto
Environment="PATH=/caminho/para/o/projeto/venv/bin"
ExecStart=/caminho/para/o/projeto/venv/bin/gunicorn -w 1 -b 127.0.0.1:8080 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Ative e inicie o serviço:
```bash
sudo systemctl daemon-reload
sudo systemctl enable assistente-utfpr
sudo systemctl start assistente-utfpr
```

Verificar se está rodando:
```bash
sudo systemctl status assistente-utfpr
```

---

## 8. Atualizar o FAQ

Quando novas perguntas forem adicionadas ao PDF:

1. Substitua o arquivo `data/FAQ.pdf` pela versão atualizada (mantendo o padrão `PERGUNTA X:` / `RESPOSTA X:`)
2. Pare o servidor
3. Delete o banco vetorial antigo:
   ```bash
   # Linux/macOS
   rm -rf chroma_db/

   # Windows
   rmdir /s /q chroma_db
   ```
4. Reindexe:
   ```bash
   python store_index.py
   ```
5. Suba o servidor novamente

---

## Estrutura do Projeto

```
├── app.py                  # Servidor Flask (ponto de entrada)
├── store_index.py          # Script de indexação do FAQ
├── requirements.txt        # Dependências Python
├── .env                    # Variáveis de ambiente (não versionar)
├── data/
│   └── FAQ.pdf             # Arquivo de perguntas e respostas
├── chroma_db/              # Banco vetorial (gerado automaticamente)
├── src/
│   ├── helper.py           # Funções de carregamento e extração
│   └── prompt.py           # Prompt do assistente
└── templates/
    └── chat.html           # Interface web
```

---

## Observações

- O arquivo `.env` contém a chave da API e **não deve ser versionado** (já está no `.gitignore`)
- A chave da API Groq possui limite de **500.000 tokens/dia** no plano gratuito
- Em caso de dúvidas sobre o deploy, contate o responsável pelo desenvolvimento do sistema
