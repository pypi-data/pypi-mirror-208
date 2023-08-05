# lnhub-rest: Cross-instance management

Note: For more extensive documentation & testing, see [docs](docs).

## Summary

1. Installation
2. CLI
   1. Run server
   2. Run tests
   3. Launch Jupyter lab
   4. Migrate
3. Deployment
4. Usage
5. Release process

## 1. Installation

1. Clone this repository
2. Navigate to the repository and run:

   ```
   pip install .
   ```

## 2. Dependencies

1. Supabase CLI

   To use lnhub CLI on local environment you will first have to install and configure [Supabase CLI](https://supabase.com/docs/guides/cli).

2. Docker

   You must also have Docker installed to allow
   Supabase CLI to create and run the relevant containers

## 3. Local Development

The [lnhub](lnhub_rest/__main__.py) script serves as the entrypoint for all actions you need to run for local development.

:warning: It is important that you use this entrypoint as it properly configures the settings.

To ensure that the environment is properly configured you can do one of three things:

1. Set `LAMIN_ENV=local` prior to running `lnhub`. This will ensure that a local Supabase instance is started and that the connection strings are properly configured.
2. If you want to connect to an external Supabase (either in the cloud or managed by another process), you can customize `LAMIN_ENV=foobar` (or `prod` or `staging`) and place a corresponding .env file in the root folder. In this case it would be `lnhub-rest--foobar.env`.

   - The .env file must contain values for the following variables:

     ```
     POSTGRES_DSN
     SUPABASE_API_URL
     SUPABASE_ANON_KEY
     SUPABASE_SERVICE_KEY
     ```

### Run the server

```
LAMIN_ENV=local lnhub run
```

### Run tests

```
LAMIN_ENV=local lnhub test -s test_local
```

Any parameters after the `lnhub test` command are passed directly to `nox`

### Launch Jupyter lab

```
LAMIN_ENV=local lnhub jupyter
```

### Open an IPython shell

```
LAMIN_ENV=local lnhub shell
```

### Migrate

See [Migrations](docs/migrations.md)

## 3. Deployment

Push on the `staging` branch to deploy in staging.

Push on the `main` branch to deploy in production.

## 4. Usage

Access API documentation from these endpoints.

Locally:

```
http://localhost:8000/docs
```

On `staging` server :

```
https://lnhub-rest-cloud-run-staging-xv4y7p4gqa-uc.a.run.app/docs
```

On `production` server:

```
https://lnhub-rest-cloud-run-main-xv4y7p4gqa-uc.a.run.app/docs
```

## 5. Release process
