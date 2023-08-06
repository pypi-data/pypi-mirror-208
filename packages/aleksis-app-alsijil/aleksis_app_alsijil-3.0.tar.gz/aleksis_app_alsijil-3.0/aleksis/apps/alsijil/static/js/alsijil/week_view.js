$(document).ready(function () {
  $("#id_group").change(function () {
    $("#id_teacher").val("").formSelect();
  });
  $("#id_teacher").change(function () {
    $("#id_group").val("").formSelect();
  });
  $("#toggle-row.pre-hidden").hide();
});
$("#toggle-button").click(function () {
  $("#toggle-row").toggle();
});
$(".unfold-trigger").click(function (event) {
  let target = event.target;
  target.classList.toggle("vertical");
  let next_container = $(target).parent().next(".horizontal-scroll-container");
  if (next_container.length >= 1) {
    next_container[0].classList.toggle("vertical");
  }
});
