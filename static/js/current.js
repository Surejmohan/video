$(function () {
  $("#fileupload").change(function () {
      if (typeof (FileReader) != "undefined") {
          var dvPreview = $("#dvPreview");
          dvPreview.html("");
          var regex = /^([a-zA-Z0-9\s_\\.\-:])+(.jpg|.jpeg|.gif|.png|.bmp)$/;
          $($(this)[0].files).each(function () {
              var file = $(this);
              if (regex.test(file[0].name.toLowerCase())) {
                  var reader = new FileReader();
                  reader.onload = function (e) {
                      var img = $("<img />");
                      img.attr("class", "img-fluid img-thumbnail");
                      img.attr("style", "height:100px;width: 100px; margin:10px");
                      img.attr("src", e.target.result);
                      dvPreview.append(img);
                  }
                  reader.readAsDataURL(file[0]);
              } else {
                  alert(file[0].name + " is not a valid image file.");
                  dvPreview.html("");
                  return false;
              }
          });
      } else {
          alert("This browser does not support HTML5 FileReader.");
      }
  });
});
  
function resetFile() {
  const file1 = document.getElementById("fileupload");
  const file2 = document.getElementById("dvPreview");
  file1.value = '';
  file2.value = '';
  $("#dvPreview").hide();
}
  



function resetvideo() {
  const file1 = document.getElementById("videobutton");
  file1.value = '';
  $("#up1").show();
  $("#up2").show();
  $("#video").hide();
  $("#third").hide();
}

function resetthird() {
  const file1 = document.getElementById("firstList");
  file1.value = '';
  $("#up1").show();
  $("#up2").show();
  $("#third").hide();
  $("#mass").hide();
}










var htm = '';

function video()
{

htm = `
<div class="col-lg-12" style="margin-bottom: 10px;">
<div class=" col-xs-12 col-sm-6 col-md-9">
<div class="form-group" style = "margin-bottom: 10px;"><br>
<div style="margin: 20px;"><b>Upload Video</b></div>
          <div class="row col-xs-12 col-sm-6 col-md-9">
          <label class="custom-file">
          <input type="file" id ="videobutton" class="custom-file-input dropzone" name="videos" accept = ".mp4" multiple required/>
          <span class="custom-file-control"></span>
          </label>
          </div><br>
          <div class="row col-md-4 col-xs-12 col-sm-6 col-md-9">
          <input type="submit" name="action" id ="video" value="Upload" class="btn btn-primary pull-left" style="max-height:40px;min-width:200px;max-width: 200px;margin-top:9px; background-color:#2dc997; margin-bottom: 10px;" onclick="processing();" />
          &nbsp;<button type="button" class="btn btn-danger pull-left" style="min-width:200px;max-width: 200px; margin-bottom: 10px;" onclick="resetvideo()"> Reset The Field
          </button>
          </div>
          <br><br><br>
          </div>
</div>
</div>
`
document.getElementById("video").innerHTML= htm; 

}








function getauth(){

var list1 = document.getElementById('firstList').value;
var list2 = document.getElementById("secondList");


if (list1 =='1')
{

list2.options.length=0;
list2.options[0] = new Option('--Select--', '');
list2.options[1] = new Option('Ernakulam Junction South (ERS)', '1');
list2.options[2] = new Option('Thiruvananthapuram Central Station (TVC)', '2');
list2.options[3] = new Option('Ernakulam Town Station (ERN)', '3');
list2.options[4] = new Option('Angamaly Station (AFK)', '4');
list2.options[5] = new Option('Chalakudi Railway Station (CKI)', '5');


}
else if (list1 =='2')
{

list2.options.length=0;
list2.options[0] = new Option('--Select--', '');
list2.options[1] = new Option('Police Stations-THiruvanthapuram','');
list2.options[2] = new Option('kollam', '');
list2.options[3] = new Option('Pathanamthitta', '');
list2.options[4] = new Option('alappuzha', '');
list2.options[5] = new Option('Kottayam', '');

}
}




function third()
{
htm = `

<centre>
<div class="col-md-4" id ="mass">
<h4>Select Department</h4>
<div class ="row col-md-4 col-xs-12 col-sm-6 col-md-9">
<select class="custom-select"  id='firstList' name='firstList' onclick="getauth()" required>
<option class="dropdown-item" value="0">--Select--</option>
						  <option class="dropdown-item" value="1">Railways</option>
						  <option class="dropdown-item" value="2">Police</option>
						  
</select>
 
<h4>Locate here</h4>
<select class="custom-select"  id='secondList' name='secondList' required >
</select>
</div><br>


  
  <label for="example-date-input" class="col-2 col-form-label">Date</label><br>
    <div class="col-10"style="margin-bottom:10px;">
      <input class="form-control" type="date" value="" id="date" required>
    </div>
  <div class="row">
  <div class="col-10" style="margin-bottom:10px;">
  <label for="example-time-input" class="col-form-label">Start Time</label>
    <input class="form-control" type="time" value="" id="starttime" required>
  </div> <br>
  <div class="col-10">
  <label for="example-time-input" class="col-form-label">End Time</label>
  <input class="form-control" type="time" value="" id="endtime" required>          
</div>
</div><br>



<div class ="row col-md-4 col-xs-12 col-sm-6 col-md-9">
<input type="submit" name="action" value = "Request_Video" class="btn btn-primary pull-left" style="min-width:200px;max-width: 300px;margin-left: 10px; background-color:#2dc997; margin-bottom: 10px;" onclick="processingthird();" />
<button type="button" class="btn btn-danger pull-left" style="min-width:200px;max-width: 200px;margin-left: 10px; margin-bottom: 10px;" onclick="resetthird()"> Reset The Field
          </button>
        </div>
 <br><br><br>
</div>

<br><br>
</centre>



`
document.getElementById("third").innerHTML= htm;

}

$("#up1").click(function () {

	$("#up2").hide();
  $("#third").hide();
  $("#video").show();
});

$("#up2").click(function () {

	$("#up1").hide();
  $("#video").hide();
  $("#third").show();
});

