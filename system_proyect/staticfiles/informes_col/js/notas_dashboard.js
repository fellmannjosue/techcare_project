document.addEventListener('DOMContentLoaded', function() {
  var backBtn = document.getElementById('back-button');
  if (backBtn) {
    backBtn.addEventListener('click', function() {
      // Vuelve al menú principal
      window.location.href = '/menu/';
    });
  }
});
