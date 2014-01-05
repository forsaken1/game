var app = angular.module('game', ['ngRoute'])
localStorage.setItem('time', 0);
//SERVER_URL_DOMAIN = '192.168.0.101:5000';
SERVER_URL_DOMAIN = 'localhost:5000';
SERVER_URL = 'http://' + SERVER_URL_DOMAIN;
SERVER_WEBSOCKET_URL = SERVER_URL + '/websocket';
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
			when('/signin', {templateUrl: '/signin.html'}).
			when('/signup', {templateUrl: '/signup.html'}).
			when('/signout', {templateUrl: '/empty.html', controller: SignoutController}).
			when('/lobby', {templateUrl: '/lobby.html'}).
			when('/home', {templateUrl: '/home.html'}).
			when('/create_game', {templateUrl: '/create_game.html'}).
			when('/find_games', {templateUrl: '/find_games.html'}).
			when('/create_map', {templateUrl: '/create_map.html'}).
			when('/game', {templateUrl: '/game.html', controller: GameController}).
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

function c(data)
{
	console.log(data);
}

window.requestAnimFrame = (function()
{
	return window.requestAnimationFrame    || 
		window.webkitRequestAnimationFrame || 
		window.mozRequestAnimationFrame    || 
		window.oRequestAnimationFrame      || 
		window.msRequestAnimationFrame     || 
		function(callback)
		{
			window.setTimeout(callback, 1000 / 30);
		};
})();
