function setAlert(text, type, block_id, header, latency)
{
	var block = jQuery('#' + block_id);
	block.html('<div class="alert ' + type + '"><strong>' + header + '</strong> ' + text + '</div>');
	setTimeout(function()
	{
		block.fadeTo("slow", 0.0, function() { block.html(''); block.css('opacity', 1) });
	}, latency)
}

function setMessage(text)
{
	setAlert(text, 'alert-success', 'message', 'Well done!', 5000);
}

function setError(text)
{
	setAlert(text, 'alert-danger', 'error', 'Error!', 60000);
}