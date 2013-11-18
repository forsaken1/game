var app = angular.module('game', ['ngRoute'])
setCookie('time', 0);
SERVER_URL = 'http://192.168.226.38:3000';
SERVER_URL = '/';
SET_INTERVAL_HANDLER = null;

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
			when('/home', {templateUrl: '/static/home.html'}).
			when('/create_game', {templateUrl: '/static/create_game.html'}).
			when('/find_games', {templateUrl: '/static/find_games.html'}).
			when('/create_map', {templateUrl: '/static/create_map.html'}).
			when('/game', {templateUrl: '/static/game.html'}).
			otherwise({redirectTo: '/signin'});
	}]);

function send(data_, success_callback)
{
	jQuery.ajax({
		url: SERVER_URL,
		type: 'POST',
		dataType: 'json',
		data: data_,
		contentType: 'application/json; charset=utf-8',
		success: success_callback
	});
}

function toDateTime(timestamp)
{
	var d = new Date(parseInt(timestamp) * 1000);
	return (d.getYear() + 1900) + '/' + (d.getMonth() + 1) + '/' + d.getDate() + ' ' + d.getHours() + ':' + d.getMinutes();
}
