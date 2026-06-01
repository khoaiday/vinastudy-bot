/**
 * asset_gen.js — Đại Việt Defense Asset Generation Pipeline
 * Kết nối Leonardo.ai + Tripo3D API để tự động tạo game assets
 *
 * Usage:
 *   node asset_gen.js                    — generate tất cả assets chưa có
 *   node asset_gen.js --type towers_2d   — chỉ generate tower icons
 *   node asset_gen.js --type towers_3d   — chỉ generate 3D models (Tripo)
 *   node asset_gen.js --type ui_2d       — chỉ generate UI
 *   node asset_gen.js --type enemies_2d  — chỉ generate enemy sprites
 *   node asset_gen.js --id arrow_tower_icon — generate 1 asset cụ thể
 *   node asset_gen.js --force            — regenerate kể cả đã có file
 *   node asset_gen.js --list             — liệt kê tất cả assets cần gen
 */

'use strict';

const fs   = require('fs');
const path = require('path');
const https = require('https');

// ── Load .env ──────────────────────────────────────────────────────────────────
const envPath = path.join(__dirname, '.env');
const env = {};
if (fs.existsSync(envPath)) {
  fs.readFileSync(envPath, 'utf8').split('\n').forEach(line => {
    const [k, ...v] = line.split('=');
    if (k && !k.startsWith('#')) env[k.trim()] = v.join('=').trim();
  });
}

const LEONARDO_KEY = env.LEONARDO_API_KEY || process.env.LEONARDO_API_KEY;
const MESHY_KEY    = env.MESHY_API_KEY    || process.env.MESHY_API_KEY;

// ── Paths ──────────────────────────────────────────────────────────────────────
const ROOT     = path.resolve(__dirname, '../..');
const PROMPTS  = JSON.parse(fs.readFileSync(path.join(__dirname, 'prompts.json'), 'utf8'));

// ── CLI args ───────────────────────────────────────────────────────────────────
const args   = process.argv.slice(2);
const typeFilter  = args.includes('--type')  ? args[args.indexOf('--type')  + 1] : null;
const idFilter    = args.includes('--id')    ? args[args.indexOf('--id')    + 1] : null;
const force       = args.includes('--force');
const listOnly    = args.includes('--list');

// ── Collect all tasks ──────────────────────────────────────────────────────────
const allCategories = Object.keys(PROMPTS);
const tasks = [];
for (const cat of allCategories) {
  if (cat.startsWith('_')) continue; // skip style anchor keys
  if (typeFilter && cat !== typeFilter) continue;
  if (!Array.isArray(PROMPTS[cat])) continue;
  for (const item of PROMPTS[cat]) {
    if (idFilter && item.id !== idFilter) continue;
    tasks.push({ ...item, category: cat });
  }
}

if (listOnly) {
  console.log('\n📋 ASSET LIST:\n');
  for (const t of tasks) {
    const destAbs = path.join(ROOT, t.dest);
    const exists  = fs.existsSync(destAbs) ? '✅' : '❌';
    console.log(`  ${exists}  [${t.api.toUpperCase().padEnd(8)}]  ${t.id}`);
    console.log(`            → ${t.dest}\n`);
  }
  console.log(`Total: ${tasks.length} assets`);
  process.exit(0);
}

// ── HTTP helpers ───────────────────────────────────────────────────────────────
function httpRequest(options, body = null) {
  return new Promise((resolve, reject) => {
    const req = https.request(options, res => {
      const chunks = [];
      res.on('data', d => chunks.push(d));
      res.on('end', () => {
        const raw = Buffer.concat(chunks).toString();
        try { resolve({ status: res.statusCode, body: JSON.parse(raw) }); }
        catch { resolve({ status: res.statusCode, body: raw }); }
      });
    });
    req.on('error', reject);
    if (body) req.write(typeof body === 'string' ? body : JSON.stringify(body));
    req.end();
  });
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function downloadFile(url, dest) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(dest);
    https.get(url, res => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        file.close();
        downloadFile(res.headers.location, dest).then(resolve).catch(reject);
        return;
      }
      res.pipe(file);
      file.on('finish', () => { file.close(); resolve(); });
    }).on('error', err => { fs.unlink(dest, () => {}); reject(err); });
  });
}

