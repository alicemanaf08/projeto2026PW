"""Hotel Shiva - API (Flask + SQLite).
Site do cliente:  http://localhost:5000/
App do funcionário: http://localhost:5000/app
"""
import os, random, sqlite3, datetime as dt
from flask import Flask, request, jsonify, session, g, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "hotel.db")
app = Flask(__name__, static_folder="static", static_url_path="/static")
app.secret_key = "shiva-projeto-faculdade"
RECUPERACAO = {}  # email -> (codigo, expira)  (envio de e-mail simulado)


# ---------- banco ----------
def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def fechar(_):
    c = g.pop("db", None)
    if c: c.close()

def q(sql, a=()):  return [dict(r) for r in db().execute(sql, a).fetchall()]
def one(sql, a=()):
    r = db().execute(sql, a).fetchone()
    return dict(r) if r else None
def run(sql, a=()):
    c = db().execute(sql, a); db().commit(); return c.lastrowid

def init_db():
    con = sqlite3.connect(DB)
    con.executescript(open(os.path.join(BASE, "schema.sql"), encoding="utf-8").read())
    if not con.execute("select 1 from andares").fetchone():
        desc = ["Vista para a rua", "Vista para o jardim", "Varanda e cômoda de 3 gavetas", "Suíte ampla"]
        for i, L in enumerate("ABC"):
            con.execute("insert into andares(letra) values(?)", (L,))
            for n in range(1, 5):
                casal, solt = [(1, 0), (0, 2), (1, 1), (1, 0)][n - 1]
                con.execute("insert into quartos values(?,?,?,?,?,?,?,?,0)",
                            (f"{L}{n}", L, desc[n - 1], casal, solt, 1 if n != 2 else 0,
                             1 if n == 4 else 0, 180 + 60 * i + 25 * n))
        # único cadastro inicial: o gerente (necessário para cadastrar os primeiros funcionários)
        con.execute("insert into funcionarios values('GR001','Gerente','00000000000','1980-01-01','-','-','0','-','-','Gerente','00000000000','gerente')")
        con.commit()
    con.close()


# ---------- utilidades ----------
def err(msg, code=400, **k): return jsonify(erro=msg, **k), code
def ok(**k): return jsonify(ok=True, **k)
def agora(): return dt.datetime.now().isoformat(timespec="seconds")
def hoje(): return dt.date.today()
def d_(s): return dt.date.fromisoformat(s)

def log(acao, detalhe, cod=None):
    run("insert into logs(quando,cod_funcionario,acao,detalhe) values(?,?,?,?)", (agora(), cod, acao, detalhe))

CODIGOS = {"clientes": ("CL", 5), "funcionarios": ("FN", 4)}  # prefixo e quantidade de números

def cod_(v): return str(v or "").strip().upper()

def gerar_codigo(tabela):
    p, n = CODIGOS[tabela]
    while True:
        c = f"{p}{random.randint(0, 10 ** n - 1):0{n}d}"
        if not one(f"select 1 from {tabela} where codigo=?", (c,)): return c

def codigo_valido(tabela, c):
    p, n = CODIGOS[tabela]
    return len(c) == len(p) + n and c.startswith(p) and c[len(p):].isdigit()

def limpar(v): return (v or "").strip() if isinstance(v, str) else v

def validar_pessoa(d, tipo):
    """Valida e normaliza os dados de cliente/funcionário. Retorna (dados, erro)."""
    campos = ["nome", "cpf", "nascimento", "rua", "bairro", "numero", "cidade", "estado", "telefone"]
    campos += ["email"] if tipo == "cliente" else ["cargo"]
    o = {c: str(limpar(d.get(c, "")) or "") for c in campos}
    if any(not v for v in o.values()): return None, "Preencha todos os campos."
    if len(o["nome"]) > 200: return None, "Nome com até 200 caracteres."
    if not (o["cpf"].isdigit() and len(o["cpf"]) == 11): return None, "CPF deve ter 11 números."
    if not (o["telefone"].isdigit() and len(o["telefone"]) == 11): return None, "Telefone deve ter 11 números (com DDD)."
    if not (o["numero"].isdigit() and len(o["numero"]) <= 6): return None, "Número do endereço: até 6 dígitos."
    try: d_(o["nascimento"])
    except ValueError: return None, "Data de nascimento inválida."
    if tipo == "cliente" and "@" not in o["email"]: return None, "E-mail inválido."
    if tipo == "cliente" and "relacionados" in d: o["relacionados"] = str(limpar(d["relacionados"]) or "")
    return o, None

