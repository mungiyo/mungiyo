# Seongtae Jang (mungiyo)

**Data Engineer** — I build and run data platforms: CDC ingestion on Kafka, orchestration on Airflow, and serving on a lakehouse.

[Blog](https://mungiyo.tistory.com/)

## Tech Stack

- **Ingestion** — Debezium CDC on Kafka Connect, custom SMTs, Iceberg sink
- **Processing** — Spark (Spark Connect on Kubernetes), Flink, dbt
- **Orchestration** — Airflow 3 on Kubernetes, dbt on Cosmos
- **Serving** — Databricks (Delta, Unity Catalog), feature store
- **Platform** — Kubernetes, ArgoCD, Terraform, OpenMetadata

## Open Source Contributions

- [apache/airflow#73517](https://github.com/apache/airflow/pull/73517) — Stream S3 remote task logs (peak heap 1,169 → 30 MiB)
- [astronomer/astronomer-cosmos#2815](https://github.com/astronomer/astronomer-cosmos/pull/2815) — Atomic writes for the dbt partial-parse cache
- [datahub-project/datahub#5918](https://github.com/datahub-project/datahub/issues/5918) — Tableau ingestion bug report
