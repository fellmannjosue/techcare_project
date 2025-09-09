$(function(){
  $('#id_alumno, #id_materia, #id_docente').select2({
    width: '100%',
    theme: 'bootstrap-5',
    dropdownParent: $('.form-container')
  });

  // Cargar el grado cuando seleccionas un alumno (AJAX)
  $('#id_alumno').on('change', function(){
    var alumnoId = $(this).val();
    if(alumnoId){
      $.get("/conducta/ajax/grado/", { alumno_id: alumnoId }, function(data){
        $('#id_grado').val(data.grado || '');
      });
    }else{
      $('#id_grado').val('');
    }
  });

  // Cargar docentes según materia (AJAX)
  $('#id_materia').on('change', function(){
    var materiaId = $(this).val();
    var area = $('body').attr('data-area') || $('#reporteForm').data('area') || '';
    $('#id_docente').empty().append('<option value="">Cargando...</option>');
    if(materiaId){
      $.get("/conducta/ajax/docentes/", { materia_id: materiaId, area: area }, function(data){
        $('#id_docente').empty().append('<option value="">— Selecciona un docente —</option>');
        $.each(data.docentes, function(i, docente){
          $('#id_docente').append('<option value="'+docente[0]+'">'+docente[1]+'</option>');
        });
      });
    }else{
      $('#id_docente').empty().append('<option value="">— Selecciona un docente —</option>');
    }
  });

  // Si viene por POST y ya hay materia seleccionada, cargar docentes vía AJAX
  if ($("#id_materia").val()) {
    var materiaId = $("#id_materia").val();
    var area = $('body').attr('data-area') || $('#reporteForm').data('area') || '';
    $.get("/conducta/ajax/docentes/", { materia_id: materiaId, area: area }, function(data){
      $('#id_docente').empty().append('<option value="">— Selecciona un docente —</option>');
      $.each(data.docentes, function(i, docente){
        var selected = "";
        if ($("#id_docente").data('selected') == docente[0]) selected = "selected";
        $('#id_docente').append('<option value="'+docente[0]+'" '+selected+'>'+docente[1]+'</option>');
      });
    });
  }
});
