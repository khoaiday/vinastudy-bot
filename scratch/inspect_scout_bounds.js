const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, '..', 'daiviet_defense', '3d_assets', 'custom', 'enemy_scout.glb');

const buffer = fs.readFileSync(filePath);
const chunkLength = buffer.readUInt32LE(12);
const jsonBuffer = buffer.slice(20, 20 + chunkLength);
const gltf = JSON.parse(jsonBuffer.toString('utf8'));

if (gltf.meshes) {
  gltf.meshes.forEach((mesh, index) => {
    console.log(`Mesh [${index}]: name="${mesh.name}"`);
    if (mesh.primitives) {
      mesh.primitives.forEach((prim, pIndex) => {
        const posAccessorIndex = prim.attributes.POSITION;
        const accessor = gltf.accessors[posAccessorIndex];
        console.log(`  Primitive [${pIndex}] POSITION:`, JSON.stringify(accessor));
      });
    }
  });
}
