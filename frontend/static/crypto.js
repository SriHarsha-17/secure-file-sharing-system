/*
 Browser-side cryptography.
 Plaintext is read and encrypted in this browser before upload.
 AES-GCM provides authenticated encryption.
*/

const CryptoClient = (() => {
  const enc = new TextEncoder();

  function bytesToBase64(bytes) {
    let binary = "";
    const chunk = 0x8000;
    for (let i = 0; i < bytes.length; i += chunk) {
      binary += String.fromCharCode(...bytes.subarray(i, i + chunk));
    }
    return btoa(binary);
  }

  function base64ToBytes(b64) {
    const binary = atob(b64);
    const out = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) out[i] = binary.charCodeAt(i);
    return out;
  }

  async function generateKey() {
    return crypto.subtle.generateKey(
      {name: "AES-GCM", length: 256},
      true,
      ["encrypt", "decrypt"]
    );
  }

  async function exportKey(key) {
    return bytesToBase64(new Uint8Array(await crypto.subtle.exportKey("raw", key)));
  }

  async function importKey(b64) {
    return crypto.subtle.importKey(
      "raw", base64ToBytes(b64),
      {name: "AES-GCM"}, false, ["encrypt", "decrypt"]
    );
  }

  async function sha256(buffer) {
    const digest = await crypto.subtle.digest("SHA-256", buffer);
    return [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, "0")).join("");
  }

  async function encryptFile(file) {
    const plaintext = await file.arrayBuffer();
    const key = await generateKey();
    const nonce = crypto.getRandomValues(new Uint8Array(12));

    const ciphertext = await crypto.subtle.encrypt(
      {name: "AES-GCM", iv: nonce, tagLength: 128},
      key,
      plaintext
    );

    return {
      ciphertext: new Blob([ciphertext], {type: "application/octet-stream"}),
      keyB64: await exportKey(key),
      nonceB64: bytesToBase64(nonce),
      plaintextHash: await sha256(plaintext),
      originalName: file.name
    };
  }

  async function decryptFile(cipherBlob, keyB64, nonceB64) {
    const ciphertext = await cipherBlob.arrayBuffer();
    const key = await importKey(keyB64);
    const plaintext = await crypto.subtle.decrypt(
      {name: "AES-GCM", iv: base64ToBytes(nonceB64), tagLength: 128},
      key,
      ciphertext
    );
    return new Blob([plaintext]);
  }

  return {encryptFile, decryptFile, sha256};
})();
