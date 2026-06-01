/**
 * crack_xor.js  –  FR2 APK asset XOR-key finder & audio extractor
 *
 * Usage:  node crack_xor.js
 *
 * Strategy:
 *   1. Read all numbered files from the assets folder.
 *   2. For every file, try all 256 single-byte XOR keys (0x00–0xFF).
 *      Also try common multi-byte keys: [0x97,0x31], [0xAB,0xCD],
 *      [0x12,0x34,0x56,0x78], etc.
 *   3. Check whether the first 4 decrypted bytes match a known magic number
 *      (MP3, OGG, PNG, JPG, ZIP, FSB5 FMOD soundbank, WAV/RIFF).
 *   4. Copy successfully identified audio files (.mp3 / .ogg / .fsb) to the
 *      output directory with proper extensions.
 *   5. Print a full report at the end.
 */

'use strict';

const fs   = require('fs');
const path = require('path');

// ── Configuration ─────────────────────────────────────────────────────────────
const ASSETS_DIR = path.join(
  'C:\\Users\\Nam\\OneDrive\\Desktop\\vinastudy-bot\\apk\\fr2_extracted\\assets'
);
const OUTPUT_DIR = path.join(
  'C:\\Users\\Nam\\OneDrive\\Desktop\\vinastudy-bot\\daiviet_defense\\audio\\fr2_originals'
);

// Size filters (bytes).  Focus: 50 KB – 10 MB (catches BGM + SFX banks)
const MIN_SIZE =   50 * 1024;   //  50 KB
const MAX_SIZE = 10 * 1024 * 1024; // 10 MB

// ── Magic-number table ────────────────────────────────────────────────────────
// Each entry: { magic: Buffer, ext: string, type: string }
const SIGNATURES = [
  // Audio
  { magic: Buffer.from([0xFF, 0xFB]),         ext: '.mp3', type: 'MP3'   },
  { magic: Buffer.from([0xFF, 0xF3]),         ext: '.mp3', type: 'MP3'   },
  { magic: Buffer.from([0xFF, 0xF2]),         ext: '.mp3', type: 'MP3'   },
  { magic: Buffer.from([0xFF, 0xFA]),         ext: '.mp3', type: 'MP3'   },
  { magic: Buffer.from([0xFF, 0xE0]),         ext: '.mp3', type: 'MP3 (MPEG-2.5)' },
  { magic: Buffer.from([0x49, 0x44, 0x33]),   ext: '.mp3', type: 'MP3 (ID3)' },
  { magic: Buffer.from([0x4F, 0x67, 0x67, 0x53]), ext: '.ogg', type: 'OGG'  },
  { magic: Buffer.from([0x46, 0x53, 0x42, 0x35]), ext: '.fsb', type: 'FSB5 (FMOD bank)' },
  { magic: Buffer.from([0x52, 0x49, 0x46, 0x46]), ext: '.wav', type: 'WAV/RIFF' },
  // Image (for confirmation, not copying)
  { magic: Buffer.from([0x89, 0x50, 0x4E, 0x47]), ext: '.png', type: 'PNG'  },
  { magic: Buffer.from([0xFF, 0xD8, 0xFF]),        ext: '.jpg', type: 'JPEG' },
  // Archive / other known formats
  { magic: Buffer.from([0x50, 0x4B, 0x03, 0x04]), ext: '.zip', type: 'ZIP'  },
  { magic: Buffer.from([0x42, 0x4D]),              ext: '.bmp', type: 'BMP'  },
  { magic: Buffer.from([0x47, 0x49, 0x46]),        ext: '.gif', type: 'GIF'  },
];

const AUDIO_EXTS = new Set(['.mp3', '.ogg', '.fsb', '.wav']);

// ── Multi-byte XOR keys to try in addition to single-byte sweep ───────────────
const MULTI_BYTE_KEYS = [
  // Common game obfuscation patterns
  [0x97, 0x31],
  [0x97, 0x35],
  [0xAB, 0xCD],
  [0xDE, 0xAD],
  [0xBE, 0xEF],
  [0xCA, 0xFE],
  [0xBA, 0xBE],
  [0x12, 0x34],
  [0x12, 0x34, 0x56, 0x78],
  [0xFF, 0x00],
  [0x55, 0xAA],
  [0xAA, 0x55],
  [0x5A, 0xA5],
  [0xA5, 0x5A],
  // Nilei / Fieldrunners-family keys seen in other FR builds
  [0x0B, 0x0E, 0x0F],
  [0x7F, 0x00, 0xFF],
  [0x13, 0x37],
  [0xC0, 0xDE],
  [0x0D, 0x0E, 0x0A, 0x0D],
  // FR1 Android assets XOR key (if same team reused it)
  [0x97],
  [0x42],
  [0x69],
  [0x7C],
  [0x5C],
  [0x3C],
  [0x2A],
];

