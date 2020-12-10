function editScores() {
	var scores = document.getElementsByClassName("score");
	var buttons = document.getElementsByClassName("score_btn");
	
	//make scores editable
	for (var i = 0; i < scores.length; i++) {
		scores.item(i).classList.remove("form-control-plaintext");
		scores.item(i).removeAttribute("readonly");
		scores.item(i).classList.add("form-control");
	}
	
	//show buttons		  
	for (var i = 0; i < buttons.length; i++) {
		buttons.item(i).removeAttribute("hidden");
	}
}

function displayCourses(course_list) {
	if (course_list.length == 0) document.getElementById("course_options").innerHTML = "<option></option>";

	else {
		var course_options = "";
		for (item in course_list) {
			opt = document.createElement("option");
			opt.value = item;
			opt.text = item;
			newSel.appendChild(opt);
		  }
		}
}