$(document).ready(
  function () {
    var calendars = bulmaCalendar.attach('[data-widget-type="datetimepicker"]');

    // add classes of input elements to the wrappers to make sure, error
    // messages are displayed correctly
    calendars.forEach(calendar => {
      if (calendar.element.classList.contains("is-invalid")) {
        $(`#${calendar.id}`).addClass("is-invalid")
      }
      if (calendar.element.classList.contains("is-valid")) {
        $(`#${calendar.id}`).addClass("is-valid")
      }
      if (calendar.element.required) {
        $(`#${calendar.id}`).addClass("required")
      }
    });
  }
)