// ── Helpers ───────────────────────────────────────────────────────────────────
function xorDecryptHeader(buf, key) {
  // Returns the first 16 XOR-decrypted bytes (enough to check magic)
  const result = Buffer.allocUnsafe(Math.min(16, buf.length));
  for (let i = 0; i < result.length; i++) {
    result[i] = buf[i] ^ key[i % key.length];
  }
  return result;
}

function detectSignature(decryptedHeader) {
  for (const sig of SIGNATURES) {
    const m = sig.magic;
    let match = true;
    for (let i = 0; i < m.length; i++) {
      if (decryptedHeader[i] !== m[i]) { match = false; break; }
    }
    if (match) return sig;
  }
  return null;
}

function xorDecryptFull(buf, key) {
  const result = Buffer.allocUnsafe(buf.length);
  for (let i = 0; i < buf.length; i++) {
    result[i] = buf[i] ^ key[i % key.length];
  }
  return result;
}

function keyToHex(key) {
  return key.map(b => b.toString(16).padStart(2, '0').toUpperCase()).join(' ');
}

function sizeLabel(bytes) {
  if (bytes >= 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  if (bytes >= 1024)        return (bytes / 1024).toFixed(1) + ' KB';
  return bytes + ' B';
}

// ── Main ──────────────────────────────────────────────────────────────────────
(function main() {
  console.log('=== FR2 XOR Key Cracker ===');
  console.log(`Assets dir : ${ASSETS_DIR}`);
  console.log(`Output dir : ${OUTPUT_DIR}`);
  console.log(`Size range : ${sizeLabel(MIN_SIZE)} – ${sizeLabel(MAX_SIZE)}`);
  console.log('');

  // Ensure output directory exists
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });

  // Read all asset files sorted numerically
  const allFiles = fs.readdirSync(ASSETS_DIR)
    .filter(f => /^\d{8}$/.test(f))   // only 8-digit numbered files
    .sort((a, b) => parseInt(a) - parseInt(b));

  console.log(`Total asset files: ${allFiles.length}`);

  // Filter by size
  const candidates = allFiles.filter(f => {
    const s = fs.statSync(path.join(ASSETS_DIR, f)).size;
    return s >= MIN_SIZE && s <= MAX_SIZE;
  });

  console.log(`Files in size range ${sizeLabel(MIN_SIZE)}–${sizeLabel(MAX_SIZE)}: ${candidates.length}`);
  console.log('');
  console.log('Scanning...\n');

  const results = [];
  let cracked = 0;
  let audioFound = 0;
  let globalKeyVotes = {}; // tally which key appears most often

  // Build the complete key list: all 256 single-byte + multi-byte combos
  const allKeys = [];
  for (let k = 0; k <= 0xFF; k++) allKeys.push([k]);
  for (const mk of MULTI_BYTE_KEYS) allKeys.push(mk);

  for (const fileName of candidates) {
    const filePath = path.join(ASSETS_DIR, fileName);
    const stat = fs.statSync(filePath);
    const buf  = fs.readFileSync(filePath);

    let found = null;

    for (const key of allKeys) {
      // Skip XOR with 0x00 for single-byte (it's a no-op, means no encryption)
      // but still check it – the file might already be plaintext!
      const header = xorDecryptHeader(buf, key);
      const sig    = detectSignature(header);
      if (sig) {
        found = { key, sig, header };
        break;
      }
    }

    const fileSize = stat.size;
    const sizeStr  = sizeLabel(fileSize);

    if (found) {
      cracked++;
      const { key, sig } = found;
      const keyHex = keyToHex(key);
      const isAudio = AUDIO_EXTS.has(sig.ext);

      // Vote for global key
      const voteKey = keyHex;
      globalKeyVotes[voteKey] = (globalKeyVotes[voteKey] || 0) + 1;

      console.log(`✓ ${fileName}  [${sizeStr}]  →  ${sig.type}  (key: 0x${keyHex})`);

      let outFile = null;
      if (isAudio) {
        audioFound++;
        const decrypted = xorDecryptFull(buf, key);
        const outName   = `${fileName}${sig.ext}`;
        outFile         = path.join(OUTPUT_DIR, outName);
        fs.writeFileSync(outFile, decrypted);
        console.log(`  ↳ Saved → ${outName}`);
      }

      results.push({
        fileName,
        size: fileSize,
        sizeStr,
        type: sig.type,
        ext: sig.ext,
        keyHex,
        isAudio,
        outFile,
      });
    } else {
      // Not cracked with any known key – show raw first bytes for manual analysis
      const rawHex = [...buf.slice(0, 8)].map(b => b.toString(16).padStart(2,'0').toUpperCase()).join(' ');
      console.log(`✗ ${fileName}  [${sizeStr}]  unknown  (raw: ${rawHex})`);
      results.push({
        fileName,
        size: fileSize,
        sizeStr,
        type: 'UNKNOWN',
        ext: null,
        keyHex: null,
        isAudio: false,
        outFile: null,
        rawBytes: rawHex,
      });
    }
  }

  // ── Global key analysis ──────────────────────────────────────────────────
  console.log('\n' + '='.repeat(60));
  console.log('KEY VOTE TALLY (most common XOR key across all cracked files):');
  const sortedKeys = Object.entries(globalKeyVotes)
    .sort((a, b) => b[1] - a[1]);
  for (const [k, count] of sortedKeys) {
    console.log(`  0x${k.padEnd(12)}  →  ${count} file(s)`);
  }

  // ── Summary ──────────────────────────────────────────────────────────────
  console.log('\n' + '='.repeat(60));
  console.log('SUMMARY');
  console.log('='.repeat(60));
  console.log(`Candidates scanned : ${candidates.length}`);
  console.log(`Cracked            : ${cracked}`);
  console.log(`Audio files found  : ${audioFound}`);
  console.log(`Output dir         : ${OUTPUT_DIR}`);

  console.log('\nAUDIO FILES EXTRACTED:');
  const audioResults = results.filter(r => r.isAudio);
  if (audioResults.length === 0) {
    console.log('  (none)');
  } else {
    for (const r of audioResults) {
      console.log(`  ${r.fileName}  [${r.sizeStr}]  ${r.type}  key=0x${r.keyHex}  → ${path.basename(r.outFile || '')}`);
    }
  }

  console.log('\nNON-AUDIO CRACKED:');
  const nonAudio = results.filter(r => !r.isAudio && r.type !== 'UNKNOWN');
  if (nonAudio.length === 0) {
    console.log('  (none)');
  } else {
    for (const r of nonAudio) {
      console.log(`  ${r.fileName}  [${r.sizeStr}]  ${r.type}  key=0x${r.keyHex}`);
    }
  }

  console.log('\nUNCRACKED FILES:');
  const uncracked = results.filter(r => r.type === 'UNKNOWN');
  if (uncracked.length === 0) {
    console.log('  (none – all files identified!)');
  } else {
    for (const r of uncracked) {
      console.log(`  ${r.fileName}  [${r.sizeStr}]  raw: ${r.rawBytes}`);
    }
  }

  // ── Extra pass: if a dominant single key was found, re-scan ALL files ─────
  if (sortedKeys.length > 0) {
    const dominantKey = sortedKeys[0][0];  // e.g. "97"
    const dominantKeyBytes = dominantKey.split(' ').map(h => parseInt(h, 16));
    const dominantCount = sortedKeys[0][1];

    if (dominantCount >= 3) {
      console.log(`\n${'='.repeat(60)}`);
      console.log(`DOMINANT KEY FOUND: 0x${dominantKey}  (${dominantCount} matches)`);
      console.log('Running full scan on ALL files using this key...\n');

      let bonusAudio = 0;
      for (const fileName of allFiles) {
        // Skip already-processed candidates
        if (candidates.includes(fileName)) continue;

        const filePath = path.join(ASSETS_DIR, fileName);
        const stat2    = fs.statSync(filePath);
        if (stat2.size < 4) continue;

        const buf2    = fs.readFileSync(filePath);
        const header2 = xorDecryptHeader(buf2, dominantKeyBytes);
        const sig2    = detectSignature(header2);

        if (sig2 && AUDIO_EXTS.has(sig2.ext)) {
          bonusAudio++;
          const decrypted2 = xorDecryptFull(buf2, dominantKeyBytes);
          const outName2   = `${fileName}${sig2.ext}`;
          const outFile2   = path.join(OUTPUT_DIR, outName2);
          fs.writeFileSync(outFile2, decrypted2);
          console.log(`  BONUS ✓ ${fileName} [${sizeLabel(stat2.size)}] ${sig2.type} → ${outName2}`);
        }
      }
      console.log(`\n  Bonus audio files extracted: ${bonusAudio}`);
      console.log(`  Total audio: ${audioFound + bonusAudio}`);
    }
  }

  console.log('\nDone!');
})();
