function HomePageController()
{

}

function CreateMapController()
{
	
}

function FindGameController ($scope, $http)
{
	$http.post('/', JSON.stringify(
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
	$scope.join_game = function($game_id)
	{

	}
}

function CreateGameController ($scope, $http)
{
	$http.post('/', JSON.stringify(
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
		send(
			JSON.stringify(
			{
				'action': 'createGame', 
				'params': 
				{
					'sid': getCookie('sid'), 
					'name': $scope.name, 
					'map': parseInt($scope.map_id),
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
				}
				else
					setError(data.message);
			}
		);
	}
}

function LobbyController ($scope, $http, $interval)
{
	$interval(function()
	{
		$http.post('/', JSON.stringify(
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
			for(var i = 0; data.messages[i] != null; ++i)
				data.messages[i].time = toUTCTime(data.messages[i].time);

			setCookie('time', data.messages[0].time);
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

function SignoutController ($scope)
{
	deleteCookie('sid');
	window.location = '#signin';
}

function SigninController ($scope)
{
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

function SignupController ($scope)
{
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