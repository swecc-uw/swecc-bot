# swecc-server

## Getting Started

### Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Add env variables to `venv/bin/activate`

```bash
export DISCORD_TOKEN=<...>
export ADMIN_CHANNEL=<...>
export LC_CHANNEL_ID=<...>
export SWECC_API_KEY=<...>
export SWECC_URL=<...>
export PREFIX_COMMAND=<...>
```


## Reference

| task | command |
| --- | --- |
| run server | `python main.py` |