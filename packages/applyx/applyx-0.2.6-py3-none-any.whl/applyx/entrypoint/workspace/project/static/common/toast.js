
class Toast {

  static info(message, delay) {
    Toast.alert(message, delay, 'info');
  }

  static warn(message, delay) {
    Toast.alert(message, delay, 'warn');
  }

  static error(message, delay) {
    Toast.alert(message, delay, 'error');
  }

  static alert(message, delay, type) {
    let element = $('.toast-template').clone();
    element.removeClass('toast-template').removeClass('d-none');
    element.find('.toast-message').html(message);
    let bg_themes = {
      info: 'bg-info',
      warn: 'bg-secondary',
      error: 'bg-danger'
    }
    if (bg_themes[type]) {
      element.find('.toast-body').addClass(bg_themes[type]);
    }
    element.prependTo('.toast-list');
    new bootstrap.Toast(element, {delay: delay || 1000 * 3}).show();
    $('.toast-list .toast.hide').remove();
  }
}

window.Toast = Toast;
