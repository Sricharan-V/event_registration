$(document).ready(function () {
  $('#registrationForm').on('submit', function (e) {
    e.preventDefault();
    let form = this;

    // Clear previous messages
    $('#formMessage').text('').removeClass('text-success text-danger');

    if (form.checkValidity() === false) {
      e.stopPropagation();
      $(form).addClass('was-validated');
      return;
    }

    // If valid, submit form normally (can replace below with AJAX if needed)
    form.submit();
  });


  // Remove validation styles on input
  $('#registrationForm input').on('input', function () {
    $(this).removeClass('is-invalid');
    $(this).closest('form').removeClass('was-validated');
  });
});
