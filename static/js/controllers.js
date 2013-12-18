function CreateMapController($scope, $interval)
{
	$interval.cancel(SET_INTERVAL_HANDLER);
	$scope.create_map = function()
	{
		send(
			JSON.stringify({
				'action': 'uploadMap',
				'params':
				{
					'sid': getCookie('sid'),
					'name': $scope.name,
					'maxPlayers': parseInt($scope.maxPlayers),
					'map': $('#map').val().split("\n")
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
					setMessage('Map successfuly created');
				}
				else
					setError(data.message);
			}
		)
	}
}

function FindGameController ($scope, $http, $interval)
{
	$interval.cancel(SET_INTERVAL_HANDLER);
	$http.post(SERVER_URL, JSON.stringify(
	{
		'action': 'getGames',
		'params':
		{
			sid: getCookie('sid')
		}
	})).success(function(data) 
	{
		$scope.games = data.games;
	});
	$scope.join_game = function(game_id)
	{
		send(
			JSON.stringify(
			{
				'action': 'joinGame',
				'params': 
				{
					'sid': getCookie('sid'),
					'game': game_id
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
					setMessage('You will be redirected to game...');
					window.location = '#game';
				}
				else
					setError(data.message);
			}
		)
	}
	$scope.leave_game = function()
	{
		send(
			JSON.stringify(
			{
				'action': 'leaveGame',
				'params': 
				{
					'sid': getCookie('sid')
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
		)
	}
}

function CreateGameController ($scope, $http, $interval)
{
	$interval.cancel(SET_INTERVAL_HANDLER);
	$http.post(SERVER_URL, JSON.stringify(
	{
		'action': 'getMaps',
		'params':
		{
			sid: getCookie('sid')
		}
	})).success(function(data) 
	{
		$scope.maps = data.maps;
	});
	$scope.create_game = function()
	{
		if(!$scope.name)
		{
			setError('Game name is empty');
			return;
		}
		if(!$scope.maxPlayers)
		{
			setError('Max players is empty');
			return;
		}
		if(! /^\d+$/.test($scope.maxPlayers) || $scope.maxPlayers <= 0)
		{
			setError('Wrong number: max players');
			return;
		}
		var map_id = parseInt($scope.map_id);
		send(
			JSON.stringify(
			{
				'action': 'createGame', 
				'params': 
				{
					'sid': getCookie('sid'), 
					'name': $scope.name, 
					'map': map_id,
					'maxPlayers': parseInt($scope.maxPlayers)
				}
			}),
			function (data)
			{
				if(!data)
				{
					setError('Wrong request');
					return;
				}
				if(data.result == 'ok')
				{
					setMessage('Game successfully created');
					setCookie('map_id', map_id);
					window.location = '#game';
				}
				else
					setError(data.message);
			}
		);
	}
}

function LobbyController ($scope, $http, $interval)
{
	$interval.cancel(SET_INTERVAL_HANDLER);
	SET_INTERVAL_HANDLER = $interval(function()
	{
		$http.post(SERVER_URL, JSON.stringify(
		{
			'action': 'getMessages',
			'params':
			{
				sid: getCookie('sid'),
				game: g = getCookie('game') ? g : '', 
				since: parseInt(getCookie('time'))
			}
		})).success(function(data) 
		{
			if(!data.messages)
				return;

			for(var i = 0; data.messages[i] != null; ++i)
				data.messages[i].time = toDateTime(data.messages[i].time);

			/*if(data.messages[0].time)
				setCookie('time', data.messages[0].time);
			else
				setCookie('time', 0);*/

			$scope.messages = data.messages;
		});
	}, 1000);

	$scope.send_message = function()
	{
		if(!$scope.text)
		{
			return;
		}
		send(
			JSON.stringify(
			{
				'action': 'sendMessage', 
				'params': 
				{
					'sid': getCookie('sid'), 
					'game': g = getCookie('game') ? g : '', 
					'text': $scope.text
				}
			}),
			function (data)
			{
				if(!data) 
				{
					setError('Wrong request');
					return;
				}
				if(data.result == 'ok')
				{
					$('#text').val('');
				}
				else
					setError(data.message);
			}
		)
	}
}

function SignoutController ($scope, $interval)
{
	$interval.cancel(SET_INTERVAL_HANDLER);
	send(
		JSON.stringify({
			'action': 'signout' ,
			'params':
			{
				'sid': getCookie('sid')
			}
		}),
		function (data)
		{
			if(!data) 
			{
				setError('Wrong request');
				return;
			}

			deleteCookie('sid');
			window.location = '#signin';
		}
	)
}

function SigninController ($scope, $interval)
{
	$interval.cancel(SET_INTERVAL_HANDLER);
	$scope.signin = function()
	{
		send(
			JSON.stringify(
			{
				'action': 'signin', 
				'params': 
				{
					'login': $scope.login, 
					'password': $scope.password
				}
			}),
			function (data)
			{
				if(!data) 
				{
					setError('Wrong request');
					return;
				}
				if(data.result == 'ok')
				{
					setMessage('Successful authorisation');
					window.location = '#lobby';
				}
				else
					setError(data.message);

				setCookie('sid', data.sid);
			}
		);
	}
}

function SignupController ($scope, $interval)
{
	$interval.cancel(SET_INTERVAL_HANDLER);
	$scope.signup = function()
	{
		if(!$scope.login)
		{
			setError('Login is empty');
			return;
		}
		if(!$scope.password)
		{
			setError('Password is empty');
			return;	
		}
		if(!$scope.pass_conf || $scope.pass_conf != $scope.password)
		{
			setError('Wrong password confirmation');
			return;
		}
		send(
			JSON.stringify(
			{
				'action': 'signup', 
				'params': 
				{
					'login': $scope.login, 
					'password': $scope.password
				}
			}),
			function (data)
			{
				if(!data)
				{
					setError('Wrong request');
					return;
				}

				if(data.result == 'ok')
				{
					setMessage('Account successfully created');
					window.location = '#signin';
				}
				else
					setError(data.message);
			}
		);
	}
}