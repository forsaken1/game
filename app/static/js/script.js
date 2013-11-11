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
			when('/signin', {templateUrl: '/static/signin.html', controller: SigninController}).
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
	jQuery('#message').text();
}

function setError(text)
{
	jQuery('#error').text();
}

app.controller('SigninController', function ($scope)
{
	$scope.signin = function()
	{
		
	}
}

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
					setError('Wrong request');

				if(data.result == 'ok')
					setMessage('Account successfully created');
				else
					setError(data.message);
			}
		);
	}
});