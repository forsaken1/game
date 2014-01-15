function Item(ctx, x, y, type)
{
	var handler = this;

	this.timing = 0;
	this.picture = IMAGES[type];

	this.draw = function(dx, dy)
	{
		if(!handler.timing)
			ctx.drawImage(handler.picture, x + dx, y + dy);
	}

	this.setTiming = function(timing)
	{
		handler.timing = timing;
	}
}