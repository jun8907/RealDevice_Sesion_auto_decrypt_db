import subprocess
import re
import sys
import time

EXPECTED_COUNT = 2
TIMEOUT       = 15.0  

HOOK_JS = 'hook.js'

CMD = [
    'frida',
    '-U',                             
    '-f', 'network.loki.messenger',   
    '-l', HOOK_JS
]

pattern = re.compile(
    r"\[\+\] Cipher\.doFinal\(inputLen=\d+\) returned outputLen=32 hex=(?P<hex>[0-9a-fA-F]+)"
)

def collect_keys():
    proc = subprocess.Popen(
        CMD,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    keys = []
    deadline = time.time() + TIMEOUT

    try:
        while True:
            line = proc.stdout.readline()
            if not line:
                break

            line = line.strip()

            m = pattern.search(line)
            if m:
                h = m.group('hex')
                if h not in keys:
                    keys.append(h)
                    print(f"[+] 키를 찾았습니다: {h}")
                if len(keys) >= EXPECTED_COUNT:
                    break

            if time.time() > deadline:
                print(f"[!] 타임아웃({TIMEOUT}s) - 수집된 키: {len(keys)}개", file=sys.stderr)
                break

    except KeyboardInterrupt:
        print("\n[!] 사용자 중단", file=sys.stderr)

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()

    return keys

if __name__ == '__main__':
    ks = collect_keys()
    if not ks:
        print("[ERROR] 키를 한 개도 찾지 못했습니다.", file=sys.stderr)
        sys.exit(1)
    print(f"총 {len(ks)}개 키 수집 완료:", ks)
