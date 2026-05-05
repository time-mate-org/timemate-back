# Timemate backend
<i> 🚀 FastAPI + Firebase + MySQL 🐍</i>
<br/>

## 📋 Requisitos Mínimos

✅ **Python 3.8+** (Não tem? [Baixe aqui](https://www.python.org/downloads/))  
✅ **MySQL Server** (Use XAMPP/WAMP ou Docker)  
✅ Conta no Firebase com projeto configurado

## 🛠️ Configuração do Projeto

### 1️⃣ Passo 1: Clone o repositório

```bash
git clone git@github.com:time-mate-org/timemate-back.git
cd timemate-back
```

### 2️⃣ Passo 2: Crie ambiente virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Passo 3: Instale dependências

```bash
pip install -r requirements.txt
```

### 4️⃣ Passo 4: Configure variáveis de ambiente

Exporte variáveis na pasta que ativou o ambiente:

```bash
export MYSQL_URI=conexãodobancolocal
```

Outras varíveis deverão ser exportar ao configurar o firebase no projeto, que também deverão estar no servidor de produção. Comunique a criação de qualquer variável de ambiente.

## ▶️ Como Executar

```bash
# Modo desenvolvimento (com reload automático)
fastapi dev
```

O sistema ira responder em `http://localhost:8000/`
Documentações(após rotas prontas) estarão em `http://localhost:8000/docs` e `http://localhost:8000/redoc`

## 🚨 Segurança Crítica!

⚠️ **Atenção:**

- ❌ Não versione `serviceAccountKey.json` ou `ca.pem`
- ❌ Sempre use `DEBUG=False` em produção
- ❌ Restrinja permissões do Firebase

## 🔄 Passo 5: Enviando suas mudanças (Windows)

### 🌟 Fluxo de Contribuição

Siga estas etapas para enviar suas alterações de forma organizada:

### 1️⃣ Crie uma branch de feature

```bash

# Verifique se está na branch main

git checkout main

# Atualize seu repositório local

git pull origin main

# Crie uma nova branch (ex: feature/calculadora)

git checkout -b feature/nome-da-sua-feature
```

### 2️⃣ Commit suas alterações

```bash

# Adicione todos os arquivos modificados

git add .

# Faça commit com mensagem descritiva

git commit -m "Adiciona: sua mensagem aqui (ex: implementa autenticação Firebase)"
```

### 3️⃣ Envie para o remoto

```bash

# Configure upstream (primeiro envio)

git push --set-upstream origin feature/nome-da-sua-feature

# Envios subsequentes

git push
```

### 4️⃣ Crie Pull Request (PR)

1. Acesse seu repositório no GitHub
2. Clique em **"Compare & pull request"**
3. Selecione:
   - Base: `main`
   - Compare: Sua branch
4. Descreva suas mudanças em detalhes
5. Clique em **"Create pull request"**

## ⚠️ Antes de Finalizar

✅ Verifique conflitos com a branch `main`  
✅ Descreva claramente sua implementação

## 🚨 Dica Windows

Use **Git Bash** para comandos mais complexos:

1. Instale via [Git for Windows](https://git-scm.com/download/win)
2. Clique com botão direito → **Git Bash Here**

## 📦 CI/CD

Após a aprovação e merge do pull-request com alterações, uma ação do Github Actions fará o doployment automático da aplicação e disponibilizará [aqui](https://timemate-back.onrender.com).

## Criando usuário com tenant_id no Firebase (processo manual)

### Pré-requisitos
- Acesso ao Firebase Console
- Aplicação rodando localmente
- Acesso ao bucket


### Passo a passo

**1. Crie um bucket com o nome do tenant, caso não exista**
 - Tudo junto, só minúsculas
 - Adicione uma foto para o logo, uma para o banner do blog e várias outras para a galeria


**2. Criar o usuário no Firebase Console**

Acesse **Firebase Console → Authentication → Users → Add User**.
Informe email e senha. Anote o **UID** gerado.


**3. Criar o Tenant no banco, caso não exista**

Diretamento no banco, verifique se seu `tenant` já existe. Se não, crie em `tenants` com os dados necessários.
Insira o caminho das imagens nos campos de blog_*, lembre-se que `blog_photos` é um campo json (ex: [`photo1.jpg', 'photo2.jpg'])
Anote o `id` gerado — será o `tenant_id`.


**4. Criar o usuário no banco**

Insira na tabela `users` com o `uid` e `tenant_id` corretos:

```sql
INSERT INTO users (uid, email, tenant_id, ...) 
VALUES ('UID_DO_FIREBASE', 'email@exemplo.com', 1, ...);
```

**5. Setar o custom claim**

Custom claims são automaticamente setados quando um usuário é encontrado com a prop `uid` igual ao do usuário do firebase. 