def validar_senha(s):
    s = str(s or "")
    return None if (s.isdigit() and 1 <= len(s) <= 8) else "A senha deve ter de 1 a 8 números."

def cliente_out(c):
    c = dict(c); c["tem_senha"] = bool(c.pop("senha_hash", None)); return c

def inserir(tabela, o, codigo, extra=None):
    o = {**o, **(extra or {}), "codigo": codigo}
    run(f"insert into {tabela}({','.join(o)}) values({','.join('?' * len(o))})", list(o.values()))

def atualizar(tabela, codigo, o):
    run(f"update {tabela} set {','.join(k + '=?' for k in o)} where codigo=?", list(o.values()) + [codigo])

def auth(gerente=False):
    """Funcionário identificado pelo cabeçalho X-Codigo. Retorna (func, erro)."""
    f = one("select * from funcionarios where codigo=?", (cod_(request.headers.get("X-Codigo")),))
    if not f: return None, err("Código de funcionário inválido.", 403)
    if gerente and f["nivel"] != "gerente": return None, err("Ação restrita ao gerente: informe um código de gerente.", 403)
    return f, None

def cliente_logado():
    return one("select * from clientes where codigo=?", (session.get("cliente"),)) if session.get("cliente") else None


# ---------- quartos / reservas ----------
def limpar_expiradas():
    run("update reservas set status='cancelada' where status='pendente' and expira_em<?", (agora(),))

def ocupado(numero, e, s, ignorar=0):
    limpar_expiradas()
    return one("select id from reservas where quarto=? and status!='cancelada' and entrada<? and saida>? and id!=?",
               (numero, s, e, ignorar)) is not None

def status_quarto(qt, dia=None):
    limpar_expiradas()
    dia = (dia or hoje()).isoformat()
    if qt["interditado"]: return "interditado"
    r = one("select 1 from reservas where quarto=? and status!='cancelada' and entrada<=? and saida>?", (qt["numero"], dia, dia))
    return "reservado" if r else "livre"

def quarto_out(qt):
    qt = dict(qt); qt["status"] = status_quarto(qt); return qt

def checar(numero, entrada, saida, ignorar=0):
    """Retorna (erro, livre, valor)."""
    qt = one("select * from quartos where numero=?", (str(numero).upper(),))
    if not qt: return "Quarto não encontrado.", None, None
    try: e, s = d_(entrada), d_(saida)
    except (ValueError, TypeError): return "Informe as datas de entrada e saída.", None, None
    if e < hoje(): return "A entrada não pode ser no passado.", None, None
    if s <= e: return "A saída deve ser depois da entrada.", None, None
    if qt["interditado"] or ocupado(qt["numero"], entrada, saida, ignorar): return None, False, 0
    return None, True, qt["valor_diaria"] * (s - e).days

def criar_reserva(cod_cliente, cod_func, numero, entrada, saida, status):
    e, livre, valor = checar(numero, entrada, saida)
    if e: return None, err(e)
    if not livre: return None, err("Quarto reservado nessa data.", 409)
    exp = (dt.datetime.now() + dt.timedelta(minutes=5)).isoformat(timespec="seconds") if status == "pendente" else None
    rid = run("insert into reservas(cod_cliente,cod_funcionario,quarto,entrada,saida,valor,status,expira_em,criada_em) values(?,?,?,?,?,?,?,?,?)",
              (cod_cliente, cod_func, str(numero).upper(), entrada, saida, valor, status, exp, agora()))
    return one("select * from reservas where id=?", (rid,)), None


# ---------- páginas ----------
@app.route("/")
def site(): return send_from_directory("static/site", "index.html")
@app.route("/app")
def app_funcionario(): return send_from_directory("static/app", "index.html")


# ---------- público: andares e quartos ----------
@app.get("/api/andares")
def andares():
    out = []
    for a in q("select * from andares order by letra"):
        qs = q("select * from quartos where andar=?", (a["letra"],))
        st = [status_quarto(x) for x in qs]
        s = "interditado" if a["interditado"] else ("todo reservado" if st and all(x != "livre" for x in st) else "livre")
        out.append({"letra": a["letra"], "status": s, "quartos": len(qs)})
    return jsonify(out)

@app.get("/api/andares/<letra>/quartos")
def quartos_andar(letra):
    return jsonify([quarto_out(x) for x in q("select * from quartos where andar=? order by numero", (letra.upper(),))])

