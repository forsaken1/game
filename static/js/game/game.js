function GameController($http, $interval)
{
	$interval.cancel(SET_INTERVAL_HANDLER);
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
			var index = data.maps[i].id;
			MAPS[index] = {};
			MAPS[index].map = data.maps[i].map;
			MAPS[index].name = data.maps[i].name;
			MAPS[index].maxPlayers = data.maps[i].maxPlayers;
		}
		MAP = MAPS[getCookie('map_id')];

		var TICK = 0;
		var SPEED = 20;
		var JUMP = 50;
		var VX = 0, VY = 0;
		var DIRECTION_X = 0;
		var DIRECTION_Y = 0;
		var LOGIN = getCookie('login');
		var N = null; // player`s number in array
		var canvas = document.getElementById('canvas');
		var CTX = canvas.getContext('2d');
		var CTX_X = 0, CTX_Y = 0;
		var onKeyUp = [];
		var onKeyDown = [];

		var block = new Image();
		var portal = new Image();
		var border = new Image();
		var respawn = new Image();
		var players = [];
		var handler = this;
		var player;

		for(var i = 0; i < MAP.maxPlayers; ++i)
			players[i] = new Player(CTX, -1000, -1000);

		block.src = '/graphics/map/block.png';
		portal.src = '/graphics/map/portal.png';
		respawn.src = '/graphics/map/respawn.png';
		border.src = '/graphics/map/border.png'; //todo: сделать границу

		// Sockets
		var ws = new WebSocket('ws://' + SERVER_URL_DOMAIN + '/websocket');

		ws.onopen = function() 
		{
			console.log("Connection is established"); 
			ws.send(JSON.stringify(
			{
				'action': 'move',
				'params':
				{
					'sid': getCookie('sid'),
					'tick': TICK,
					'dx': 0,
					'dy': 0
				}
			}));
		};

		ws.onclose = function(event)
		{ 
			if (event.wasClean) {
				console.log('Connection closed');
			} else {
				console.log('Connection interrupted');
			}
			console.log('Error code: ' + event.code + ' reason: ' + event.reason);
		};
		 
		ws.onmessage = function(event)
		{
			var data = JSON.parse(event.data);
			TICK = data.tick;
			if(N == null)
			{
				N = handler.getN(LOGIN, data.players);
				player = players[N];
			}
			var x = data.players[N][0] * BLOCK_SIZE - BLOCK_SIZE / 2;
			var y = data.players[N][1] * BLOCK_SIZE - BLOCK_SIZE / 2;
			player.setCoords(x, y);
			VX = data.players[N][2];
			VY = data.players[N][3];
			DX = -x + 400;
			DY = -y + 300;
			//console.log(event.data); // for debug
		};

		ws.onerror = function(error)
		{
			console.log("Error " + error.message);
		};

		this.getN = function(login, pl)
		{
			for(var i = 0; i < pl.length; ++i)
				if(pl[i][5] == login)
					return i;
		}

		var FILL_WIDTH  = (w = MAP.map[0].length * BLOCK_SIZE) > canvas.width ? w : canvas.width;
		var FILL_HEIGHT = (w = MAP.map.length * BLOCK_SIZE) > canvas.height ? w : canvas.height;
		var DX = 0;
		var DY = 0;

		// Draw
		this.draw = function()
		{
			CTX.fillRect(0, 0, FILL_WIDTH, FILL_HEIGHT);

			for(var i = 0; i < MAP.map.length; ++i)
			{
				for(var j = 0; j < MAP.map[i].length; ++j)
				{
					!MAP.map[i][j] && CTX.drawImage(border, j * BLOCK_SIZE + DX, i * BLOCK_SIZE + DY);
					MAP.map[i][j] == '#' &&	CTX.drawImage(block, j * BLOCK_SIZE + DX, i * BLOCK_SIZE + DY);
					//MAP.map[i][j] == '$' &&	CTX.drawImage(respawn, j * BLOCK_SIZE, i * BLOCK_SIZE);
					/^\d+$/.test(MAP.map[i][j]) && CTX.drawImage(portal, j * BLOCK_SIZE + DX, i * BLOCK_SIZE + DY);
				}
			}
			for(var i = 0; i < players.length; ++i)
			{
				players[i] && i == N ? players[N].drawMe() : players[i].draw(DX, DY);
			}
		}

		// DOWN keys
		onKeyDown[37] = function()
		{
			ws.send(JSON.stringify(
			{
				'action': 'move',
				'params':
				{
					'tick': TICK,
					'dx': -SPEED,
					'dy': VY
				}
			}));
			DIRECTION_X = -1;
		}

		onKeyDown[38] = function()
		{
			ws.send(JSON.stringify(
			{
				'action': 'move',
				'params':
				{
					'tick': TICK,
					'dx': DIRECTION_X * SPEED,
					'dy': -JUMP
				}
			}));
			DIRECTION_Y = -1;
		}

		onKeyDown[39] = function()
		{
			ws.send(JSON.stringify(
			{
				'action': 'move',
				'params':
				{
					'tick': TICK,
					'dx': SPEED,
					'dy': VY
				}
			}));
			DIRECTION_X = 1;
		}
		// UP keys
		onKeyUp[37] = function()
		{
			ws.send(player.getStopJson(TICK, DIRECTION_X, DIRECTION_Y));
			DIRECTION_X = 0;
		}

		onKeyUp[38] = function()
		{
			ws.send(player.getStopJson(TICK, DIRECTION_X, DIRECTION_Y));
			DIRECTION_Y = 0;
		}

		onKeyUp[39] = function()
		{
			ws.send(player.getStopJson(TICK, DIRECTION_X, DIRECTION_Y));
			DIRECTION_X = 0;
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
		setInterval(this.draw, 33);
	});
}