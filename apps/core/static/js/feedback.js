/* ==========================================================
   Feedback global: auto-dismiss de toasts e modal de
   confirmação para ações destrutivas.

   Uso do modal: adicionar ao <form> os atributos
     data-confirm="Mensagem exibida no modal"
     data-confirm-title="Título opcional"
     data-confirm-btn="Rótulo opcional do botão de confirmação"
   ========================================================== */

(function () {
  'use strict';

  var TOAST_TIMEOUT_MS = 5000;

  /* ---------- Toasts ---------- */
  function dismissToast(toast) {
    if (toast.dataset.dismissed) return;
    toast.dataset.dismissed = '1';
    toast.classList.add('toast-hide');
    toast.addEventListener('animationend', function () {
      toast.remove();
    });
  }

  function initToasts() {
    document.querySelectorAll('.toast').forEach(function (toast) {
      var closeBtn = toast.querySelector('.toast-close');
      if (closeBtn) {
        closeBtn.addEventListener('click', function () {
          dismissToast(toast);
        });
      }
      setTimeout(function () {
        dismissToast(toast);
      }, TOAST_TIMEOUT_MS);
    });
  }

  /* ---------- Modal de confirmação ---------- */
  function initConfirmModal() {
    var overlay = document.getElementById('confirm-overlay');
    if (!overlay) return;

    var titleEl = document.getElementById('confirm-title');
    var msgEl = document.getElementById('confirm-msg');
    var okBtn = document.getElementById('confirm-ok');
    var cancelBtn = document.getElementById('confirm-cancel');
    var pendingForm = null;

    function openModal(form) {
      pendingForm = form;
      titleEl.textContent = form.dataset.confirmTitle || 'Confirmar ação';
      msgEl.textContent = form.dataset.confirm;
      okBtn.textContent = form.dataset.confirmBtn || 'Sim, confirmar';
      overlay.classList.add('open');
      okBtn.focus();
    }

    function closeModal() {
      pendingForm = null;
      overlay.classList.remove('open');
    }

    okBtn.addEventListener('click', function () {
      if (pendingForm) {
        var form = pendingForm;
        pendingForm = null;
        form.dataset.confirmed = '1';
        overlay.classList.remove('open');
        form.submit();
      }
    });

    cancelBtn.addEventListener('click', closeModal);

    overlay.addEventListener('click', function (e) {
      if (e.target === overlay) closeModal();
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && overlay.classList.contains('open')) closeModal();
    });

    document.addEventListener('submit', function (e) {
      var form = e.target;
      if (form.dataset.confirm && !form.dataset.confirmed) {
        e.preventDefault();
        openModal(form);
      }
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initToasts();
    initConfirmModal();
  });
})();