@app.get("/api/quartos/<numero>")
def quarto(numero):
    qt = one("select * from quartos where numero=?", (numero.upper(),))
    return jsonify(quarto_out(qt)) if qt else err("Quarto não encontrado.", 404)

@app.post("/api/quartos/<numero>/disponibilidade")
def disponibilidade(numero):
    d = request.json or {}
    e, livre, valor = checar(numero, d.get("entrada"), d.get("saida"))
    return err(e) if e else jsonify(livre=livre, valor=valor)


# ---------- cliente (site) ----------
@app.post("/api/cliente/cadastro")
def cliente_cadastro():
    d = request.json or {}
    o, e = validar_pessoa(d, "cliente")
    e = e or validar_senha(d.get("senha"))
    if e: return err(e)
    if one("select 1 from clientes where cpf=?", (o["cpf"],)): return err("Já existe cliente com esse CPF.", 409)
    cod = gerar_codigo("clientes")
    inserir("clientes", o, cod, {"senha_hash": generate_password_hash(str(d["senha"]))})
    session["cliente"] = cod
    return ok(codigo=cod)

@app.post("/api/cliente/login")
def cliente_login():
    d = request.json or {}
    c = one("select * from clientes where codigo=?", (cod_(d.get("codigo")),))
    if not c: return err("Não achamos seu login.", 404, naoEncontrado=True)
    if not c["senha_hash"] or not check_password_hash(c["senha_hash"], str(d.get("senha", ""))):
        return err("Senha incorreta.", 401)
    session["cliente"] = c["codigo"]
    return ok(cliente=cliente_out(c))

@app.post("/api/cliente/logout")
def cliente_logout(): session.pop("cliente", None); return ok()

@app.route("/api/cliente/me", methods=["GET", "PUT"])
def cliente_me():
    c = cliente_logado()
    if not c: return err("Faça login.", 401)
    if request.method == "GET": return jsonify(cliente_out(c))
    d = request.json or {}
    o, e = validar_pessoa(d, "cliente")
    if e: return err(e)
    if one("select 1 from clientes where cpf=? and codigo!=?", (o["cpf"], c["codigo"])): return err("CPF já usado por outro cliente.", 409)
    o.pop("relacionados", None)
    if d.get("senha"):
        e = validar_senha(d["senha"])
        if e: return err(e)
        o["senha_hash"] = generate_password_hash(str(d["senha"]))
    atualizar("clientes", c["codigo"], o)  # o código do cliente nunca é alterado
    return ok(cliente=cliente_out(one("select * from clientes where codigo=?", (c["codigo"],))))

@app.post("/api/senha/email")
def senha_email():
    email = limpar((request.json or {}).get("email"))
    if not one("select 1 from clientes where email=?", (email,)): return err("E-mail não cadastrado.", 404)
    cod = f"{random.randint(0, 999999):06d}"
    RECUPERACAO[email] = (cod, dt.datetime.now() + dt.timedelta(minutes=15))
    print(f"[E-MAIL SIMULADO] código de recuperação para {email}: {cod}")
    return ok(codigo_demo=cod)  # sem servidor de e-mail: o código é devolvido para a demonstração

def _codigo_ok(email, cod):
    r = RECUPERACAO.get(email)
    return bool(r and r[0] == str(cod) and r[1] > dt.datetime.now())

@app.post("/api/senha/codigo")
def senha_codigo():
    d = request.json or {}
    return ok() if _codigo_ok(d.get("email"), d.get("codigo")) else err("Código inválido ou expirado.")

@app.post("/api/senha/nova")
def senha_nova():
    d = request.json or {}
    if not _codigo_ok(d.get("email"), d.get("codigo")): return err("Código inválido ou expirado.")
    e = validar_senha(d.get("senha"))
    if e: return err(e)
    run("update clientes set senha_hash=? where email=?", (generate_password_hash(str(d["senha"])), d["email"]))
    RECUPERACAO.pop(d["email"], None)
    return ok()

@app.route("/api/cliente/reservas", methods=["GET", "POST"])
def cliente_reservas():
    c = cliente_logado()
    if not c: return err("Faça login.", 401)
    if request.method == "POST":
        d = request.json or {}
        r, e = criar_reserva(c["codigo"], None, d.get("quarto"), d.get("entrada"), d.get("saida"), "pendente")
        if e: return e
        log("reserva", f"cliente {c['codigo']} reservou {r['quarto']} ({r['entrada']} a {r['saida']})")
        return ok(reserva=r)
    limpar_expiradas()
    return jsonify(q("select * from reservas where cod_cliente=? and status!='cancelada' order by entrada", (c["codigo"],)))

