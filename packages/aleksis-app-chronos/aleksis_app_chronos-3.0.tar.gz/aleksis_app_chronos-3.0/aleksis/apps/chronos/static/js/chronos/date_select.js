var data = getJSONScript("datepicker_data");
var activeDate = new Date(data.date);

function updateDatepicker() {
  $("#date").val(formatDate(activeDate));
}

function loadNew() {
  window.location.href = data.dest + formatDateForDjango(activeDate);
}

function onDateChanged() {
  activeDate = M.Datepicker.getInstance($("#date")).date;
  loadNew();
}

$(document).ready(function () {
  $("#date").change(onDateChanged);

  updateDatepicker();
});
