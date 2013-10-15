var canvas = document.getElementById('canvas');
var player = new Player(400, 300);
var map = 
[
	[],
	[],
	[],
];

setInterval(draw, 33);

function draw()
{
	var ctx = canvas.getContext('2d');
	ctx.fillRect(0, 0, canvas.width, canvas.height);
	ctx.drawImage(player.getSprite(), player.getX(), player.getY());
}