@app.post("/api/cliente/reservas/<int:rid>/pagar")
def cliente_pagar(rid):
    c = cliente_logado()
    if not c: return err("Faça login.", 401)
    limpar_expiradas()
    r = one("select * from reservas where id=? and cod_cliente=?", (rid, c["codigo"]))
    if not r or r["status"] != "pendente": return err("Reserva expirada ou já paga.", 409)
    run("update reservas set status='paga', expira_em=NULL where id=?", (rid,))
    log("pagamento", f"reserva {rid} paga via {(request.json or {}).get('forma', '?')}")
    return ok()

@app.delete("/api/cliente/reservas/<int:rid>")
def cliente_cancelar(rid):
    c = cliente_logado()
    if not c: return err("Faça login.", 401)
    if not one("select 1 from reservas where id=? and cod_cliente=?", (rid, c["codigo"])): return err("Reserva não encontrada.", 404)
    run("update reservas set status='cancelada' where id=?", (rid,))
    log("exclusão", f"cliente {c['codigo']} cancelou a reserva {rid}")
    return ok()


# ---------- funcionário (app) ----------
@app.post("/api/func/validar")
def func_validar():
    f, e = auth((request.json or {}).get("gerente", False))
    return e or ok(nome=f["nome"], nivel=f["nivel"])

def _busca(tabela, termo):
    termo = (termo or "").strip()
    if not termo: return []
    if one(f"select 1 from {tabela} where codigo=?", (cod_(termo),)):
        return q(f"select * from {tabela} where codigo=?", (cod_(termo),))
    return q(f"select * from {tabela} where nome like ? order by nome", (f"%{termo}%",))

def _preview(tabela, tipo):
    f, e = auth(tipo == "funcionario")
    if e: return e
    o, e = validar_pessoa(request.json or {}, tipo)
    if e: return err(e)
    ex = one(f"select codigo from {tabela} where cpf=?", (o["cpf"],))
    return jsonify(existe=True, codigo=ex["codigo"]) if ex else jsonify(existe=False, codigo=gerar_codigo(tabela))

def _criar(tabela, tipo):
    f, e = auth(tipo == "funcionario")
    if e: return e
    d = request.json or {}
    o, e = validar_pessoa(d, tipo)
    if e: return err(e)
    if one(f"select 1 from {tabela} where cpf=?", (o["cpf"],)): return err("Cadastro já existe.", 409)
    pedido = cod_(d.get("codigo"))
    ok_pedido = codigo_valido(tabela, pedido) and not one(f"select 1 from {tabela} where codigo=?", (pedido,))
    cod = pedido if ok_pedido else gerar_codigo(tabela)
    inserir(tabela, o, cod)
    log("cadastro", f"{tipo} {cod}", f["codigo"])
    return ok(codigo=cod)

def _editar(tabela, tipo, cod):
    cod = cod_(cod)
    f, e = auth(tipo == "funcionario")
    if e: return e
    o, e = validar_pessoa(request.json or {}, tipo)
    if e: return err(e)
    if not one(f"select 1 from {tabela} where codigo=?", (cod,)): return err("Não encontrado.", 404)
    if one(f"select 1 from {tabela} where cpf=? and codigo!=?", (o["cpf"], cod)): return err("CPF já usado por outro cadastro.", 409)
    atualizar(tabela, cod, o)  # código nunca muda
    log("edição", f"{tipo} {cod}", f["codigo"])
    return ok()

@app.post("/api/func/clientes/preview")
def cli_preview(): return _preview("clientes", "cliente")
@app.post("/api/func/clientes")
def cli_criar(): return _criar("clientes", "cliente")
@app.get("/api/func/clientes")
def cli_busca():  # consulta livre: não exige código de funcionário
    return jsonify([cliente_out(c) for c in _busca("clientes", request.args.get("q"))])
@app.put("/api/func/clientes/<cod>")
def cli_editar(cod): return _editar("clientes", "cliente", cod)
@app.delete("/api/func/clientes/<cod>")
def cli_apagar(cod):
    f, e = auth(True)
    if e: return e
    cod = cod_(cod)
    run("update reservas set status='cancelada' where cod_cliente=?", (cod,))
    run("delete from clientes where codigo=?", (cod,))
    log("exclusão", f"cliente {cod}", f["codigo"])
    return ok()

