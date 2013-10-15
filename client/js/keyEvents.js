var onKeyUp = [];
var onKeyDown = [];

onKeyDown[37] = function()
{
	player.moveLeft();
}

onKeyDown[39] = function()
{
	player.moveRight();
}

onKeyUp[37] = function()
{
	player.stopLeft();
}

onKeyUp[39] = function()
{
	player.stopRight();
}

document.body.onkeydown = function(e)
{
	if(onKeyDown[e.keyCode])
		onKeyDown[e.keyCode]();
}

document.body.onkeyup = function(e)
{
	if(onKeyUp[e.keyCode])
		onKeyUp[e.keyCode]();
}
