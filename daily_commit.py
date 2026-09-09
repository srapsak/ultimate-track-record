# daily_commit.py — nightly tamper-evident track-record commitment.
import csv, hashlib, io, json, os, subprocess, sys
from datetime import datetime, timedelta

REPO_DIR   = os.path.dirname(os.path.abspath(__file__))
CSV_FILE   = r'F:\TRADING\project_FinRL_meta_rl\trade_history.csv'
CHAIN_FILE = os.path.join(REPO_DIR, 'hash_chain.jsonl')
REVEAL_DIR = os.path.join(REPO_DIR, 'reveals')

def canonical_text(header, rows):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(header)
    w.writerows(rows)
    return buf.getvalue()

def load_chain():
    if not os.path.exists(CHAIN_FILE):
        return []
    with open(CHAIN_FILE, encoding='utf-8') as f:
        return [json.loads(l) for l in f if l.strip()]

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    push = '--push' in sys.argv[1:]
    day = args[0] if args else (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')

    chain = load_chain()
    if any(r.get('date') == day for r in chain):
        print(f'already committed {day}: {[r for r in chain if r["date"] == day][0]["day_hash"]}')
        return

    with open(CSV_FILE, newline='', encoding='utf-8') as f:
        rd = csv.reader(f)
        header = next(rd)
        rows = [r for r in rd if len(r) > 1 and r[1].startswith(day)]

    text = canonical_text(header, rows)
    day_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
    prev = chain[-1]['chain_hash'] if chain else '0' * 64
    chain_hash = hashlib.sha256((prev + day_hash).encode()).hexdigest()

    i = header.index('pnl_usd')
    net  = sum(float(r[i]) for r in rows)
    wins = sum(1 for r in rows if float(r[i]) > 0)

    os.makedirs(REVEAL_DIR, exist_ok=True)
    with open(os.path.join(REVEAL_DIR, f'{day}.csv'), 'w', encoding='utf-8', newline='') as f:
        f.write(text)

    rec = {'date': day, 'trades': len(rows), 'wins': wins, 'net_pnl_usd': round(net, 6),
           'day_hash': day_hash, 'prev': prev, 'chain_hash': chain_hash,
           'committed_utc': datetime.utcnow().isoformat() + 'Z'}
    with open(CHAIN_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(rec) + '\n')

    print('=' * 60)
    print(f'DAY {day} | trades={len(rows)} | wins={wins} | net={net:+.6f} USDT')
    print(f'day_hash   {day_hash}')
    print(f'chain_hash {chain_hash}')
    print('=' * 60)
    print('LinkedIn line:')
    print(f'Daily ledger commitment {day}: {len(rows)} trades, net {net:+.2f} USDT. '
          f'SHA-256 {day_hash[:16]}... chained from {prev[:16]}... '
          f'Raw rows + chain: github.com/srapsak/ultimate-track-record')

    if push:
        for cmd in (['git', 'add', '-A'],
                    ['git', 'commit', '-m', f'ledger day {day}'],
                    ['git', 'push']):
            subprocess.run(cmd, cwd=REPO_DIR, check=True)
        print('pushed')

if __name__ == '__main__':
    main()