@app.post("/api/func/funcionarios/preview")
def fun_preview(): return _preview("funcionarios", "funcionario")
@app.post("/api/func/funcionarios")
def fun_criar(): return _criar("funcionarios", "funcionario")
@app.get("/api/func/funcionarios")
def fun_busca():  # consulta livre: não exige código de funcionário
    return jsonify(_busca("funcionarios", request.args.get("q")))
@app.put("/api/func/funcionarios/<cod>")
def fun_editar(cod): return _editar("funcionarios", "funcionario", cod)
@app.delete("/api/func/funcionarios/<cod>")
def fun_apagar(cod):
    f, e = auth(True)
    if e: return e
    cod = cod_(cod)
    if f["codigo"] == cod: return err("Você não pode apagar o próprio cadastro.")
    run("delete from funcionarios where codigo=?", (cod,))
    log("exclusão", f"funcionário {cod}", f["codigo"])
    return ok()

@app.route("/api/func/quartos/<numero>", methods=["GET", "PUT"])
def func_quarto(numero):
    f = None
    if request.method == "PUT":  # editar exige funcionário; consultar (GET) é livre
        f, e = auth()
        if e: return e
    qt = one("select * from quartos where numero=?", (numero.upper(),))
    if not qt: return err("Quarto não encontrado.", 404)
    if request.method == "PUT":
        d = request.json or {}
        desc = (d.get("descricao") or qt["descricao"]).strip()
        if len(desc) > 200: return err("Descrição com até 200 caracteres.")
        run("update quartos set descricao=?, interditado=? where numero=?", (desc, int(d.get("interditado", qt["interditado"])), qt["numero"]))
        log("edição", f"quarto {qt['numero']}", f["codigo"])
        return ok()
    st = status_quarto(qt)
    rs = q("""select r.*, c.nome as nome_cliente from reservas r left join clientes c on c.codigo=r.cod_cliente
              where r.quarto=? and r.status!='cancelada' and r.saida>? order by r.entrada""", (qt["numero"], hoje().isoformat()))
    atual = next((r for r in rs if r["entrada"] <= hoje().isoformat()), None) if st == "reservado" else None
    return jsonify(quarto={**qt, "status": st}, reserva=atual, futuras=[r for r in rs if r is not atual])

@app.post("/api/func/reservas/verificar")
def res_verificar():
    f, e = auth()
    if e: return e
    d = request.json or {}
    if not one("select 1 from clientes where codigo=?", (cod_(d.get("cod_cliente")),)): return err("Cliente não encontrado.", 404)
    e, livre, valor = checar(d.get("quarto"), d.get("entrada"), d.get("saida"))
    return err(e) if e else jsonify(livre=livre, valor=valor)

@app.post("/api/func/reservas")
def res_criar():
    f, e = auth()
    if e: return e
    d = request.json or {}
    if not one("select 1 from clientes where codigo=?", (cod_(d.get("cod_cliente")),)): return err("Cliente não encontrado.", 404)
    r, e = criar_reserva(cod_(d.get("cod_cliente")), f["codigo"], d.get("quarto"), d.get("entrada"), d.get("saida"), "confirmada")
    if e: return e
    log("reserva", f"reserva {r['id']} quarto {r['quarto']} cliente {r['cod_cliente']}", f["codigo"])
    return ok(reserva=r)

@app.put("/api/func/reservas/<int:rid>")
def res_editar(rid):
    f, e = auth()
    if e: return e
    r = one("select * from reservas where id=? and status!='cancelada'", (rid,))
    if not r: return err("Reserva não encontrada.", 404)
    d = request.json or {}
    e, livre, valor = checar(r["quarto"], d.get("entrada"), d.get("saida"), ignorar=rid)
    if e: return err(e)
    if not livre: return err("Quarto reservado nessa data.", 409)
    run("update reservas set entrada=?, saida=?, valor=?, cod_funcionario=? where id=?", (d["entrada"], d["saida"], valor, f["codigo"], rid))
    log("edição", f"reserva {rid}", f["codigo"])
    return ok(valor=valor, cod_cliente=r["cod_cliente"])

@app.delete("/api/func/reservas/<int:rid>")
def res_apagar(rid):
    f, e = auth()
    if e: return e
    run("update reservas set status='cancelada' where id=?", (rid,))
    log("exclusão", f"reserva {rid}", f["codigo"])
    return ok()

@app.get("/api/func/logs")
def ver_logs():
    f, e = auth(True)
    return e or jsonify(q("select * from logs order by id desc limit 100"))


if __name__ == "__main__":
    init_db()
    print("Cliente: http://localhost:5000/   |   Funcionário: http://localhost:5000/app")
    app.run(debug=True)
