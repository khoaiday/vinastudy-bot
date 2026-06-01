const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, '..', 'daiviet_defense', '3d_assets', 'custom', 'enemy_scout.glb');
console.log('Reading file:', filePath);

if (!fs.existsSync(filePath)) {
  console.error('File does not exist!');
  process.exit(1);
}

const buffer = fs.readFileSync(filePath);
const magic = buffer.readUInt32LE(0);
const version = buffer.readUInt32LE(4);
const length = buffer.readUInt32LE(8);
console.log(`GLB Magic: 0x${magic.toString(16)}, Version: ${version}, Length: ${length}`);

const chunkLength = buffer.readUInt32LE(12);
const chunkType = buffer.readUInt32LE(16);
const jsonBuffer = buffer.slice(20, 20 + chunkLength);
const gltf = JSON.parse(jsonBuffer.toString('utf8'));

console.log('Nodes count:', gltf.nodes ? gltf.nodes.length : 0);
if (gltf.nodes) {
  gltf.nodes.forEach((node, index) => {
    if (node.name && (node.name.toLowerCase().includes('hand') || node.name.toLowerCase().includes('arm') || node.name.toLowerCase().includes('weapon') || node.name.toLowerCase().includes('sword') || node.name.toLowerCase().includes('right'))) {
      console.log(`Node [${index}]: "${node.name}"${node.skin !== undefined ? ' (Skin)' : ''}${node.mesh !== undefined ? ' (Mesh)' : ''}`);
    }
  });
}