// ── Leonardo.ai API ────────────────────────────────────────────────────────────
// Docs: https://docs.leonardo.ai/reference/creategeneration
const LEONARDO_MODELS = {
  phoenix: 'de7d3faf-762f-48e0-b3b7-9d0ac3a3fcf3',  // Leonardo Phoenix 1.0
  kino:    'aa77f04e-3eec-4034-9c07-d0f619684628',   // Leonardo Kino XL
  vision:  '5c232a9e-9061-4777-980a-ddc8e65647c6',  // Leonardo Vision XL
};

async function leonardoGenerate(task) {
  if (!LEONARDO_KEY || LEONARDO_KEY === 'your_leonardo_key_here') {
    throw new Error('LEONARDO_API_KEY chưa được set trong .env');
  }

  const modelId = LEONARDO_MODELS[task.model] || LEONARDO_MODELS.phoenix;

  // ── Upload reference image if task has image_ref ──
  let imagePrompts = undefined;
  if (task.image_ref) {
    const refPath = path.join(ROOT, task.image_ref);
    if (fs.existsSync(refPath)) {
      try {
        // Step 1: Get presigned upload URL
        const initRes = await httpRequest({
          hostname: 'cloud.leonardo.ai',
          path: '/api/rest/v1/init-image',
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${LEONARDO_KEY}` }
        }, { extension: path.extname(refPath).replace('.','') });

        const uploadUrl = initRes.body?.uploadInitImage?.url;
        const fields    = initRes.body?.uploadInitImage?.fields;
        const imageId   = initRes.body?.uploadInitImage?.id;

        if (uploadUrl && fields && imageId) {
          // Step 2: Upload image via multipart POST (S3)
          const imgData = fs.readFileSync(refPath);
          const boundary = '----LeonardoBoundary' + Date.now();
          let formBody = '';
          const fieldsObj = typeof fields === 'string' ? JSON.parse(fields) : fields;
          for (const [k,v] of Object.entries(fieldsObj)) {
            formBody += `--${boundary}\r\nContent-Disposition: form-data; name="${k}"\r\n\r\n${v}\r\n`;
          }
          formBody += `--${boundary}\r\nContent-Disposition: form-data; name="file"; filename="${path.basename(refPath)}"\r\nContent-Type: image/png\r\n\r\n`;
          const formEnd = `\r\n--${boundary}--\r\n`;
          const uploadUrl2 = new URL(uploadUrl);
          await new Promise((res, rej) => {
            const req = https.request({ hostname: uploadUrl2.hostname, path: uploadUrl2.pathname + uploadUrl2.search, method: 'POST',
              headers: { 'Content-Type': `multipart/form-data; boundary=${boundary}`, 'Content-Length': Buffer.byteLength(formBody) + imgData.length + Buffer.byteLength(formEnd) }
            }, r => { r.resume(); r.on('end', res); });
            req.write(formBody); req.write(imgData); req.write(formEnd); req.end();
            req.on('error', rej);
          });
          imagePrompts = [{ id: imageId, weight: task.image_ref_weight || 0.5 }];
          console.log(`  📎 Image reference uploaded: ${imageId}`);
        }
      } catch(e) { console.warn(`  ⚠️  Image ref upload failed: ${e.message}`); }
    }
  }

  console.log(`  🎨 [Leonardo] Generating ${task.id}...`);

  // Step 1: Create generation
  const genRes = await httpRequest({
    hostname: 'cloud.leonardo.ai',
    path: '/api/rest/v1/generations',
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${LEONARDO_KEY}`,
    }
  }, {
    modelId,
    prompt: (task.skip_style_anchor ? '' : (PROMPTS._style_anchor ? PROMPTS._style_anchor + '. ' : '')) + task.prompt,
    negative_prompt: (PROMPTS._style_negative ? PROMPTS._style_negative + ', ' : '') + (task.negative || ''),
    width:  task.width  || 512,
    height: task.height || 512,
    num_images: task.num_images || 4,
    guidance_scale: task.guidance || 7,
    alchemy: true,
    photoReal: false,
    transparency: 'disabled',
    ...(imagePrompts ? { imagePrompts } : {}),
  });

  if (genRes.status !== 200) {
    throw new Error(`Leonardo API error ${genRes.status}: ${JSON.stringify(genRes.body)}`);
  }

  const genId = genRes.body?.sdGenerationJob?.generationId;
  if (!genId) throw new Error('No generationId in response');

  console.log(`  ⏳ [Leonardo] Waiting for ${task.id} (id: ${genId})...`);

  // Step 2: Poll until done
  for (let i = 0; i < 30; i++) {
    await sleep(3000);
    const pollRes = await httpRequest({
      hostname: 'cloud.leonardo.ai',
      path: `/api/rest/v1/generations/${genId}`,
      method: 'GET',
      headers: { 'Authorization': `Bearer ${LEONARDO_KEY}` }
    });

    const gen = pollRes.body?.generations_by_pk;
    if (!gen) continue;
    if (gen.status === 'COMPLETE') {
      const imgs = gen.generated_images || [];
      if (!imgs.length) throw new Error('No image URL in response');
      // Return all URLs for multi-variant review
      return imgs.map(i => i.url);
    }
    if (gen.status === 'FAILED') throw new Error('Generation FAILED');
    process.stdout.write('.');
  }
  throw new Error('Leonardo timeout after 90s');
}

// ── Meshy.ai API ──────────────────────────────────────────────────────────────
// Docs: https://docs.meshy.ai/en/api
async function meshyGenerate(task) {
  if (!MESHY_KEY) throw new Error('MESHY_API_KEY chưa được set trong .env');

  console.log(`  🧊 [Meshy] Generating ${task.id}...`);

  // Step 1: Create text-to-3D task (preview stage)
  const createRes = await httpRequest({
    hostname: 'api.meshy.ai',
    path: '/openapi/v2/text-to-3d',
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${MESHY_KEY}`,
    }
  }, {
    mode: 'preview',
    prompt: task.prompt,
    art_style: 'realistic',
    negative_prompt: 'low quality, blurry, duplicate, ugly',
  });

  if (createRes.status !== 202) {
    throw new Error(`Meshy API error ${createRes.status}: ${JSON.stringify(createRes.body)}`);
  }

  const taskId = createRes.body?.result;
  if (!taskId) throw new Error('No task ID from Meshy');
  console.log(`  ⏳ [Meshy] Task ${taskId} — waiting preview...`);

  // Step 2: Poll preview
  let modelUrl = null;
  for (let i = 0; i < 60; i++) {
    await sleep(5000);
    const poll = await httpRequest({
      hostname: 'api.meshy.ai',
      path: `/openapi/v2/text-to-3d/${taskId}`,
      method: 'GET',
      headers: { 'Authorization': `Bearer ${MESHY_KEY}` }
    });
    const status   = poll.body?.status;
    const progress = poll.body?.progress_percentage || 0;
    process.stdout.write(`\r  ⏳ [Meshy] ${task.id}: ${status} ${progress}%   `);
    if (status === 'SUCCEEDED') {
      modelUrl = poll.body?.model_urls?.glb;
      if (!modelUrl) throw new Error('No GLB URL in Meshy response');
      console.log('');
      break;
    }
    if (status === 'FAILED') throw new Error(`Meshy task FAILED: ${JSON.stringify(poll.body?.task_error)}`);
  }
  if (!modelUrl) throw new Error('Meshy preview timeout');

  // Step 3: Refine (adds textures) — costs 10 more credits
  const refineRes = await httpRequest({
    hostname: 'api.meshy.ai',
    path: '/openapi/v2/text-to-3d',
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${MESHY_KEY}` }
  }, { mode: 'refine', preview_task_id: taskId });

  if (refineRes.status === 202) {
    const refineId = refineRes.body?.result;
    console.log(`  ✨ [Meshy] Refining textures (${refineId})...`);
    for (let i = 0; i < 60; i++) {
      await sleep(5000);
      const rp = await httpRequest({
        hostname: 'api.meshy.ai',
        path: `/openapi/v2/text-to-3d/${refineId}`,
        method: 'GET',
        headers: { 'Authorization': `Bearer ${MESHY_KEY}` }
      });
      const rs = rp.body?.status;
      const rp2 = rp.body?.progress_percentage || 0;
      process.stdout.write(`\r  ✨ [Meshy] Refine: ${rs} ${rp2}%   `);
      if (rs === 'SUCCEEDED') {
        const refined = rp.body?.model_urls?.glb;
        if (refined) { modelUrl = refined; }
        console.log('');
        break;
      }
      if (rs === 'FAILED') { console.log('\n  ⚠️  Refine failed, using preview model'); break; }
    }
  }

  return modelUrl;
}

// ── Meshy Image-to-3D ──────────────────────────────────────────────────────────
async function meshyImageTo3D(task) {
  if (!MESHY_KEY) throw new Error('MESHY_API_KEY not set');
  console.log(`  🧊 [Meshy Image-to-3D] ${task.id}...`);

  // Upload image to get public URL first (use Leonardo upload or base64)
  const imgPath = path.join(ROOT, task.image_ref);
  if (!fs.existsSync(imgPath)) throw new Error(`Image not found: ${imgPath}`);
  const imgBase64 = fs.readFileSync(imgPath).toString('base64');
  const ext = path.extname(imgPath).replace('.','').toLowerCase();
  const dataUrl = `data:image/${ext};base64,${imgBase64}`;

  // Step 1: Create image-to-3D task
  const createRes = await httpRequest({
    hostname: 'api.meshy.ai',
    path: '/openapi/v1/image-to-3d',
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${MESHY_KEY}` }
  }, {
    image_url: dataUrl,
    ai_model: 'meshy-6',
  });

  if (createRes.status !== 202) throw new Error(`Meshy img-to-3d error ${createRes.status}: ${JSON.stringify(createRes.body)}`);
  const taskId = createRes.body?.result;
  if (!taskId) throw new Error('No task ID');
  console.log(`  ⏳ Task ${taskId} — processing...`);

  // Step 2: Poll until done
  for (let i = 0; i < 120; i++) {
    await sleep(5000);
    const poll = await httpRequest({
      hostname: 'api.meshy.ai',
      path: `/openapi/v1/image-to-3d/${taskId}`,
      method: 'GET',
      headers: { 'Authorization': `Bearer ${MESHY_KEY}` }
    });
    const st = poll.body?.status;
    const pct = poll.body?.progress_percentage || 0;
    process.stdout.write(`\r  ⏳ [Meshy] ${st} ${pct}%   `);
    if (st === 'SUCCEEDED') {
      const glbUrl = poll.body?.model_urls?.glb;
      if (!glbUrl) throw new Error('No GLB URL');
      console.log(`\n  ✅ Done: ${glbUrl}`);
      return glbUrl;
    }
    if (st === 'FAILED') throw new Error(`FAILED: ${JSON.stringify(poll.body?.task_error)}`);
  }
  throw new Error('Meshy image-to-3D timeout');
}

// ── Main ───────────────────────────────────────────────────────────────────────
(async function main() {
  console.log('\n🎮 ĐẠI VIỆT DEFENSE — Asset Generation Pipeline');
  console.log('='.repeat(55));
  console.log(`📦 Tasks to run: ${tasks.length}`);
  console.log(`🔑 Leonardo: ${LEONARDO_KEY ? '✅ Key found' : '❌ MISSING (.env)'}`);
  console.log(`🔑 Meshy:    ${MESHY_KEY    ? '✅ Key found' : '❌ MISSING (.env)'}`);
  console.log('');

  let generated = 0, skipped = 0, failed = 0;

  for (const task of tasks) {
    const destAbs = path.join(ROOT, task.dest);
    const destDir = path.dirname(destAbs);

    // Skip if already exists and not --force
    if (!force && fs.existsSync(destAbs)) {
      console.log(`  ⏭️  SKIP (exists): ${task.id}`);
      skipped++;
      continue;
    }

    fs.mkdirSync(destDir, { recursive: true });

    try {
      let url;
      if (task.api === 'leonardo') {
        url = await leonardoGenerate(task);
      } else if (task.api === 'meshy') {
        url = await meshyGenerate(task);
      } else if (task.api === 'meshy_image') {
        url = await meshyImageTo3D(task);
      } else {
        throw new Error(`Unknown API: ${task.api}`);
      }

      console.log(`\n  ⬇️  Downloading ${task.id}...`);
      // Handle multiple variants (4 options for review)
      const urls = Array.isArray(url) ? url : [url];
      const ext = path.extname(destAbs) || '.png';
      const base = destAbs.replace(ext, '');
      for (let i = 0; i < urls.length; i++) {
        const varPath = urls.length === 1 ? destAbs : `${base}_v${i+1}${ext}`;
        await downloadFile(urls[i], varPath);
        console.log(`  ✅  Saved: ${varPath}`);
      }
      generated++;

    } catch (err) {
      console.error(`\n  ❌  FAILED ${task.id}: ${err.message}`);
      failed++;
    }

    // Rate limit: 2s between requests
    await sleep(2000);
  }

  // ── Summary ────────────────────────────────────────────────────────────────
  console.log('\n' + '='.repeat(55));
  console.log(`✅ Generated : ${generated}`);
  console.log(`⏭️  Skipped   : ${skipped} (already exist)`);
  console.log(`❌ Failed    : ${failed}`);
  console.log('');

  if (generated > 0) {
    console.log('💡 Next: Check generated assets trong thư mục game.');
    console.log('   Chạy git add + commit để đưa assets vào Railway.\n');
  }
})();
