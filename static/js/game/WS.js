function WS(onMessage)
{
//	var ws = new WebSocket('ws://' + SERVER_URL_DOMAIN + '/websocket');
	var ws = new WebSocket('ws://5.100.88.174:8001');
	ws.onopen = function() 
	{
		console.log("Connection is established"); 
		ws.send(JSON.stringify(
		{
			'action': 'move',
			'params':
			{
				'sid': localStorage.getItem('sid'),
				'tick': 0,
				'dx': 0,
				'dy': 0
			}
		}));
	};

	ws.onclose = function(event)
	{ 
		if (event.wasClean)
		{
			console.log('Connection closed');
		} 
		else
		{
			console.log('Connection interrupted');
		}
		console.log('Error code: ' + event.code + ' reason: ' + event.reason);
	};
	 
	ws.onmessage = onMessage;

	ws.onerror = function(error)
	{
		console.log("Error " + error.message);
	};

	return ws;
}