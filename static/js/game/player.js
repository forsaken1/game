function Player(ctx, x, y)
{
	var handler = this;

	this.ctx = ctx;
	this.x = x;
	this.y = y;
	this.animationPicCount = 10;
	this.animationCurrentNumber = 0;
	this.direction = 0;
	this.animation = [];
	this.animation[0] = [];
	this.animation[1] = [];
	this.moving = false;
	this.animSpeed = 10;
	
	for(var i = 0; i < this.animationPicCount; ++i)
	{
		this.animation[0][i] = new Image();
		this.animation[0][i].src = '/graphics/players/pl' + i + '.png';
		this.animation[1][i] = new Image();
		this.animation[1][i].src = '/graphics/players/pr' + i + '.png';
	}

	this.move = function()
	{
		handler.moving = true;
	}

	this.stop = function()
	{
		handler.moving = false;
	}

	this.incAnimationCurrentNumber = function()
	{
		handler.animationCurrentNumber = handler.animationCurrentNumber < handler.animationPicCount * handler.animSpeed - 1 ?
			++handler.animationCurrentNumber : 0;
	}

	this.getDirection = function()
	{
		return handler.direction ? 1 : -1;
	}

	this.setDirection = function(dir)
	{
		if(dir == 0)
			return;
		handler.direction = dir > 0 ? 1 : 0;
	}

	this.setCoords = function(x, y)
	{
		handler.x = x;
		handler.y = y;
	}

	this.getCoordX = function()
	{
		return handler.x;
	}

	this.getCoordY = function()
	{
		return handler.y;
	}

	this.draw = function(isUser, dx, dy)
	{
		var x = isUser ? 400 : handler.x + dx - 5; //todo: заюзать константы
		var y = isUser ? 300 : handler.y + dy;

		if(handler.moving)
			handler.incAnimationCurrentNumber();
		else
			handler.animationCurrentNumber = 3 * handler.animSpeed;
		
		handler.incAnimationCurrentNumber();
		handler.ctx.drawImage(handler.animation[handler.direction][parseInt(handler.animationCurrentNumber / handler.animSpeed)], x, y, 59, 59);
	}

	this.getStopJson = function(tick) //todo: вынести в отдельный класс
	{
		return JSON.stringify(
		{	
			'action': 'move',
			'params':
			{
				'tick': tick,
				'dx': 0,
				'dy': 0
			}
		})
	}
}