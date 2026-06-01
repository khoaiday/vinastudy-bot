const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, '..', 'daiviet_defense', '3d_assets', 'custom', 'thanh_kiem.glb');
console.log('Reading file:', filePath);

if (!fs.existsSync(filePath)) {
  console.error('File does not exist!');
  process.exit(1);
}

const buffer = fs.readFileSync(filePath);

// Read GLB header
const magic = buffer.readUInt32LE(0);
const version = buffer.readUInt32LE(4);
const length = buffer.readUInt32LE(8);

console.log(`GLB Magic: 0x${magic.toString(16)}, Version: ${version}, Length: ${length}`);

if (magic !== 0x46546c67) {
  console.error('Not a valid GLB file!');
  process.exit(1);
}

// Read Chunk 0 (JSON)
const chunkLength = buffer.readUInt32LE(12);
const chunkType = buffer.readUInt32LE(16);

console.log(`Chunk 0 Length: ${chunkLength}, Type: 0x${chunkType.toString(16)}`);

if (chunkType !== 0x4e4f534a) {
  console.error('Chunk 0 is not JSON!');
  process.exit(1);
}

const jsonBuffer = buffer.slice(20, 20 + chunkLength);
const gltf = JSON.parse(jsonBuffer.toString('utf8'));

console.log('Successfully parsed GLTF JSON!');
console.log('Nodes count:', gltf.nodes ? gltf.nodes.length : 0);

if (gltf.nodes) {
  console.log('\n--- LIST OF ALL NODES (including Bones) ---');
  gltf.nodes.forEach((node, index) => {
    if (node.name) {
      console.log(`Node [${index}]: "${node.name}"${node.skin !== undefined ? ' (Skin)' : ''}${node.mesh !== undefined ? ' (Mesh)' : ''}`);
    }
  });
} else {
  console.log('No nodes found!');
}
