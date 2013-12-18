function Player(ctx)
{
	this.sprite = new Image();
	this.sprite.src = '/graphics/players/p.png';
	this.ctx = ctx;
	this.x = 0;
	this.y = 0;

	var handler = this;

	this.setCoords = function(x, y)
	{
		handler.x = x;
		handler.y = y;
	}

	this.draw = function()
	{
		handler.ctx.drawImage(handler.sprite, handler.x, handler.y);
	}
}