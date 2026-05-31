/**
 * VInaStudy Auto-Pipeline Daemon
 * 
 * Watch dev branch → detect new commits → check → merge main → push → wait deploy → test online
 * Chỉ báo cáo khi có vấn đề. Im lặng khi mọi thứ ổn.
 */

const { execSync, exec } = require("child_process");
const https = require("https");
const http = require("http");
const fs = require("fs");
const path = require("path");
const readline = require("readline");

// ── CONFIG ──────────────────────────────────────────────────────────────────
const ROOT = path.resolve(__dirname, "..");
const LOG_FILE = path.join(__dirname, "pipeline_log.md");
const ALERT_FILE = path.join(ROOT, "PIPELINE_ALERT.md");
const CONFIG_FILE = path.join(__dirname, "pipeline.config");

// Đọc pipeline.config
function readConfig() {
  const defaults = {
    PROD_URL: "",
    WATCH_BRANCH: "dev",
    DEPLOY_BRANCH: "main",
    DEPLOY_WAIT_SECONDS: "90",
    POLL_INTERVAL_SECONDS: "15",
  };
  try {
    const content = fs.readFileSync(CONFIG_FILE, "utf-8");
    for (const line of content.split("\n")) {
      const [k, ...rest] = line.split("=");
      if (k && rest.length && !k.trim().startsWith("#")) {
        defaults[k.trim()] = rest.join("=").trim();
      }
    }
  } catch {}
  // Auto-detect PROD_URL nếu chưa set
  if (!defaults.PROD_URL || defaults.PROD_URL.includes("vinastudy-bot-production")) {
    defaults.PROD_URL = detectProdUrl();
  }
  return defaults;
}

function detectProdUrl() {
  // Thử đọc từ .env
  try {
    const envContent = fs.readFileSync(path.join(ROOT, ".env"), "utf-8");
    const match = envContent.match(/BASE_DOMAIN=(.+)/);
    if (match && match[1] && !match[1].includes("localhost")) return match[1].trim();
  } catch {}
  return "https://vinastudy-bot-production.up.railway.app";
}

const CFG = readConfig();
const PROD_URL = CFG.PROD_URL;
const WATCH_BRANCH = CFG.WATCH_BRANCH;
const DEPLOY_BRANCH = CFG.DEPLOY_BRANCH;
const POLL_INTERVAL_MS = parseInt(CFG.POLL_INTERVAL_SECONDS) * 1000;
const DEPLOY_WAIT_MS = parseInt(CFG.DEPLOY_WAIT_SECONDS) * 1000;

// ── ENDPOINTS cần test sau deploy ────────────────────────────────────────────
// Format: { path, expectedStatus, description, checkFn? }
const TEST_SUITE = [
  { path: "/health",        expectedStatus: 200, desc: "Health check API" },
  { path: "/",              expectedStatus: 200, desc: "Trang chủ (intro.html)" },
  { path: "/register",      expectedStatus: 200, desc: "Trang đăng ký" },
  { path: "/map",           expectedStatus: 200, desc: "Bản đồ chiến dịch" },
  { path: "/battle.html",   expectedStatus: 200, desc: "Màn chiến đấu" },
  { path: "/tower_defense", expectedStatus: 200, desc: "Tower Defense" },
  { path: "/minigame.html", expectedStatus: 200, desc: "Minigame Tuyệt Chiêu 1" },
  { path: "/leaderboard",   expectedStatus: 200, desc: "Bảng xếp hạng" },
  { path: "/admin",         expectedStatus: 200, desc: "Admin dashboard" },
  { path: "/nonexistent-page-xyz", expectedStatus: 404, desc: "404 handler" },
];

// ── STATE ─────────────────────────────────────────────────────────────────────
let lastKnownHash = null;
let pipelineRunning = false;
let _resolvedProdUrl = PROD_URL; // sẽ được cập nhật sau khi xác nhận URL

function getProdUrl() { return _resolvedProdUrl; }

// ── HELPERS ──────────────────────────────────────────────────────────────────
function git(cmd, opts = {}) {
  return execSync(`git ${cmd}`, { cwd: ROOT, encoding: "utf-8", ...opts }).trim();
}

function log(msg, level = "INFO") {
  const ts = new Date().toISOString().slice(0, 19).replace("T", " ");
  const line = `[${ts}] [${level}] ${msg}`;
  console.log(line);
  try {
    fs.appendFileSync(LOG_FILE, line + "\n");
  } catch {}
}

