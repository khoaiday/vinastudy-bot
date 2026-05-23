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

  fetch('/api/student/tg-status?tg_id=' + tgId)
    .then(function (res) { return res.json(); })
    .then(function (data) {
      if (data.status !== 'approved') {
        // Pending, rejected, not_found → về trang đăng ký
        window.location.replace('/register?tg_id=' + tgId);
      }
    })
    .catch(function () {
      // Lỗi mạng → fail open, không chặn học sinh
    });
})();
