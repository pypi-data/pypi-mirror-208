

function toggleSettingsVisibility(){
  if (this.checked) {
    $("#settingsFieldset").removeClass("d-none");
  } else {
    $("#settingsFieldset").addClass("d-none");
  }
}

function toggleCollationSettingsState(){
  if (this.checked) {
      $("#collateMailsFieldset").removeClass("d-none");
  } else {
    $("#collateMailsFieldset").addClass("d-none");
  }
}

$(document).ready(function () {
  // turn checkboxes into bootstrap switches
  var boxes = $("input[type='checkbox']");
  // wrapping divs
  boxes.parent().addClass("custom-control custom-switch");
  // checkboxes
  boxes.addClass("custom-control-input");
  // labels
  boxes.next().addClass("custom-control-label");

  $("#id_receive_mails")
    .change(toggleSettingsVisibility)
    .trigger("change");
  $("#id_collate_mails")
    .change(toggleCollationSettingsState)
    .trigger("change");

})
