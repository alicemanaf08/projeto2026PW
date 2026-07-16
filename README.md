# Projeto 2026 PW

### Membros
 Alice Manaf

---

### Tema
Sistema de hotel / pousada.

---

### Objetivo
Um sistema desenvolvido para ajudar no cadastro e reservas de clientes no hotel ou pousada.

---

### Ferramentas
* Canva para prototipagem de telas
* Word para documentação
* Github para abrigagem de codigo e arquivos
* VScode studio para progamação de backend e interface
* Astha para desenhos de diagramas e fluxogramas
* MySQL workbench para desenvolvimento do banco de dados

---

### Funcionamento
O sistema contara com o seguinte funcionamento:

1. **Cadastro simples dos clientes e funcionarios, cada cadastrado sendo possibilitado e contendo um codigo unico para facilitar buscas, associações e conceder permissões**
 

2. **Informações sobre os andares e os quartos, cuje os quartos contenham as informações:**
   * Status (reservados e livres)
   * Descrição breve, criada por um funcionario
   * Numero do quarto

3. **Controle de Reservas:**
   * Atribuira a reserva a um codigo unico que corresponde ao cliente cadastrado, e a restrição de realiza-las somente mediante ao codigo do funcionario responsavel pela mesma.
  
4. **Consulta de quartos, clientes e funcionarios:**
   * Exibira informações sobre a existencia do cadastro de clientes e funcionaios, ou não.
   * Exibira informações e status dos quartos disponiveis.
  

---

*Projeto desenvolvido para a aula de Programação Web e Mobile.*

---

# Requisitos Sistema Hotel Shiva - interface do funcionario

**Requisitos Funcionais** 

   **Tela Inicial**

* RF01 – O sistema deve exibir, na tela inicial do funcionário, as opções: Consultar Reserva, Cadastrar Funcionário e Cadastrar Cliente.

     **Cadastro de Cliente**

* RF02 – O sistema deve permitir que qualquer funcionário inicie o cadastro de cliente mediante inserção do código de funcionário.

* RF03 – O sistema deve solicitar os seguintes dados do cliente: nome completo, CPF, data de nascimento, endereço, e-mail e telefone.

* RF04 – O sistema deve gerar automaticamente um código único e imutável para cada cliente cadastrado.

* RF05 – O sistema deve exibir uma tela de confirmação com todos os dados inseridos antes de finalizar o cadastro, permitindo ao funcionário editar as informações ou prosseguir.

* RF06 – Ao confirmar o cadastro do cliente, o sistema deve direcionar automaticamente para a tela de reserva ou informar se já existir um cliente com os mesmos dados cadastrado, e se sim exibir o código dele.


    **Cadastro de Funcionário**

* RF07 – O sistema deve permitir o cadastro de novo funcionário apenas mediante inserção de um código de gerente válido.

* RF08 – O sistema deve solicitar os seguintes dados do funcionário: nome completo, CPF, data de nascimento, endereço, cargo e telefone.

* RF09 – O sistema deve gerar automaticamente um código único e imutável para cada funcionário cadastrado, e informar se o funcionário com aqueles dados já existe exibindo seu código.

* RF10 – O sistema deve exibir uma tela de confirmação com os dados do funcionário antes de validar o cadastro, permitindo editar ou confirmar.


     **Reserva**

* RF11 – O sistema deve permitir realizar uma reserva mediante inserção do código do funcionário, código do cliente, número do quarto e data da reserva.

* RF12 – O sistema deve verificar a disponibilidade do quarto na data informada.

* RF13 – Caso o quarto esteja reservado na data, o sistema deve exibir a mensagem "Quarto reservado nessa data" com opção de voltar.

* RF14 – Caso o quarto esteja livre, o sistema deve exibir o valor da diária e permitir a confirmação da reserva.

* RF15 – Ao confirmar a reserva, o sistema deve exibir mensagem de sucesso e instruir o funcionário a realizar o pagamento no caixa.


     **Consultas**

* RF16 – O sistema deve permitir ao funcionário escolher entre buscar por Cliente, Funcionário ou consultar quartos.

*	RF17 – Na consulta de cliente, o sistema deve permitir busca por código ou nome do cliente.

* RF18 – Caso o cliente não seja encontrado, o sistema deve exibir "Cliente não encontrado" com opção de cadastrá-lo.

* RF19 – Caso o cliente exista, o sistema deve exibir seus dados (nome, código, CPF, data de nascimento, e-mail, telefone, endereço) com opções de editar, apagar ou fazer reserva.

* RF20 – Na consulta de quarto, o sistema deve permitir busca pelo número do quarto ou visualizar o mapa de andares.

* RF21 – no mapa de andares deve ser possivel escolher um andar para consultar os quartos existentes nele juntamente com suas informações.

* RF22- o sistema deve permitir a edição da descrição do quarto selecionado que quando escolhida: aparece uma caixa de texto para uma nova decrição, opções de cancelar ação e concluir edição; ou sua reserva, opção essa que direciona o usuário diretamente para a tela de reservar.

* RF23-  na pesquisa caso o quarto esteja livre, o sistema deve indicar "Quarto livre" com opção de fazer reserva.

* RF24 – Caso o quarto esteja reservado, o sistema deve exibir nome do cliente, código do cliente e data da reserva, com opções de editar ou apagar a reserva.



**Requisitos Não Funcionais**
* RNF01 – Usabilidade: A interface deve ser simples e intuitiva, permitindo que qualquer funcionário realize cadastros e consultas sem necessidade de treinamento extenso.

