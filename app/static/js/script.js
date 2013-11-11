var app = angular.module('game', [])

app.
	config(['$interpolateProvider', function ($interpolateProvider) 
	{
		$interpolateProvider.startSymbol('[[');
		$interpolateProvider.endSymbol(']]');
	}]).
	config(['$routeProvider', function ($routeProvider) 
	{
		$routeProvider.
			when('/signin', {templateUrl: '/static/signin.html'}).
			when('/signup', {templateUrl: '/static/signup.html'}).
			when('/lobby', {templateUrl: '/static/lobby.html'}).
			when('/home', {templateUrl: '/static/home.html'}).
			otherwise({redirectTo: '/home'});
	}]);

function send(data_, success_callback)
{
	jQuery.ajax({
		//url: 'http://172.20.10.8:5000/',
		url: '/',
		type: 'POST',
		dataType: 'json',
		data: data_,
		contentType: 'application/json; charset=utf-8',
		success: success_callback
	});
}

function setMessage(text)
{
	jQuery('#message').html('<div class="alert alert-success"><strong>Well done!</strong> '+text+'</div>');
	setTimeout(function()
	{
		jQuery('#message').fadeTo("slow", 0.0, function() { jQuery('#error').html('') });
	}, 2000)
}

function setError(text)
{
	jQuery('#error').html('<div class="alert alert-danger"><strong>Oh snap!</strong> '+text+'</div>');
	setTimeout(function()
	{
		jQuery('#error').fadeTo("slow", 0.0, function() { jQuery('#error').html('') });
	}, 2000)
}

app.controller('SigninController', function ($scope)
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
});

app.controller('SignupController', function ($scope)
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
});