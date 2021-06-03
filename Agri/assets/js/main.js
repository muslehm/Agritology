
$(document).ready(function () {
  setTimeout(function () {
    $(".dashboard").css("visibility", "hidden");

    $("#plantingPeriodButton").click(function (){
      $("#cropButton").css("opacity", "0.4");
      $("#plantingPeriodButton").css("opacity", "1");
      $(".plantTimeInput").css("display", "block");
      $(".noDataSelectedText").css("display", "none");
      $(".dashboard").css("visibility", "visible");
      $("#vegetableName").css("display", "block");
      $("#vegetableNameAr").css("display", "block");
      $("#vegetableNameMt").css("display", "block");
    });

    $("#cropButton").click(function () {
      $("#cropButton").css("opacity", "1");
      $("#plantingPeriodButton").css("opacity", "0.4");
      $(".plantTimeInput").css("display", "none");
      $(".dashboard").css("visibility", "visible");
      $(".noDataSelectedText").css("display", "none");
      $("#vegetableName").css("display", "block");
      $("#vegetableNameAr").css("display", "block");
      $("#vegetableNameMt").css("display", "block");
    });


  }, 500);

});