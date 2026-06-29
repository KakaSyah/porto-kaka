/* login-animations.js — VISUAL ONLY.
   Tidak mengubah logika autentikasi, validasi, atau request login.js.
   Hanya menambahkan micro-interaction:
   - toggle show/hide password
   - state loading + shake error pada tombol/kartu (mengamati teks #message)
   - sapaan berdasarkan jam saat ini
*/
(function () {
  // Time-based greeting (visual only)
  const greeting = document.getElementById('greetingText');
  if (greeting) {
    const hour = new Date().getHours();
    let text = 'Masuk untuk mengelola portofolio Anda';
    if (hour < 11) text = 'Selamat pagi, mari kelola portofolio Anda';
    else if (hour < 15) text = 'Selamat siang, mari kelola portofolio Anda';
    else if (hour < 18) text = 'Selamat sore, mari kelola portofolio Anda';
    else text = 'Selamat malam, mari kelola portofolio Anda';
    greeting.textContent = text;
  }

  // Show/hide password toggle
  const toggleBtn = document.getElementById('togglePass');
  const passwordInput = document.getElementById('password');
  if (toggleBtn && passwordInput) {
    toggleBtn.addEventListener('click', () => {
      const isHidden = passwordInput.type === 'password';
      passwordInput.type = isHidden ? 'text' : 'password';
      toggleBtn.innerHTML = isHidden
        ? '<i class="fas fa-eye-slash"></i>'
        : '<i class="fas fa-eye"></i>';
    });
  }

  // Loading state on submit button + shake/error feedback,
  // purely by observing what login.js already writes into #message.
  const form = document.getElementById('loginForm');
  const submitBtn = document.getElementById('loginSubmitBtn');
  const card = document.querySelector('.auth-card');
  const messageEl = document.getElementById('message');

  if (form && submitBtn) {
    form.addEventListener('submit', () => {
      submitBtn.classList.add('loading');
    }, { capture: true });
  }

  if (messageEl) {
    const observer = new MutationObserver(() => {
      const text = messageEl.textContent.trim();
      messageEl.classList.remove('is-error', 'is-success');

      if (!text) return;

      if (text === 'Memproses...') {
        return;
      }

      submitBtn && submitBtn.classList.remove('loading');

      // Heuristic: anything other than the processing message that appears
      // after submit is treated as an error for visual feedback only.
      messageEl.classList.add('is-error');
      if (card) {
        card.classList.remove('shake');
        // restart animation
        void card.offsetWidth;
        card.classList.add('shake');
      }
    });
    observer.observe(messageEl, { childList: true, characterData: true, subtree: true });
  }
})();
