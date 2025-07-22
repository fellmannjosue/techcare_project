document.addEventListener('DOMContentLoaded', function() {
  // Botón Regresar
  var backBtn = document.getElementById('back-button');
  if (backBtn) {
    backBtn.addEventListener('click', function() {
      window.history.back();
    });
  }
});
