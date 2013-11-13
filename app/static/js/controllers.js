function LobbyController ($scope, $http)
{
	/*send(
		JSON.stringify({'action': 'getMessages', 'params': {'sid': getCookie('sid'), 'game': g = getCookie('game') ? g : '', since: 0}}),
		function(data)
		{
			if(!data)
			{
				setError('Wrong request');
				return;
			}
			if(data.result == 'ok')
			{
				$scope.messages = data.messages;
			}
			else
				setError(data.message);
		}
	);*/
	
	$http.post('/').success(function() {
		//alert('gdfg');
	});

	$scope.send_message = function()
	{
		if(!$scope.text)
		{
			return;
		}
		send(
			JSON.stringify({'action': 'sendMessage', 'params': {'sid': getCookie('sid'), 'game': g = getCookie('game') ? g : '', 'text': $scope.text}}),
			function(data)
			{
				if(!data) 
				{
					setError('Wrong request');
					return;
				}
				if(data.result == 'ok')
				{
					//setMessage('Successful authorisation');
				}
				else
					setError(data.message);
			}
		)
	}
}

function SignoutController ($scope)
{
	document.cookie = '';
	window.location = '#signin';
}

function SigninController ($scope)
{
	$scope.signin = function()
	{
		send(
			JSON.stringify({'action': 'signin', 'params': {'login': $scope.login, 'password': $scope.password}}),
			function(data)
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
			JSON.stringify({'action': 'signup', 'params': {'login': $scope.login, 'password': $scope.password}}),
			function(data)
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