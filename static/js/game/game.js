function GameController($scope, $http, $interval)
{
	$interval.cancel(SET_INTERVAL_HANDLER);
	
	var MAPS = [];
	var TICK = 0;
	var DX = 0;
	var DY = 0;
	var VX = 0;
	var VY = 0;
	var N = null; // player`s number in array
	var LOGIN = localStorage.getItem('login');
	var MAP_ID = localStorage.getItem('map_id');
	var SID = localStorage.getItem('sid');

	$http.post(SERVER_URL, JSON.stringify(
	{
		'action': 'getMaps',
		'params':
		{
			sid: SID
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
		var MAP = MAPS[MAP_ID];
		var canvas = document.getElementById('canvas');
		var CTX = canvas.getContext('2d');
		var onKeyUp = [];
		var onKeyDown = [];
		var wall = new Image();
		var block = new Image();
		var portal = new Image();
		var respawn = new Image();
		var background = new Image();
		var aim = new Image();
		var players = [];
		var playersCount = 0;
		var projectiles = [];
		var items = [];
		var handler = this;
		var player;
		var mousePos;
		var currentWeapon = 0;
		var showStats = false;
		var iter = 0;
		var mapItems = {'K': 1, 'P': 1, 'M': 1, 'A': 1, 'R': 1, 'h': 1};
		var isMoveRight = false, isMoveLeft = false, isFire = false;
		var weaponProjectiles = {'K': PROJ_EMPTY, 'P': PROJ_PISTOL, 'M': PROJ_PISTOL, 'A': PROJ_ROCKET, 'R': PROJ_ROCKET};

		background.src = '/graphics/map/background.png';
		block.src = '/graphics/map/ground.png';
		portal.src = '/graphics/map/portal.png';
		respawn.src = '/graphics/map/respawn.png';
		wall.src = '/graphics/map/wall.png';
		aim.src = '/graphics/weapons/aim.png';

		CTX.font = 'bold 30px sans-serif';

		for(var i = 0; i < MAP.maxPlayers; ++i)
			players[i] = new Player(CTX, -1000, -1000);

		var wall_ = '';
		for(var i = 0; i < MAP.map[0].length; ++i)
			wall_ += '!';

		MAP.map.unshift(wall_);
		MAP.map.push(wall_);

		for(var i = 0; i < MAP.map.length; ++i)
			MAP.map[i] = '!' + MAP.map[i] + '!';

		for(var i = 0; i < MAP.map.length; ++i)
		{
			for(var j = 0; j < MAP.map[i].length; ++j)
			{
				if(mapItems[ MAP.map[i][j] ])
				{
					items[iter++] = new Item(CTX, j * BLOCK_SIZE, i * BLOCK_SIZE, MAP.map[i][j]);
				}
			}
		}

		// Socket onMessage
		var ws = WS(function(event)
		{
			var data = JSON.parse(event.data);
			TICK = data.tick;
			if(N == null)
			{
				N = handler.getN(LOGIN, data.players);
				player = players[N];
			}
			playersCount = data.players.length;
			for(var i = 0; i < playersCount; ++i)
			{
				players[i].setVars(data.players[i]);
				i != N && players[i].setDirection(data.players[i][2]);
			}
			for(var i = 0; i < items.length; ++i)
			{
				items[i].setTiming(data.items[i]);
			}
			var pl = data.players[N];
			VX = pl[2];
			VY = pl[3];
			DX = - (pl[0] * BLOCK_SIZE + BLOCK_SIZE / 2) + SCREEN_MIDDLE_X + 5;
			DY = - (pl[1] * BLOCK_SIZE + BLOCK_SIZE / 2) + SCREEN_MIDDLE_Y;
			projectiles = data.projectiles;
			//console.log(event.data); // for debug
		});

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
			if(showStats)
			{
				CTX.fillText('Player | Health | Kills | Deaths', 100, 30);
				CTX.fillText('________________________________', 100, 40);
				for(var i = 0; i < playersCount; ++i)
				{
					if(i == N)
					{
						CTX.fillStyle = "#F00";
						CTX.fillText(players[i].getVarsString(), 100, 80 + i * 40);
						CTX.fillStyle = "#000";
					}
					else
						CTX.fillText(players[i].getVarsString(), 100, 80 + i * 40);
				}				
				return requestAnimFrame(handler.draw);
			}
			for(var i = 0; i < MAP.map.length; ++i)
			{
				for(var j = 0; j < MAP.map[i].length; ++j)
				{
					MAP.map[i][j] == '!' &&	CTX.drawImage(wall,    j * BLOCK_SIZE + DX, i * BLOCK_SIZE + DY);
					MAP.map[i][j] == '#' &&	CTX.drawImage(block,   j * BLOCK_SIZE + DX, i * BLOCK_SIZE + DY);
					MAP.map[i][j] == '$' &&	CTX.drawImage(respawn, j * BLOCK_SIZE + DX, i * BLOCK_SIZE + DY);
					/^\d+$/.test(MAP.map[i][j]) && CTX.drawImage(portal, j * BLOCK_SIZE + DX, i * BLOCK_SIZE + DY);
				}
			}
			for(var i = 0; i < items.length; ++i)
			{
				items[i] && items[i].draw(DX, DY);
			}
			for(var i = 0; i < projectiles.length; ++i)
			{
				projectiles[i] && CTX.drawImage(weaponProjectiles[ projectiles[i][4] ], projectiles[i][0] * BLOCK_SIZE + DX - 4, projectiles[i][1] * BLOCK_SIZE + DY - 4);
			}
			for(var i = 0; i < playersCount; ++i)
			{
				players[i] && players[i].draw(i == N, DX, DY);
			}
			mousePos && CTX.drawImage(aim, mousePos.x - AIM_SIZE / 2, mousePos.y - AIM_SIZE / 2);
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
			player && player.setWeaponDirection(mousePos);
		}, true);

		canvas.addEventListener('mousedown', function(evt)
		{
			isFire = true;
		}, true);

		canvas.addEventListener('mouseup', function(evt)
		{
			isFire = false;
		}, true);

		this.sendWS = function()
		{
			if(isMoveLeft)
			{
				ws.send(JSON.stringify(
				{
					'action': 'move',
					'params':
					{
						'tick': TICK,
						'dx': - SPEED,
						'dy': VY
					}
				}));
			}
			else if(isMoveRight)
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
			}
			if(isFire)
			{
				ws.send(JSON.stringify(
				{
					'action': 'fire',
					'params':
					{
						'tick': TICK,
						'dx': (mousePos.x - DX) / BLOCK_SIZE - player.getCoordX(),
						'dy': (mousePos.y - DY) / BLOCK_SIZE - player.getCoordY()
					}
				}));
			}
			player && player.incAnimationCurrentNumber();
		}

		// DOWN keys
		onKeyDown[32] = function()
		{
			showStats = true;
		}

		onKeyDown[65] = onKeyDown[37] = function()
		{
			isMoveLeft = true;
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
					'dx': player.getDirection() * SPEED,
					'dy': - JUMP
				}
			}));
		}

		onKeyDown[68] = onKeyDown[39] = function()
		{
			isMoveRight = true;			
			player.setDirection(1);
			player.move();
		}
		// UP keys
		onKeyUp[32] = function()
		{
			showStats = false;
		}

		onKeyUp[65] = onKeyUp[37] = function()
		{
			isMoveLeft = false;
			ws.send(player.getStopJson(TICK));
			player.stop();
		}

		onKeyUp[87] = onKeyUp[38] = function()
		{
			ws.send(player.getStopJson(TICK));
		}

		onKeyUp[68] = onKeyUp[39] = function()
		{
			isMoveRight = false;
			ws.send(player.getStopJson(TICK));
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
		SET_INTERVAL_HANDLER = $interval(handler.sendWS, 33);
	});

	$scope.leave_game = function()
	{
		send(
			JSON.stringify(
			{
				'action': 'leaveGame',
				'params': 
				{
					'sid': SID
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