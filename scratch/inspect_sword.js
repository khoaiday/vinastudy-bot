const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, '..', 'daiviet_defense', '3d_assets', 'custom', 'thanh_kiem.glb');
console.log('Reading file:', filePath);

const buffer = fs.readFileSync(filePath);
const chunkLength = buffer.readUInt32LE(12);
const jsonBuffer = buffer.slice(20, 20 + chunkLength);
const gltf = JSON.parse(jsonBuffer.toString('utf8'));

console.log('Nodes count:', gltf.nodes ? gltf.nodes.length : 0);
if (gltf.nodes) {
  gltf.nodes.forEach((node, index) => {
    console.log(`Node [${index}]: name="${node.name}", translation=${JSON.stringify(node.translation)}, rotation=${JSON.stringify(node.rotation)}, scale=${JSON.stringify(node.scale)}, mesh=${node.mesh}`);
  });
}
if (gltf.meshes) {
  gltf.meshes.forEach((mesh, index) => {
    console.log(`Mesh [${index}]: name="${mesh.name}", primitives count=${mesh.primitives ? mesh.primitives.length : 0}`);
  });
}
