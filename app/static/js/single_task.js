$(window).on('load', function() {
  $("#task-slider").twentytwenty();
  $(".twentytwenty-before-label")[0].dataset.content = "До";
  $(".twentytwenty-after-label")[0].dataset.content = "После";
});

$(function() {
  $('#toggle1').change(function() {
    let img = $('#img2')[0];
    if(img.style.opacity !== "0") {
      img.style.opacity = "0";
    } else {
      img.style.opacity = "0.2";
    }
  });
  $('#toggle2').change(function() {
    let img = $('#img3')[0];
    if(img.style.opacity !== "0") {
      img.style.opacity = "0";
    } else {
      img.style.opacity = "0.2";
    }
  });

  $('#toggleUsual').change(function() {
    let files = $('.usual');
    for (let file of files) {
      file.hidden = !file.hidden
    }
  });

  $('#toggleSentinel').change(function() {
    let files = $('.sentinel');
    for (let file of files) {
      file.hidden = !file.hidden
    }
  });
});

function changeSlider(beforeSrc, afterSrc) {
  $('.twentytwenty-before')[0].src = beforeSrc;
  $('.twentytwenty-after')[0].src = afterSrc;
}

function changeAnomalies(lst) {
  $('#anomaliesList')[0].innerHTML = "";
  // TODO: add elems to list
  // TODO: change active anomaly
}
