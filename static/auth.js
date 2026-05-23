/**
 * VInaStudy Auth Gate
 * Include sau telegram-web-app.js trong mọi content/game file.
 * Kiểm tra tài khoản approved trước khi cho phép chơi.
 */
(function () {
  var tg = window.Telegram && window.Telegram.WebApp;
  var tgId = tg && tg.initDataUnsafe && tg.initDataUnsafe.user && tg.initDataUnsafe.user.id;

  // Không mở từ Telegram (browser/dev) → cho qua
  if (!tgId) return;

  // Tạo overlay chặn nội dung game trong khi kiểm tra quyền truy cập
  var ov = document.createElement('div');
  ov.style.cssText = [
    'position:fixed', 'inset:0', 'background:#050a1f',
    'z-index:99999', 'display:flex', 'flex-direction:column',
    'align-items:center', 'justify-content:center', 'gap:12px'
  ].join(';');
  ov.innerHTML =
    '<div style="font-size:36px;animation:_spin 1.2s linear infinite">⚙️</div>' +
    '<div style="color:rgba(10,224,254,.8);font-size:14px;font-family:sans-serif">Đang xác thực...</div>' +
    '<style>@keyframes _spin{to{transform:rotate(360deg)}}</style>';
  document.body.appendChild(ov);

  fetch('/api/student/tg-status?tg_id=' + tgId)
    .then(function (res) { return res.json(); })
    .then(function (data) {
      if (data.status !== 'approved') {
        // Pending, rejected, not_found → về trang đăng ký
        window.location.replace('/register?tg_id=' + tgId);
      } else {
        // Đã xác thực → xóa overlay, cho vào game
        ov.remove();
      }
    })
    .catch(function () {
      // Lỗi mạng → fail open, không chặn học sinh
      ov.remove();
    });
})();
