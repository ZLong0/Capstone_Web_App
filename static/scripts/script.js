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