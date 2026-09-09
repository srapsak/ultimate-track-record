# ultimate-track-record
Tamper-evident daily ledger of a live Binance spot execution engine.
Each day's raw trade rows are frozen in reveals/<date>.csv, hashed with
SHA-256, and chained in hash_chain.jsonl. GitHub commit timestamps are
the notary. Audit: clone, recompute each file's SHA-256, walk the chain.
If one row is ever altered, inserted or removed, the chain breaks.
No keys, no balances, no strategy code. The engine stays home.