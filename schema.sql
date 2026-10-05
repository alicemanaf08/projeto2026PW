CREATE TABLE IF NOT EXISTS andares(letra TEXT PRIMARY KEY, interditado INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS quartos(
  numero TEXT PRIMARY KEY, andar TEXT REFERENCES andares(letra), descricao TEXT,
  camas_casal INTEGER DEFAULT 0, camas_solteiro INTEGER DEFAULT 0, ar INTEGER DEFAULT 0,
  banheira INTEGER DEFAULT 0, valor_diaria REAL, interditado INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS clientes(
  codigo TEXT PRIMARY KEY, nome TEXT, cpf TEXT UNIQUE, nascimento TEXT,
  rua TEXT, bairro TEXT, numero TEXT, cidade TEXT, estado TEXT,
  email TEXT, telefone TEXT, senha_hash TEXT, relacionados TEXT DEFAULT '');
CREATE TABLE IF NOT EXISTS funcionarios(
  codigo TEXT PRIMARY KEY, nome TEXT, cpf TEXT UNIQUE, nascimento TEXT,
  rua TEXT, bairro TEXT, numero TEXT, cidade TEXT, estado TEXT,
  cargo TEXT, telefone TEXT, nivel TEXT DEFAULT 'funcionario');
CREATE TABLE IF NOT EXISTS reservas(
  id INTEGER PRIMARY KEY AUTOINCREMENT, cod_cliente TEXT, cod_funcionario TEXT,
  quarto TEXT REFERENCES quartos(numero), entrada TEXT, saida TEXT, valor REAL,
  status TEXT, expira_em TEXT, criada_em TEXT);
CREATE TABLE IF NOT EXISTS logs(
  id INTEGER PRIMARY KEY AUTOINCREMENT, quando TEXT, cod_funcionario TEXT,
  acao TEXT, detalhe TEXT);