function fetchUrl(url, timeoutMs = 15000) {
  return new Promise((resolve) => {
    const lib = url.startsWith("https") ? https : http;
    const req = lib.get(url, { timeout: timeoutMs }, (res) => {
      let body = "";
      res.on("data", (d) => (body += d));
      res.on("end", () =>
        resolve({ ok: true, status: res.statusCode, body: body.slice(0, 500) })
      );
    });
    req.on("error", (e) => resolve({ ok: false, error: e.message }));
    req.on("timeout", () => { req.destroy(); resolve({ ok: false, error: "timeout" }); });
  });
}

function sendWindowsNotification(title, body) {
  try {
    const escaped = body.replace(/'/g, "''");
    execSync(
      `powershell -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('${escaped}', '${title}', 'OK', 'Warning')"`,
      { timeout: 5000, stdio: "ignore" }
    );
  } catch {}
}

function writeAlert(title, details) {
  const ts = new Date().toLocaleString("vi-VN");
  const content = `# ⚠️ PIPELINE ALERT — ${ts}\n\n## ${title}\n\n${details}\n\n---\n`;
  fs.writeFileSync(ALERT_FILE, content);
  log(`ALERT written: ${title}`, "WARN");
  sendWindowsNotification(`🤖 Pipeline Alert`, title);
}

function clearAlert() {
  if (fs.existsSync(ALERT_FILE)) fs.unlinkSync(ALERT_FILE);
}

// ── GIT OPERATIONS ───────────────────────────────────────────────────────────
function getCurrentHash(branch = "dev") {
  try {
    return git(`rev-parse ${branch}`);
  } catch {
    return null;
  }
}

function getLatestCommitInfo() {
  try {
    return git('log -1 --format="%h|%s|%an|%ar" dev');
  } catch {
    return "unknown";
  }
}

function getDiffSummary() {
  try {
    const diff = git("diff HEAD~1 HEAD --stat --no-color");
    return diff.slice(0, 500);
  } catch {
    return "(không lấy được diff)";
  }
}

function checkSyntaxErrors() {
  // Kiểm tra JS files thay đổi gần đây
  const errors = [];
  try {
    const changedFiles = git("diff HEAD~1 HEAD --name-only").split("\n").filter(Boolean);
    for (const file of changedFiles) {
      const fullPath = path.join(ROOT, file);
      if (!fs.existsSync(fullPath)) continue;

      if (file.endsWith(".js") && !file.includes("node_modules")) {
        try {
          execSync(`node --check "${fullPath}"`, { timeout: 5000, stdio: "pipe" });
        } catch (e) {
          errors.push(`❌ JS syntax error: ${file}\n   ${e.stderr?.toString().slice(0, 200)}`);
        }
      }

      if (file.endsWith(".json")) {
        try {
          JSON.parse(fs.readFileSync(fullPath, "utf-8"));
        } catch (e) {
          errors.push(`❌ JSON invalid: ${file} — ${e.message}`);
        }
      }
    }
  } catch {}
  return errors;
}

function mergeAndPush() {
  // Đảm bảo đang ở WATCH_BRANCH, pull mới nhất
  git(`checkout ${WATCH_BRANCH}`);
  git(`pull origin ${WATCH_BRANCH}`);

  // Merge WATCH → DEPLOY
  git(`checkout ${DEPLOY_BRANCH}`);
  git(`pull origin ${DEPLOY_BRANCH}`);
  git(`merge ${WATCH_BRANCH} --no-edit`);

  // Push deploy branch → Railway deploy
  git(`push origin ${DEPLOY_BRANCH}`);

  // Quay lại watch branch
  git(`checkout ${WATCH_BRANCH}`);
}

// ── ONLINE TESTING ───────────────────────────────────────────────────────────
async function waitForDeploy(targetHash) {
  log(`⏳ Chờ Railway deploy (${DEPLOY_WAIT_MS / 1000}s)...`);

  // Chờ server restart: /health trả về OK + header X-Commit mới (nếu có)
  // Nếu không có custom header, chỉ poll cho đến khi /health OK sau khoảng chờ
  await sleep(DEPLOY_WAIT_MS);
  log("⏳ Deploy wait xong, bắt đầu test...");
}

async function runOnlineTests() {
  const results = [];
  let failCount = 0;

  log(`🧪 Testing ${TEST_SUITE.length} endpoints trên ${getProdUrl()}...`);

  for (const test of TEST_SUITE) {
    const url = getProdUrl() + test.path;
    const res = await fetchUrl(url);

    const pass =
      res.ok &&
      res.status === test.expectedStatus;

    results.push({
      ...test,
      url,
      actual: res.ok ? res.status : `ERR: ${res.error}`,
      pass,
    });

    if (!pass) failCount++;

    const icon = pass ? "✅" : "❌";
    log(`${icon} [${res.ok ? res.status : "ERR"}] ${test.desc} → ${url}`);

    // Nhỏ delay giữa requests
    await sleep(500);
  }

  return { results, failCount, totalTests: TEST_SUITE.length };
}

function formatTestReport(commitInfo, diff, testResult, durationMs) {
  const { results, failCount, totalTests } = testResult;
  const ts = new Date().toLocaleString("vi-VN");
  const [hash, subject, author, timeAgo] = commitInfo.split("|");
  const passCount = totalTests - failCount;

  let report = `## Pipeline Run — ${ts}\n\n`;
  report += `**Commit:** \`${hash}\` — ${subject} (${author}, ${timeAgo})\n\n`;
  report += `**Result:** ${failCount === 0 ? "✅ ALL PASS" : `❌ ${failCount}/${totalTests} FAILED`} (${Math.round(durationMs / 1000)}s total)\n\n`;

  if (failCount > 0) {
    report += `### ❌ Tests thất bại:\n`;
    for (const r of results.filter((r) => !r.pass)) {
      report += `- **${r.desc}** — expected ${r.expectedStatus}, got ${r.actual}\n  ${r.url}\n`;
    }
    report += "\n";
  }

  report += `<details><summary>📋 Tất cả ${totalTests} tests</summary>\n\n`;
  for (const r of results) {
    report += `- ${r.pass ? "✅" : "❌"} \`${r.actual}\` ${r.desc}\n`;
  }
  report += `\n</details>\n\n`;
  report += `**Diff:**\n\`\`\`\n${diff}\n\`\`\`\n\n---\n\n`;

  return report;
}

function appendToLog(content) {
  const header = fs.existsSync(LOG_FILE) ? "" : "# VInaStudy Pipeline Log\n\n";
  fs.writeFileSync(LOG_FILE, header + content + (fs.existsSync(LOG_FILE) ? fs.readFileSync(LOG_FILE, "utf-8") : ""));
}

// ── PIPELINE CORE ────────────────────────────────────────────────────────────
async function runPipeline(newHash) {
  const startTime = Date.now();
  const commitInfo = getLatestCommitInfo();
  const diff = getDiffSummary();

  log(`🚀 Pipeline bắt đầu — commit: ${newHash.slice(0, 7)}`);
  log(`   ${commitInfo}`);

  // STEP 1: Syntax check
  const syntaxErrors = checkSyntaxErrors();
  if (syntaxErrors.length > 0) {
    const errMsg = syntaxErrors.join("\n");
    log(`❌ Syntax errors detected:\n${errMsg}`, "ERROR");
    writeAlert("Syntax Errors — Deploy bị chặn", errMsg + `\n\nCommit: ${commitInfo}`);
    appendToLog(`## ❌ Syntax Error — ${new Date().toLocaleString("vi-VN")}\n\n${errMsg}\n\n---\n\n`);
    return;
  }

  // STEP 2: Merge dev → main → push
  log("🔀 Merging dev → main → push...");
  try {
    mergeAndPush();
    log("✅ Push to main thành công — Railway đang deploy...");
  } catch (e) {
    const errMsg = e.message || String(e);
    log(`❌ Git merge/push thất bại: ${errMsg}`, "ERROR");
    writeAlert("Git Push Thất Bại", errMsg + `\n\nCommit: ${commitInfo}`);
    // Khôi phục về dev
    try { git("checkout dev"); } catch {}
    return;
  }

  // STEP 3: Chờ deploy
  await waitForDeploy(newHash);

  // STEP 4: Test online
  let testResult;
  try {
    testResult = await runOnlineTests();
  } catch (e) {
    writeAlert("Test Runner Lỗi", String(e));
    return;
  }

  const duration = Date.now() - startTime;

  // STEP 5: Ghi log + alert nếu cần
  const report = formatTestReport(commitInfo, diff, testResult, duration);
  appendToLog(report);

  if (testResult.failCount > 0) {
    const failedTests = testResult.results
      .filter((r) => !r.pass)
      .map((r) => `• ${r.desc}: expected ${r.expectedStatus}, got ${r.actual}`)
      .join("\n");

    writeAlert(
      `${testResult.failCount} tính năng bị lỗi sau deploy`,
      `Commit: ${commitInfo}\n\nTests thất bại:\n${failedTests}\n\nXem chi tiết: pipeline/pipeline_log.md`
    );
  } else {
    clearAlert();
    log(`✅ DONE — ${testResult.totalTests}/${testResult.totalTests} tests pass (${Math.round(duration / 1000)}s)`);
  }
}

// ── MAIN LOOP ─────────────────────────────────────────────────────────────────
function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

async function tick() {
  if (pipelineRunning) return;

  try {
    // Fetch remote WATCH_BRANCH để cập nhật
    git(`fetch origin ${WATCH_BRANCH} --quiet`);
    const remoteHash = git(`rev-parse origin/${WATCH_BRANCH}`);

    if (lastKnownHash === null) {
      // Khởi động lần đầu — lưu hash hiện tại, không chạy
      lastKnownHash = remoteHash;
      log(`🟢 Pipeline started. Watching [${WATCH_BRANCH}] → deploy [${DEPLOY_BRANCH}] (${remoteHash.slice(0, 7)})`);
      log(`   Production URL: ${PROD_URL}`);
      return;
    }

    if (remoteHash !== lastKnownHash) {
      log(`🔔 Commit mới phát hiện: ${lastKnownHash.slice(0, 7)} → ${remoteHash.slice(0, 7)}`);
      lastKnownHash = remoteHash;
      pipelineRunning = true;
      try {
        await runPipeline(remoteHash);
      } finally {
        pipelineRunning = false;
      }
    }
  } catch (e) {
    log(`⚠️ Tick error: ${e.message}`, "WARN");
  }
}

async function main() {
  console.log("╔══════════════════════════════════════════════════╗");
  console.log("║   VInaStudy Auto-Pipeline Daemon                ║");
  console.log("║   Claude Code commit → Test → Deploy → Verify  ║");
  console.log("╚══════════════════════════════════════════════════╝");
  console.log(`   Root:   ${ROOT}`);
  console.log(`   Watch:  ${WATCH_BRANCH} → ${DEPLOY_BRANCH}`);
  console.log(`   Poll:   every ${POLL_INTERVAL_MS / 1000}s | Deploy wait: ${DEPLOY_WAIT_MS / 1000}s\n`);

  // Xác nhận PROD_URL — test /health
  let prodUrl = PROD_URL;
  const testResult = await fetchUrl(prodUrl + "/health", 8000);
  if (!testResult.ok || testResult.status === 404) {
    // URL không đúng — hỏi 1 lần
    console.log(`⚠️  Không kết nối được: ${prodUrl}`);
    console.log(`   (status: ${testResult.ok ? testResult.status : testResult.error})`);
    console.log();
    prodUrl = await askOnce("   Nhập Railway URL của bạn (vd: https://abc.railway.app): ");
    prodUrl = prodUrl.trim().replace(/\/$/, "");
    // Lưu vào config để không hỏi lại
    saveProdUrl(prodUrl);
  }

  // Override với URL đã xác nhận
  _resolvedProdUrl = prodUrl;
  console.log(`   Prod:   ${prodUrl} ✅`);
  console.log();

  // Khởi tạo log file nếu chưa có
  if (!fs.existsSync(LOG_FILE)) {
    fs.writeFileSync(LOG_FILE, "# VInaStudy Pipeline Log\n\n");
  }

  // Main loop
  await tick();
  setInterval(tick, POLL_INTERVAL_MS);
}

function askOnce(prompt) {
  return new Promise((resolve) => {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    rl.question(prompt, (ans) => { rl.close(); resolve(ans); });
  });
}

function saveProdUrl(url) {
  try {
    let content = fs.readFileSync(CONFIG_FILE, "utf-8");
    content = content.replace(/^PROD_URL=.*/m, `PROD_URL=${url}`);
    fs.writeFileSync(CONFIG_FILE, content);
    console.log(`   ✅ Đã lưu vào pipeline/pipeline.config`);
  } catch (e) {
    console.log(`   ⚠️ Không lưu được config: ${e.message}`);
  }
}

main().catch((e) => {
  console.error("Fatal:", e);
  process.exit(1);
});
