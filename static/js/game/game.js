function GameController($scope, $http, $interval)
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
			sid: localStorage.getItem('sid')
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
		MAP = MAPS[localStorage.getItem('map_id')];

		var AIM_SIZE = 75;
		var TICK = 0;
		var SPEED = 20;
		var JUMP = 50;
		var VX = 0, VY = 0;
		var DIRECTION_X = 0;
		var DIRECTION_Y = 0;
		var LOGIN = localStorage.getItem('login');
		var N = null; // player`s number in array
		var canvas = document.getElementById('canvas');
		var CTX = canvas.getContext('2d');
		var DX = 0;
		var DY = 0;
		var onKeyUp = [];
		var onKeyDown = [];

		var pistol = new Image();
		var minigun = new Image();
		var railgun = new Image();
		var sword = new Image();
		var rocket = new Image();
		var block = new Image();
		var portal = new Image();
		var respawn = new Image();
		var background = new Image();
		var bullet = new Image();
		var aim = new Image();
		var players = [];
		var projectiles = [];
		var handler = this;
		var player;
		var mousePos;
		var currentWeapon = 0;

		for(var i = 0; i < MAP.maxPlayers; ++i)
			players[i] = new Player(CTX, -1000, -1000);

		background.src = '/graphics/map/background.png';
		block.src = '/graphics/map/ground.png';
		portal.src = '/graphics/map/portal.png';
		respawn.src = '/graphics/map/respawn.png';
		pistol.src = '/graphics/weapons/pistol.png';
		minigun.src = '/graphics/weapons/minigun.png';
		railgun.src = '/graphics/weapons/railgun.png';
		sword.src = '/graphics/weapons/sword.png';
		rocket.src = '/graphics/weapons/rocket.png';
		bullet.src = '/graphics/weapons/bullet.png';
		aim.src = '/graphics/weapons/aim.png';

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
					'sid': localStorage.getItem('sid'),
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
			for(var i = 0; i < data.players.length; ++i)
			{
				if(i != N)
				{
					var x = data.players[i][0] * BLOCK_SIZE - BLOCK_SIZE / 2;
					var y = data.players[i][1] * BLOCK_SIZE - BLOCK_SIZE / 2;
					players[i].setCoords(x, y);
					players[i].setDirection(data.players[i][2]);
				}
			}
			var x = data.players[N][0] * BLOCK_SIZE - BLOCK_SIZE / 2;
			var y = data.players[N][1] * BLOCK_SIZE - BLOCK_SIZE / 2;
			player.setCoords(x, y);
			VX = data.players[N][2];
			VY = data.players[N][3];
			DX = -x + 405;
			DY = -y + 300;
			projectiles = data.projectiles;
			//console.log(event.data); // for debug
		};

		ws.onerror = function(error)
		{
			console.log("Error " + error.message);
		};

		this.getN = function(login, pl)
		{
			for(var i = 0; i < pl.length; ++i)
				if(pl[i][6] == login)
					return i;
		}

		// Draw
		this.draw = function()
		{
			CTX.drawImage(background, 0, 0);

			for(var i = 0; i < MAP.map.length; ++i)
			{
				for(var j = 0; j < MAP.map[i].length; ++j)
				{
					MAP.map[i][j] == '#' &&	CTX.drawImage(block, j * BLOCK_SIZE + DX, i * BLOCK_SIZE + DY);
					MAP.map[i][j] == 'K' &&	CTX.drawImage(sword, j * BLOCK_SIZE + DX, i * BLOCK_SIZE + DY - 15, 50, 80);
					MAP.map[i][j] == 'P' &&	CTX.drawImage(pistol, j * BLOCK_SIZE + DX + 6, i * BLOCK_SIZE + DY + 17, 40, 22);
					MAP.map[i][j] == 'M' &&	CTX.drawImage(minigun, j * BLOCK_SIZE + DX, i * BLOCK_SIZE + DY + 18);
					MAP.map[i][j] == 'A' &&	CTX.drawImage(railgun, j * BLOCK_SIZE + DX + 2, i * BLOCK_SIZE + DY + 18, 46, 15);
					MAP.map[i][j] == 'R' &&	CTX.drawImage(rocket, j * BLOCK_SIZE + DX + 1, i * BLOCK_SIZE + DY + 17, 50, 20);
					//MAP.map[i][j] == '$' &&	CTX.drawImage(respawn, j * BLOCK_SIZE, i * BLOCK_SIZE);
					/^\d+$/.test(MAP.map[i][j]) && CTX.drawImage(portal, j * BLOCK_SIZE + DX, i * BLOCK_SIZE + DY);
				}
			}
			for(var i = 0; i < players.length; ++i)
			{
				players[i] && players[i].draw(i == N, DX, DY);
			}
			for(var i = 0; i < projectiles.length; ++i)
			{
				projectiles[i] && CTX.drawImage(bullet, projectiles[i][0] * BLOCK_SIZE + DX, projectiles[i][1] * BLOCK_SIZE + DY);
				c(projectiles);
			}
			mousePos && CTX.drawImage(aim, mousePos.x - AIM_SIZE / 2, mousePos.y - AIM_SIZE / 2, AIM_SIZE, AIM_SIZE);
			requestAnimFrame(handler.draw);
		}

		// MOUSE events
		this.getMousePos = function(canvas, evt)
		{
			var rect = canvas.getBoundingClientRect();
			return {
				x: evt.clientX - rect.left,
				y: evt.clientY - rect.top
			};
		}

		canvas.addEventListener('mousemove', function(evt)
		{
			mousePos = handler.getMousePos(canvas, evt);
		}, true);

		canvas.addEventListener('mousedown', function(evt)
		{
			mousePos = handler.getMousePos(canvas, evt);
			var dd;
			ws.send(dd = JSON.stringify(
			{
				'action': 'fire',
				'params':
				{
					'tick': TICK,
					'dx': (mousePos.x - DX) / BLOCK_SIZE,
					'dy': (mousePos.y - DY) / BLOCK_SIZE
				}
			}));
			c(dd);
		}, true);

		// DOWN keys
		onKeyDown[65] = onKeyDown[37] = function()
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
			player.setDirection(-1);
			player.move();
		}

		onKeyDown[87] = onKeyDown[38] = function()
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

		onKeyDown[68] = onKeyDown[39] = function()
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
			player.setDirection(1);
			player.move();
		}
		// UP keys
		onKeyUp[65] = onKeyUp[37] = function()
		{
			ws.send(player.getStopJson(TICK, DIRECTION_X, DIRECTION_Y));
			DIRECTION_X = 0;
			player.stop();
		}

		onKeyUp[87] = onKeyUp[38] = function()
		{
			ws.send(player.getStopJson(TICK, DIRECTION_X, DIRECTION_Y));
			DIRECTION_Y = 0;
		}

		onKeyUp[68] = onKeyUp[39] = function()
		{
			ws.send(player.getStopJson(TICK, DIRECTION_X, DIRECTION_Y));
			DIRECTION_X = 0;
			player.stop();
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
		this.draw();
	});

	$scope.leave_game = function()
	{
		send(
			JSON.stringify(
			{
				'action': 'leaveGame',
				'params': 
				{
					'sid': localStorage.getItem('sid')
				}
			}),
			function(data)
			{
				if(!data)
				{
					setError('Wrong request');
					return;
				}
				if(data.result == 'ok')
				{
					setMessage('You disconnected from game');
				}
				else
					setError(data.message);
			}
		);
		window.location = '#find_games';
	}
}