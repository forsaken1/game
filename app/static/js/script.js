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
			when('/signout', {templateUrl: '/static/home.html', controller: 'SignoutController'}).
			when('/lobby', {templateUrl: '/static/lobby.html'}).
			when('/home', {templateUrl: '/static/home.html'}).
			when('/find_game', {templateUrl: '/static/find_game.html'}).
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

