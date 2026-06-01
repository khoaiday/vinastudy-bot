const fs = require('fs');
const path = require('path');

function getJpegSize(buf) {
    let i = 2; // skip SOI
    while (i < buf.length) {
        if (buf[i] !== 0xFF) {
            i++;
            continue;
        }
        const marker = buf[i + 1];
        if (marker === 0xD9 || marker === 0xDA) { // EOI or SOS: stop
            break;
        }
        const length = buf.readUInt16BE(i + 2);
        if (marker === 0xC0 || marker === 0xC2) { // SOF0 or SOF2
            const height = buf.readUInt16BE(i + 5);
            const width = buf.readUInt16BE(i + 7);
            return { width, height };
        }
        i += 2 + length;
    }
    return null;
}

function scanDir(dir) {
    const files = fs.readdirSync(dir);
    files.forEach(file => {
        const filepath = path.join(dir, file);
        const stat = fs.statSync(filepath);
        if (stat.isDirectory()) {
            scanDir(filepath);
            return;
        }
        if (file.endsWith('.png') || file.endsWith('.jpg')) {
            const buf = fs.readFileSync(filepath);
            if (buf[0] === 0xFF && buf[1] === 0xD8) {
                const size = getJpegSize(buf);
                if (size) {
                    console.log(`${filepath}: JPEG ${size.width}x${size.height}`);
                } else {
                    console.log(`${filepath}: JPEG but dimensions not found`);
                }
            } else if (buf[0] === 0x89 && buf[1] === 0x50 && buf[2] === 0x4E && buf[3] === 0x47) {
                const width = buf.readUInt32BE(16);
                const height = buf.readUInt32BE(20);
                console.log(`${filepath}: PNG ${width}x${height}`);
            } else {
                console.log(`${filepath}: Unknown format`);
            }
        }
    });
}

scanDir('daiviet_defense/assets');