* RNF02 – Controle de acesso: O sistema deve restringir o cadastro de funcionários apenas a usuários que informem um código de gerente válido, e a cada reserva o sistema deve exigir código do cliente e do funcionário, numero do quarto e data da reserva.

*RNF03 – Integridade dos dados: Os códigos gerados para clientes e funcionários devem ser imutáveis após a criação.

* RNF04 – Desempenho: As operações de consulta (clientes, funcionários e quartos) devem retornar resultados em caso de existência e não existência, ou status no caso dos quartos.

* RNF05 – Consistência: O sistema não deve permitir duas reservas simultâneas para o mesmo quarto na mesma data.

* RNF06 – Auditabilidade: O sistema deve registrar (log) as ações de cadastro, edição, exclusão e reserva, associando-as ao código do funcionário responsável.

---
  
# Requisitos Sistema Hotel Shiva - interface do cliente

 **Requisitos Funcionais** 

   **Tela Inicial**

* RF01 – O sistema deve exibir, na tela inicial do funcionário, as opções: Consultar Reserva, Cadastrar Funcionário e Cadastrar Cliente.

     **Cadastro de Cliente**

* RF02 – O sistema deve permitir que qualquer funcionário inicie o cadastro de cliente mediante inserção do código de funcionário.

* RF03 – O sistema deve solicitar os seguintes dados do cliente: nome completo, CPF, data de nascimento, endereço, e-mail e telefone.

* RF04 – O sistema deve gerar automaticamente um código único e imutável para cada cliente cadastrado.

* RF05 – O sistema deve exibir uma tela de confirmação com todos os dados inseridos antes de finalizar o cadastro, permitindo ao funcionário editar as informações ou prosseguir.

* RF06 – Ao confirmar o cadastro do cliente, o sistema deve direcionar automaticamente para a tela de reserva ou informar se já existir um cliente com os mesmos dados cadastrado, e se sim exibir o código dele.


    **Cadastro de Funcionário**

* RF07 – O sistema deve permitir o cadastro de novo funcionário apenas mediante inserção de um código de gerente válido.

* RF08 – O sistema deve solicitar os seguintes dados do funcionário: nome completo, CPF, data de nascimento, endereço, cargo e telefone.

* RF09 – O sistema deve gerar automaticamente um código único e imutável para cada funcionário cadastrado, e informar se o funcionário com aqueles dados já existe exibindo seu código.

* RF10 – O sistema deve exibir uma tela de confirmação com os dados do funcionário antes de validar o cadastro, permitindo editar ou confirmar.


     **Reserva**

* RF11 – O sistema deve permitir realizar uma reserva mediante inserção do código do funcionário, código do cliente, número do quarto e data da reserva.

* RF12 – O sistema deve verificar a disponibilidade do quarto na data informada.

* RF13 – Caso o quarto esteja reservado na data, o sistema deve exibir a mensagem "Quarto reservado nessa data" com opção de voltar.

* RF14 – Caso o quarto esteja livre, o sistema deve exibir o valor da diária e permitir a confirmação da reserva.

* RF15 – Ao confirmar a reserva, o sistema deve exibir mensagem de sucesso e instruir o funcionário a realizar o pagamento no caixa.


     **Consultas**

* RF16 – O sistema deve permitir ao funcionário escolher entre buscar por Cliente, Funcionário ou consultar quartos.

*	RF17 – Na consulta de cliente, o sistema deve permitir busca por código ou nome do cliente.

* RF18 – Caso o cliente não seja encontrado, o sistema deve exibir "Cliente não encontrado" com opção de cadastrá-lo.

* RF19 – Caso o cliente exista, o sistema deve exibir seus dados (nome, código, CPF, data de nascimento, e-mail, telefone, endereço) com opções de editar, apagar ou fazer reserva.

* RF20 – Na consulta de quarto, o sistema deve permitir busca pelo número do quarto ou visualizar o mapa de andares.

* RF21 – no mapa de andares deve ser possivel escolher um andar para consultar os quartos existentes nele juntamente com suas informações.

* RF22- o sistema deve permitir a edição da descrição do quarto selecionado que quando escolhida: aparece uma caixa de texto para uma nova decrição, opções de cancelar ação e concluir edição; ou sua reserva, opção essa que direciona o usuário diretamente para a tela de reservar.

* RF23-  na pesquisa caso o quarto esteja livre, o sistema deve indicar "Quarto livre" com opção de fazer reserva.

* RF24 – Caso o quarto esteja reservado, o sistema deve exibir nome do cliente, código do cliente e data da reserva, com opções de editar ou apagar a reserva.


 **Requisitos Não Funcionais**

* RNF01 – Usabilidade: A interface deve ser simples e intuitiva, permitindo que qualquer funcionário realize cadastros e consultas sem necessidade de treinamento extenso.

* RNF02 – Controle de acesso: O sistema deve restringir o cadastro de funcionários apenas a usuários que informem um código de gerente válido, e a cada reserva o sistema deve exigir código do cliente e do funcionário, numero do quarto e data da reserva.

* RNF03 – Integridade dos dados: Os códigos gerados para clientes e funcionários devem ser imutáveis após a criação.

* RNF04 – Desempenho: As operações de consulta (clientes, funcionários e quartos) devem retornar resultados em caso de existência e não existência, ou status no caso dos quartos.

* RNF05 – Consistência: O sistema não deve permitir duas reservas simultâneas para o mesmo quarto na mesma data.

* RNF06 – Auditabilidade: O sistema deve registrar (log) as ações de cadastro, edição, exclusão e reserva, associando-as ao código do funcionário responsável.


