import os
import sys
import sqlite3
import csv
import xml.etree.ElementTree as ET
from sqlcipher3 import dbapi2 as sqlcipher
import hook

def decrypt_and_export_db(encrypted_db_path, output_db_path, key_plaintext):
    try:
        print(f"[*] 복호화 시도 – key: {key_plaintext}")
        conn = sqlcipher.connect(encrypted_db_path)
        cur = conn.cursor()
        cur.execute(f"PRAGMA key = '{key_plaintext}';")
        cur.execute("PRAGMA cipher_page_size = 4096;")
        cur.execute("PRAGMA kdf_iter = 1;")
        cur.execute("PRAGMA cipher_hmac_algorithm = HMAC_SHA512;")
        cur.execute("PRAGMA cipher_kdf_algorithm = PBKDF2_HMAC_SHA512;")
        cur.execute("SELECT count(*) FROM sqlite_master;")
        print("[+] 복호화 성공")

        os.makedirs(os.path.dirname(output_db_path), exist_ok=True)
        print(f"[*] 백업 중 → {output_db_path}")
        with sqlite3.connect(output_db_path) as out_conn:
            out_cur = out_conn.cursor()
            cur.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
            for name, sql in cur.fetchall():
                if not sql or name == "sqlite_sequence" or "fts5" in sql.lower():
                    continue
                out_cur.execute(sql)
                cur.execute(f"SELECT * FROM {name}")
                rows = cur.fetchall()
                if not rows:
                    continue
                ph = ",".join("?" * len(rows[0]))
                for row in rows:
                    out_cur.execute(f"INSERT INTO {name} VALUES ({ph})", row)
            out_conn.commit()

        base   = os.path.splitext(os.path.basename(output_db_path))[0]
        parent = os.path.dirname(output_db_path)
        csv_dir = os.path.join(parent, f"{base}_csv")
        xml_dir = os.path.join(parent, f"{base}_xml")
        os.makedirs(csv_dir, exist_ok=True)
        os.makedirs(xml_dir, exist_ok=True)

        with sqlite3.connect(output_db_path) as exp_conn:
            exp_cur = exp_conn.cursor()
            exp_cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [t[0] for t in exp_cur.fetchall()]
            for table in tables:
                exp_cur.execute(f"PRAGMA table_info({table})")
                cols = [c[1] for c in exp_cur.fetchall()]
                exp_cur.execute(f"SELECT * FROM {table}")
                rows = exp_cur.fetchall()

                
                csv_path = os.path.join(csv_dir, f"{table}.csv")
                with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    writer.writerow(cols)
                    for row in rows:
                        out = []
                        for val in row:
                            out.append(val.hex() if isinstance(val, (bytes,bytearray)) else val)
                        writer.writerow(out)
                print(f"[+] CSV 저장: {csv_path}")

                
                root = ET.Element(f"{table}_rows")
                for row in rows:
                    elem = ET.SubElement(root, table)
                    for col_name, val in zip(cols, row):
                        sub = ET.SubElement(elem, col_name)
                        sub.text = '' if val is None else str(val)
                xml_path = os.path.join(xml_dir, f"{table}.xml")
                ET.ElementTree(root).write(xml_path, encoding='utf-8', xml_declaration=True)
                print(f"[+] XML 저장: {xml_path}")

        conn.close()
        return True

    except Exception as e:
        print(f"[!] 복호화 실패 (key={key_plaintext}): {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    keys = hook.collect_keys()
    if not keys:
        print("[ERROR] 키를 하나도 찾지 못했습니다.", file=sys.stderr)
        sys.exit(1)

    src_db = "extracted_files/session.db"
    dst_db = "decrypted_files/dec_session.sqlite"
    for k in keys:
        if decrypt_and_export_db(src_db, dst_db, k):
            print(f"[+] 최종 복호화 성공 키: {k}")
            sys.exit(0)
        else:
            print(f"[*] 키 {k} 로 실패, 다음 키 시도...")

    print("[ERROR] 모든 키로 복호화에 실패했습니다.", file=sys.stderr)
    sys.exit(1)
