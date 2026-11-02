# PAV-Project: API de detecção de anomalias em transações financeiras

API REST (FastAPI + SQLAlchemy + PostgreSQL) que registra transações e identifica
operações fora do padrão do cliente, atribuindo um score de risco e uma classificação
(`NORMAL`, `ATTENTION` ou `SUSPICIOUS`) com o motivo de cada alerta.

## Executar com Docker

Requisito: Docker Desktop (ou Docker Engine com o plugin Compose). Nada mais precisa ser instalado.

```bash
docker compose up --build
```

Na primeira vez, o próprio container do banco cria as tabelas e carrega as 7 regras de
detecção (`init.sql`). A API só inicia depois que o banco está pronto.

| O quê                                 | Endereço                                                                 |
| ------------------------------------- | ------------------------------------------------------------------------ |
| API                                   | http://localhost:8000                                                    |
| Documentação interativa (Swagger)     | http://localhost:8000/docs                                               |
| PostgreSQL (opcional, para consultas) | `localhost:5432` · usuário `postgres` · senha `root` · banco `anomalies` |

A interface gráfica roda **fora** dos containers e se comunica com a API em `http://localhost:8000`.

### Comandos úteis

```bash
docker compose ps                   # os dois serviços devem estar "healthy"
docker compose logs -f api          # acompanhar a API
docker compose down                 # parar (os dados são mantidos)
docker compose down -v              # parar e APAGAR os dados (o banco é recriado do zero)
docker compose exec db psql -U postgres -d anomalies    # abrir o banco
```

> O `init.sql` só é executado quando o volume do banco está vazio. Para refazer a
> inicialização, use `docker compose down -v` antes de subir de novo.

## Executar sem Docker (desenvolvimento)

```bash
python -m venv .venv
.venv\Scripts\activate            # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
docker compose up -d db           # só o banco (já sobe com tabelas e regras)
uvicorn app:app --reload
```

Se usar outro PostgreSQL, crie as tabelas e as regras com
`python create_tables.py` e `python seed_rules.py` (ambos podem ser repetidos sem problema).
A conexão vem da variável `DATABASE_URL` (padrão: `postgresql+psycopg2://postgres:root@localhost:5432/anomalies`).

## Alterou uma entidade?

O `init.sql` é **gerado** a partir das entidades (`entities/`) e das regras padrão (`seed_rules.py`):

```bash
python generate_init_sql.py            # regenera o init.sql
python generate_init_sql.py --check    # confere se está atualizado (sai com erro se não estiver)
docker compose down -v && docker compose up --build
```

## Estrutura

```
entities/       modelos SQLAlchemy (clients, rules, transactions, alerts)
schemas/        validação de entrada e saída (Pydantic)
repositories/   acesso ao banco
services/       regras de negócio e motor de detecção (services/rules/)
controllers/    ligação entre as rotas e os services
routes/         endpoints
config/         conexão com o banco e tratamento de erros
app.py          aplicação FastAPI
```
