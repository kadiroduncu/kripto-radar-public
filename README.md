# Kripto Radar public launcher

Public app: https://kripto-short-radar.streamlit.app/

This launcher runs a pinned version of the private research app on Streamlit Community Cloud. The user explicitly approved public display of dashboard scores, observations and research results. Source archives and checkpoint ZIPs remain in the private repository.

Python: 3.11. Entrypoint: app.py.

## One-time connection

Create a fine-grained GitHub token for only `kadiroduncu/kripto-short-radar`, with repository Contents permission set to Read and write. Enter it directly into this app's Streamlit Settings > Secrets, never into source code or chat:

```toml
[radar]
github_repo = "kadiroduncu/kripto-short-radar"
github_token = "REPLACE_DIRECTLY_IN_STREAMLIT_SECRETS"
```

The token downloads the pinned private application and reads/writes verified private checkpoints. It does not connect to an exchange or place orders. Without this connection, the public app shows a setup message and does not start a fresh research experiment.

Streamlit may hibernate. Continuous 24/7 collection is not guaranteed. Checkpoint backups run hourly while the research engine is running.
