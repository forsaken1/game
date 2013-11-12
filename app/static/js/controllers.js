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
					setMessage('Successful authorisation');
				else
					setError(data.message);

				document.cookie = data.sid;
			}
		);
	}
}

function SignupController ($scope)
{
	$scope.signup = function()
	{
		if($scope.pass_conf != $scope.password)
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
					setMessage('Account successfully created');
				else
					setError(data.message);
			}
		);
	}
}