Java.perform(() => {
  const Cipher = Java.use('javax.crypto.Cipher');

  // 헥스 변환 헬퍼
  function bytesToHex(bytes) {
    if (!bytes) return '';
    return Array.prototype.map
      .call(bytes, (b) => ('00' + (b & 0xff).toString(16)).slice(-2))
      .join('');
  }

  try {
    Cipher.doFinal.overload('[B').implementation = function (data) {
      const result = this.doFinal(data);
      if (result.length === 32) {
        console.log(
          `[+] Cipher.doFinal(inputLen=${data.length}) returned outputLen=${
            result.length
          } hex=${bytesToHex(result)}`
        );
      }
      return result;
    };
  } catch (e) {
    console.error('[!] hook failed:', e);
  }

  console.log(
    '[*] hook-cipher-filtered.js loaded - filtering outputLen=32 only'
  );
});
