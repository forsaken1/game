function Game($http)
{
	var BLOCK_SIZE = 50;
	var MAX_MAP_SIZE = 100;
	var MAX_MAPS_COUNT = 100;
	var MAPS = Array(MAX_MAPS_COUNT);

	$http.post(SERVER_URL, JSON.stringify(
	{
		'action': 'getMaps',
		'params':
		{
			sid: getCookie('sid')
		}
	})).success(function(data) 
	{
		// Init
		for(var i = 0; i < data.maps.length; ++i)
		{
			MAPS[data.maps[i].id] = data.maps[i].map;
		}
		MAP = MAPS[getCookie('map_id')];

		var socket = new WebSocket('ws://' + SERVER_URL_DOMAIN + '/websocket');
		var canvas = document.getElementById('canvas');
		var CTX = canvas.getContext('2d');
		var CTX_X = 0, CTX_Y = 0;
		var onKeyUp = [];
		var onKeyDown = [];

		var block = new Image();
		var portal = new Image();
		var border = new Image();
		var respawn = new Image();

		block.src = '/graphics/map/block.png';
		portal.src = '/graphics/map/portal.png';
		respawn.src = '/graphics/map/respawn.png';
		border.src = '/graphics/map/border.png'; //todo: сделать границу

		// Sockets
		socket.onopen = function() 
		{ 
			console.log("Connection is established"); 
		};

		socket.onclose = function(event) { 
			if (event.wasClean) {
				console.log('Connection closed');
			} else {
				console.log('Connection interrupted');
			}
			console.log('Error code: ' + event.code + ' reason: ' + event.reason);
		};
		 
		socket.onmessage = function(event) { 
			console.log("Data " + event.data);
		};

		socket.onerror = function(error) { 
			console.log("Error " + error.message); 
		};

		// Draw
		this.drawMap = function()
		{
			CTX.fillRect(0, 0, canvas.width, canvas.height);

			for(var i = 0; i < MAP.length; ++i)
			{
				for(var j = 0; j < MAP[i].length; ++j)
				{
					!MAP[i][j] && CTX.drawImage(border, j * BLOCK_SIZE, i * BLOCK_SIZE);
					MAP[i][j] == '#' &&	CTX.drawImage(block, j * BLOCK_SIZE, i * BLOCK_SIZE);
					MAP[i][j] == '$' &&	CTX.drawImage(respawn, j * BLOCK_SIZE, i * BLOCK_SIZE);
					/^\d+$/.test(MAP[i][j]) && CTX.drawImage(portal, j * BLOCK_SIZE, i * BLOCK_SIZE);
				}
			}			
		}

		// Keys
		onKeyDown[32] = function()
		{

		}

		onKeyDown[37] = function()
		{
			CTX.translate(CTX_X - 5, CTX_Y);
		}

		onKeyDown[39] = function()
		{
			CTX.translate(CTX_X + 5, CTX_Y);
		}

		onKeyUp[37] = function()
		{

		}

		onKeyUp[39] = function()
		{

		}

		document.body.onkeydown = function(e)
		{
			onKeyDown[e.keyCode] && onKeyDown[e.keyCode]();
		}

		document.body.onkeyup = function(e)
		{
			onKeyUp[e.keyCode] && onKeyUp[e.keyCode]();
		}

		// Start
		setInterval(drawMap, 25);

		socket.send(JSON.stringify(
		{
			'action': 'move',
			'params':
			{
				'sid': getCookie('sid'),
				'tick': 1,
				'dx': 0,
				'dy': 0
			}
		}));
	});
}