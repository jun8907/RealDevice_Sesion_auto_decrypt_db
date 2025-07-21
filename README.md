# RealDevice_Session_auto_decrypt_db 🔐

복호화되지 않은 Session 메신저의 session.db 파일을 복호화하는 코드입니다.

<br><br>

## 🧪 사용법

```bash
git clone https://github.com/jun8907/RealDevice_Session_auto_decrypt_db.git
cd RealDevice_Session_auto_decrypt_db
pip install -r requirements.txt
python pull.py
python decrypt_db.py
```

<br><br>

## 📖 관련 라이브러리 설치

```bash
> pip install pycryptodome
> pip install sqlcipher3-wheels
> pip install frida-tools
```

<br><br>
## 🪝 Frida 설치
frida를 통해 signal.db의 복호화 키를 후킹하기 때문에 frida를 설치.
```bash
> pip install frida-tools
> frida --version
17.x.x
```

**Frida 서버 준비 (Android 기기용)**
```bash
https://github.com/frida/frida/releases
```
기기 아키텍처에 맞는 frida-server 다운로드

**Android 기기의 CPU 아키텍처 확인**
```bash
> adb shell getprop ro.product.cpu.abi
arm64-v8a
```

**압축해제**
```bash
> xz -d frida-server-17.x.x-android-arm64.xz
> chmod +x frida-server-17.x.x-android-arm64
```

**ADB로 기기에 전송**
```bash
> adb push frida-server-17.x.x-android-arm64 /data/local/tmp/
```

**루팅 쉘 진입 후 실행**
```bash
> adb shell
> su
> chmod 755 /data/local/tmp/frida-server-17.x.x-android-arm64
> /data/local/tmp/frida-server-17.x.x-android-arm64 &
```

<br><br>

## 🔧 코드 설명

- pull.py
- hook.py
- hook.js
- decrypt_db.py
<br><br>
### pull.py

루팅된 Android 디바이스에서 Session 메신저의 db 파일을 자동으로 추출하는 코드입니다.
db 파일은 `extracted_files/` 디렉터리에 저장

```python
[실행 결과]
[*] su 권한으로 /data/data/network.loki.messenger/databases/session.db → /sdcard/session.db 복사 중...
[*] /sdcard/session.db → extracted_files\session.db 로컬로 추출 중...
/sdcard/session.db: 1 file pulled, 0 skipped. 21.3 MB/s (1024000 bytes in 0.046s)
[+] 추출 완료: extracted_files\session.db
```

<br><br>
### hook.py

Frida로 hook.js를 앱에 로드하고, 출력된 키를 정규 표현식으로 추출하여 출력하는 코드입니다.

```python
[실행 결과]
[+] 키를 찾았습니다: 76b1f11c582a8372c994844b19bfe8c6cae019b7ba6d8fe7db7422696ca981b0
[+] 키를 찾았습니다: 62b9b15b5dcdd9dc4db74cb183cb488b32e68b5af8bf16c4addab22426f0c3ce
총 2개 키 수집 완료: ['76b1f11c582a8372c994844b19bfe8c6cae019b7ba6d8fe7db7422696ca981b0', '62b9b15b5dcdd9dc4db74cb183cb488b32e68b5af8bf16c4addab22426f0c3ce']
```

<br><br>
### hook.js

javax.crypto.Cipher 클래스를 후킹하여 session.db 복호화에 사용되는 32바이트 키를 캡처합니다.

```python
[실행 결과]
[+] Cipher.doFinal(inputLen=48) returned outputLen=32 hex=76b1f11c582a8372c994844b19bfe8c6cae019b7ba6d8fe7db7422696ca981b0
[+] Cipher.doFinal(inputLen=48) returned outputLen=32 hex=62b9b15b5dcdd9dc4db74cb183cb488b32e68b5af8bf16c4addab22426f0c3ce
```

<br><br>
### decrypt_db.py

암호화된 Session 데이터베이스(`session.db`)를 복호화하여 일반 SQLite, 텍스트 형식으로 변환 및 저장해주는 코드 입니다.

```python
[실행 결과]
[*] 복호화 시도 – key: 76b1f11c582a8372c994844b19bfe8c6cae019b7ba6d8fe7db7422696ca981b0
[+] 복호화 성공
[*] 백업 중 → decrypted_files/dec_session.sqlite
[+] CSV 저장: decrypted_files\dec_session_csv\{table_name}.csv
[+] XML 저장: decrypted_files\dec_session_xml\{table_name}.xml
[+] 최종 복호화 성공 키: 76b1f11c582a8372c994844b19bfe8c6cae019b7ba6d8fe7db7422696ca981b0
```
