# Telemetry_Backend
The UOSupermileage offical repo for a telemetry webapp

# Telemetry units

See [the raw sensor contract and audit](docs/telemetry-units.md) for API/CSV units,
duration semantics, existing-record evidence, and focused test instructions.

See [chart telemetry requests](docs/chart-telemetry.md) for point budgets and
zooming with tick ranges.

## Backend on the Linux VM

The image uses Python 3.14.6 (matching the configured development interpreter),
pip, and the existing pinned `requirements.txt`; there is no separate lockfile
or application build step. It runs `python -m uvicorn app.main:app --host 0.0.0.0
--port 8000` as UID/GID 10001. Compose publishes only `127.0.0.1:8000` for a
reverse proxy on the VM. The database stays in its existing installation;
Compose creates no database and runs no schema/migration commands.

On the VM, with Docker Engine and the Compose plugin installed:

```sh
cp .env.example .env
chmod 600 .env
nano .env
docker compose config --quiet
docker compose build
docker compose up -d --wait
docker compose ps
curl --fail http://127.0.0.1:8000/openapi.json > /dev/null
curl --fail 'http://127.0.0.1:8000/teams?limit=1'
docker compose logs --tail=100 -f backend
# Ctrl-C exits the log viewer. Stop/remove the backend when needed:
docker compose down
```

Supply `DATABASE_URL`: a SQLAlchemy PostgreSQL URL containing the existing
database name, dedicated backend role, password, reachable host, and port.
The example uses the installed psycopg 3 driver (`postgresql+psycopg://`).
URL-encode special characters in usernames/passwords; preserve any required
TLS options (for example `?sslmode=require`) and the database's current policy.
`SQL_ECHO` is optional and defaults to `false`; leave it false on the VM to avoid
logging SQL and parameter values. Shell variables override `.env` values.
`.env` and its variants are Git-ignored and excluded from the image; only these
two settings are passed into the container at runtime. Never commit credentials.

There is no dedicated health endpoint. The image probes the existing
`/openapi.json` route for HTTP liveness. A healthy container does **not** prove
database connectivity; the read-only `/teams?limit=1` request above checks a
database-backed route and requires the existing schema and role permissions.

### Connecting to the existing PostgreSQL installation

`localhost` inside the default container network means the container itself.
Compose maps `host.docker.internal` to Docker's host gateway on Linux; use that
name in `DATABASE_URL` only if PostgreSQL accepts connections on the resulting
host address. This mapping does not make a loopback-only database reachable.
The repo contains no VM listener, firewall, or PostgreSQL authentication config,
so the private connection method must be verified on the VM over NetBird.

Inspect, without changing settings (adjust 5432 if necessary):

```sh
sudo -u postgres psql -c 'SHOW listen_addresses;' -c 'SHOW port;' \
  -c 'SHOW unix_socket_directories;' -c 'SHOW hba_file;'
sudo ss -lntp 'sport = :5432'
# Once built, inspect the container's mapped host address and network/subnet:
docker compose run --rm --no-deps --entrypoint getent backend hosts host.docker.internal
docker network inspect "$(docker inspect "$(docker compose ps -q backend)" --format '{{range .NetworkSettings.Networks}}{{.NetworkID}}{{end}}')"
```

If PostgreSQL already listens on a private address reachable from Docker,
use that address (or the gateway alias when appropriate). Verify the existing
`pg_hba.conf` rules and host firewall permit the actual container source subnet
for only the backend database and role, using the existing password/TLS policy.
NetBird administration alone does not establish Docker-to-database routing.

If `listen_addresses` is only `localhost` / `127.0.0.1` / `::1`, choose one of:

- Mount the existing Unix socket directory read-only into the container using a
  local Compose override, and use a URL such as
  `postgresql+psycopg://USER:PASSWORD@/DATABASE?host=/var/run/postgresql`.
  Verify `unix_socket_directories`, directory/socket permissions for UID 10001,
  and the applicable `local` rules in `pg_hba.conf`. Peer authentication depends
  on the OS identity and may not accept this container user; preserve it rather
  than replacing it with `trust`.
- Have the VM maintainer approve PostgreSQL listening on a specific Docker host
  bridge/private address in addition to loopback. Verify that exact address is
  what the container reaches, restrict authentication to the backend role,
  database and actual Docker source subnet, and restrict the host firewall.
  Listener changes require a PostgreSQL restart. Do not use a public listener,
  broad `trust` rules, or public firewall allowances.
- Linux host networking can reach the existing loopback listener without a
  database listener change. This requires a deliberate alternative Compose
  configuration: remove `ports` and `extra_hosts`, set `network_mode: host`, and
  override the Uvicorn command to bind **127.0.0.1:8000**, with `localhost` in
  `DATABASE_URL`. The default `0.0.0.0` command would expose the API on the VM's
  interfaces in host mode. Review this tradeoff before using it.

Do not publish the database port or apply `app/db/schema.sql` to production as
part of container startup. See [Docker networking](https://docs.docker.com/compose/how-tos/networking/),
[PostgreSQL listener/socket settings](https://www.postgresql.org/docs/current/runtime-config-connection.html),
and [PostgreSQL access rules](https://www.postgresql.org/docs/current/auth-pg-hba-conf.html).
