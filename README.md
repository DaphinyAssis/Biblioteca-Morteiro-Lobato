# 📚 Biblioteca Morteiro Lobato  
Sistema de gerenciamento de empréstimos e devoluções de livros, disponível via **web** e com integração ao **balcão presencial**.  
<img width="1045" height="970" alt="image" src="https://github.com/user-attachments/assets/f1a584b9-24a7-495c-9255-e41e2d1502d2" />
---

## 🚀 Fluxo do Sistema  

### 🔹 Processo de Empréstimos (Web)  

#### 1. Autenticação  
- **Usuário já cadastrado** → Login com **CPF + senha**.  
- **Novo usuário** → Realiza cadastro informando os dados obrigatórios( cpf, nome completo, senha, endereço, telefone, comprovantes de endereço e documento).  
- O sistema valida as credenciais e libera o acesso.  

#### 2. Solicitação de Empréstimo  
- O usuário acessa o **catálogo digital** e visualiza apenas livros **com exemplares disponíveis**.  
- Seleciona o exemplar desejado e solicita o empréstimo.  
- Agenda a **data e horário de retirada presencial**.  
- O sistema registra o empréstimo como **pendente** (aguardando retirada).  

#### 3. Retirada no Balcão  
- O atendente confirma a identidade do usuário (**CPF/documento**).  
- O sistema altera o status do exemplar para **indisponível**.  
- O prazo de **7 dias para devolução** começa a contar a partir da retirada.  

#### 4. Confirmação  
O usuário recebe notificação/recibo digital contendo:  
- Detalhes do empréstimo.  
- Data prevista para devolução.  

---

### 🔹 Processo de Devoluções (Web + Presencial)  

#### 1. Entrega do Livro  
- O usuário devolve o exemplar no **balcão**. 

#### 2. Registro da Devolução  
- O atendente registra a devolução no sistema.  
- A data real de devolução é gravada.  

#### 3. Validação de Atrasos  
- O sistema compara a **data de devolução real** com a **prevista**.  
- Se houver atraso → gera **multa automática** vinculada à conta do usuário.  

#### 4. Atualização do Exemplar  
- O exemplar retorna ao status **disponível**.  

#### 5. Confirmação  
- O sistema confirma a devolução.  
- Caso haja multa, o usuário recebe **notificação imediata**.  

---

## 📌 Tecnologias (sugestão de implementação)  
- **Frontend**: HTML, CSS e Js.  
- **Backend**: Python.  
- **Banco de Dados**: SQLite.  
- **Autenticação**: JWT ou OAuth2.  
- **Notificações**: SMS.  

---

## ✅ Funcionalidades Principais  
- Cadastro e autenticação de usuários.  
- Catálogo digital com disponibilidade em tempo real.  
- Empréstimo com agendamento de retirada.  
- Controle de prazos e multas automáticas.  
- Registro de estado de conservação dos exemplares.  
- Notificações digitais para usuários.  

---

## 📄 Licença  
Este projeto está sob a licença **MIT** – livre para uso, modificação e distribuição.  
