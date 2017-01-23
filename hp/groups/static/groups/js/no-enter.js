$("#id_member_name").keypress(
	function(event){
		if (event.which == '13') {
			event.preventDefault();
		}
	}
);
$("#id_owner_name").keypress(
	function(event){
		if (event.which == '13') {
			event.preventDefault();
		}
	}
);
