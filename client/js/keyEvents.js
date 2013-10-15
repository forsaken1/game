var onKeyUp = [];
var onKeyDown = [];

// Key down events

onKeyDown[32] = function()
{
	player.jump();
}

onKeyDown[37] = function()
{
	player.moveLeft();
}

onKeyDown[39] = function()
{
	player.moveRight();
}

// Key Up events

onKeyUp[37] = function()
{
	player.stopLeft();
}

onKeyUp[39] = function()
{
	player.stopRight();
}

// Bind events

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
