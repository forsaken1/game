function setAlert(text, type, block_id)
{
	var block = jQuery('#' + block_id);
	block.html('<div class="alert ' + type + '"><strong>Well done!</strong> ' + text + '</div>');
	setTimeout(function()
	{
		block.fadeTo("slow", 0.0, function() { block.html('') });
	}, 2000)
}

function setMessage(text)
{
	setAlert(text, 'alert-success', 'message');
}

function setError(text)
{
	setAlert(text, 'alert-danger', 'error');
}