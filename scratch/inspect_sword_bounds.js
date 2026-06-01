const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, '..', 'daiviet_defense', '3d_assets', 'custom', 'thanh_kiem.glb');

const buffer = fs.readFileSync(filePath);
const chunkLength = buffer.readUInt32LE(12);
const jsonBuffer = buffer.slice(20, 20 + chunkLength);
const gltf = JSON.parse(jsonBuffer.toString('utf8'));

const mesh = gltf.meshes[0];
const prim = mesh.primitives[0];
const posAccessorIndex = prim.attributes.POSITION;
const accessor = gltf.accessors[posAccessorIndex];

console.log('POSITION Accessor:', JSON.stringify(accessor, null, 2));
