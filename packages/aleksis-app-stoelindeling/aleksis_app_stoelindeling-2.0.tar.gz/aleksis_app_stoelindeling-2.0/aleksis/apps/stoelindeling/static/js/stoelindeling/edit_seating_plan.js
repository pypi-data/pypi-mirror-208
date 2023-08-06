function setPosition(event) {
  const parent = $(event.to);
  const xPos = parent.data("x");
  const yPos = parent.data("y");

  let pk = $(event.item).attr("data-pk");
  let sel = $("#seating-plan-form input[value=" + pk + "].pk-input");
  let x = sel.nextAll("input.x-input").first();
  let y = sel.nextAll("input.y-input").first();
  let seated = sel.nextAll("input.seated-input").first();

  if (parent.hasClass("seat-grid-cell")) {
    x.val(xPos);
    y.val(yPos);
    seated.val("True");
  } else {
    x.val("0");
    y.val("0");
    seated.val("False");
  }
}

function enableSeatGridCells() {
  $(".seat-grid-cell").sortable({
    group: "seats",
    animation: 150,
    onEnd: setPosition,
  });
}

function getStartY() {
  return Number.parseInt(
    $(".seat-grid .seat-grid-col .seat-grid-cell").first().data("y")
  );
}

function getEndY() {
  return Number.parseInt(
    $(".seat-grid .seat-grid-col .seat-grid-cell").last().data("y")
  );
}

function getStartX() {
  return Number.parseInt(
    $(".seat-grid .seat-grid-col .seat-grid-cell").first().data("x")
  );
}

function getEndX() {
  return Number.parseInt(
    $(".seat-grid .seat-grid-col .seat-grid-cell").last().data("x")
  );
}

function buildRow(x) {
  const el = $("<div class='seat-grid-col'></div>");
  for (let y = getStartY(); y <= getEndY(); y++) {
    el.append(
      "<div class='seat-grid-cell' data-x='" + x + "' data-y='" + y + "'></div>"
    );
  }
  return el;
}

$(document).ready(function () {
  $("#not-used-seats").sortable({
    group: "seats",
    animation: 150,
    onEnd: setPosition,
  });
  enableSeatGridCells();

  $("#seat-row-add-top").click(function () {
    const y = getStartY() - 1;
    $(".seat-grid .seat-grid-col").each(function (idx, el) {
      const x = Number.parseInt(
        $(el).children(".seat-grid-cell").first().data("x")
      );
      $(el).prepend(
        "<div class='seat-grid-cell' data-x='" +
          x +
          "' data-y='" +
          y +
          "'></div>"
      );
    });
    enableSeatGridCells();
  });
  $("#seat-row-add-bottom").click(function () {
    const y = getEndY() + 1;
    $(".seat-grid .seat-grid-col").each(function (idx, el) {
      const x = Number.parseInt(
        $(el).children(".seat-grid-cell").first().data("x")
      );
      $(el).prepend(
        "<div class='seat-grid-cell' data-x='" +
          x +
          "' data-y='" +
          y +
          "'></div>"
      );
    });
    enableSeatGridCells();
  });
  $("#seat-col-add-left").click(function () {
    const el = buildRow(getStartX() - 1);
    el.insertBefore(".seat-grid-col:first");
    enableSeatGridCells();
  });
  $("#seat-col-add-right").click(function () {
    const el = buildRow(getEndX() + 1);
    el.insertAfter(".seat-grid-col:last");
    enableSeatGridCells();
  });
});
