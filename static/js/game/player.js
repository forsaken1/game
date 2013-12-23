function Player(ctx, x, y)
{
	this.sprite = new Image();
	this.sprite.src = '/graphics/players/p.png';
	this.ctx = ctx;
	this.x = x;
	this.y = y;

	var handler = this;

	this.setCoords = function(x, y)
	{
		handler.x = x;
		handler.y = y;
	}

	this.draw = function(dx, dy)
	{
		handler.ctx.drawImage(handler.sprite, handler.x + dx, handler.y + dy);
	}

	this.drawMe = function()
	{
		handler.ctx.drawImage(handler.sprite, 800 / 2, 600 / 2); //todo
	}

	this.getStopJson = function(tick, x, y)
	{
		return JSON.stringify(
		{	
			'action': 'move',
			'params':
			{
				'tick': tick,
				'dx': x,
				'dy': y
			}
		})
	}
}