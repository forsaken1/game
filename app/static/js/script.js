var app = angular.module('game', ['ngRoute'])
setCookie('time', 0);

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
			when('/signout', {templateUrl: '/static/empty.html', controller: SignoutController}).
			when('/lobby', {templateUrl: '/static/lobby.html'}).
			when('/home', {templateUrl: '/static/home.html', controller: HomePageController}).
			when('/create_game', {templateUrl: '/static/create_game.html'}).
			when('/find_games', {templateUrl: '/static/find_games.html'}).
			when('/create_map', {templateUrl: '/static/create_map.html'}).
			when('/game', {templateUrl: '/static/game.html'}).
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

function toUTCTime(timestamp)
{
	var d = new Date(timestamp);
	return d.getYear() + '/' + (d.getMonth() + 1) + '/' + d.getDay() + ' ' + d.getHours() + ':' + d.getMinutes();
}

function checkAuth()
{
	var g = getCookie('sid');
	send(
		JSON.stringify(
		{
			'action': 'sidValidation',
			'params':
			{
				'sid': g ? g : ''
			}
		}),
		function(data)
		{
			if(!data)
			{
				setError('Wrong request');
				return;
			}
			if(data.result != 'ok')
			{
				window.location = '#signin';
			}
		}
	);
}