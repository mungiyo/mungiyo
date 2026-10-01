# Hi, I'm Seongtae Jang (mungiyo)

- 🌐 Blog: [mungiyo.tistory.com](https://mungiyo.tistory.com/)
- 📧 wkdtjdxo2@gmail.com

## Open Source Contributions

| Project | PR / Issue | Status | Summary |
|---|---|---|---|
| **apache/airflow** | [#73517](https://github.com/apache/airflow/pull/73517) | 🟡 In review | Add `S3RemoteLogIO.stream()` so S3 remote task logs are streamed instead of loaded whole. Peak heap for a 250 MB log read: 1,169 → 30 MiB. Fixes api-server OOM kills that also took down the Task Execution API. |
| **astronomer/astronomer-cosmos** | [#2815](https://github.com/astronomer/astronomer-cosmos/pull/2815) | ✅ Merged | Atomic writes for the `partial_parse.msgpack` cache (`safe_copy` with file-mode preservation). Fixes a race where parallel dbt tasks sharing a cache dir silently fell back to a full parse. |
| **datahub-project/datahub** | [#5918](https://github.com/datahub-project/datahub/issues/5918) | 🐛 Issue | Tableau ingestion failed on dataset names containing a comma — URN was split into 4 parts because the name wasn't encoded. |
