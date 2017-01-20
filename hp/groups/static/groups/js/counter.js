var text_max = 1000;
$('#count_message').html(text_max);
function mycounter() {
	var text_length = $('#id_group_description').val().length;
	var text_remaining = text_max - text_length;
	$('#count_message').html(text_remaining);
};
$('#id_group_description').keyup(mycounter);
window.onload = mycounter;
