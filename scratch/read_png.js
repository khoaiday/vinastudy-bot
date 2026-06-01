const fs = require('fs');
const path = require('path');

const dir = 'daiviet_defense/assets';
const files = fs.readdirSync(dir);

files.forEach(file => {
    if (file.endsWith('.png') && file.startsWith('enemy_')) {
        const filepath = path.join(dir, file);
        const buf = fs.readFileSync(filepath);
        
        // PNG signature check
        if (buf[0] === 0x89 && buf[1] === 0x50 && buf[2] === 0x4E && buf[3] === 0x47) {
            // Find IHDR chunk. In standard PNG, it starts at byte 12 with "IHDR" (0x49 0x48 0x44 0x52)
            // Width is at offset 16 (4 bytes), Height is at offset 20 (4 bytes)
            const width = buf.readUInt32BE(16);
            const height = buf.readUInt32BE(20);
            console.log(`${file}: ${width}x${height}`);
        } else {
            console.log(`${file}: Not a valid PNG`);
        }
    }
});
