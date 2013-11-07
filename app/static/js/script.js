function send(data_, success_callback)
{
	$.ajax({
		url: '/',
		type: 'POST',
		dataType: 'json',
		data: data_,
		success: success_callback
	})
}