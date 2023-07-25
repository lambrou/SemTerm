# First stage: build the project
FROM python:3.11-slim as builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install poetry

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

RUN apt-get update && \
    apt-get install -y gpg wget lsb-release

RUN wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg && \
    fingerprint=$(gpg --no-default-keyring --keyring /usr/share/keyrings/hashicorp-archive-keyring.gpg --fingerprint) && \
    if [ $fingerprint != *"798A 1EC65 4E5C 1542 8C8E  42EE AA16 FCBC A621 E701"* ]; then \
        echo "Hashicorp GPG key fingerprint mismatch! Received: $fingerprint"; \
        exit 1; \
    fi && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | \
    tee /etc/apt/sources.list.d/hashicorp.list && \
    apt-get update && \
    apt-get install -y vault jq && \
    apt-get remove -y && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY . /app


FROM python:3.11-slim as runner

ARG CI

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

RUN if [ "$CI" = "true" ]; then \
    export VAULT_TOKEN="$(vault write -field=token auth/jwt/login role=boomtown-$CI_ENVIRONMENT_SLUG jwt=$CI_JOB_JWT)" && \
    vault kv get -format=json kv/$CI_ENVIRONMENT_SLUG/boomtown/pipeline_vars | jq -r '.data.data | to_entries | map("\(.key)=\(.value|@sh)") | .[]' > pipeline_vars.env && \
    vault kv get -field=SERVICE_ACCOUNT.json kv/$CI_ENVIRONMENT_SLUG/boomtown/files | base64 > SERVICE_ACCOUNT.json.base64 && \
    vault kv get -field=master-values.yaml kv/$CI_ENVIRONMENT_SLUG/boomtown/files > master-values.yaml && \
    export MASTER_VALUES_YAML_SHA256=$(sha256sum master-values.yaml) && \
    set -o allexport && \
    source pipeline_vars.env && \
    export OPENAI_API_KEY=OPENAI_API_KEY_$CI_ENVIRONMENT_SLUG && \
    set +o allexport \
    ; fi

CMD ["python", "-m", "supervisor.supervisord", "-c", "conf/supervisord.conf"]
