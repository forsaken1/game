function Player(startX, startY)
{
	this.x = startX;
	this.y = startY;
	this.dx = 0;
	this.dy = 0;
	this.sprite = new Image();
	this.sprite.src = 'graphics/pl1.png';
	this.speed = 6;
	this.movingLeft = false;
	this.movingRight = false;
	
	this.getX = function()
	{
		return this.x = this.x + this.dx;
	}
	
	this.getY = function()
	{
		return this.y = this.y + this.dy;
	}
	
	this.getSprite = function()
	{
		return this.sprite;
	}
	
	this.moveLeft = function()
	{
		this.dx = - this.speed;
		this.movingLeft = true;
	}
	
	this.moveRight = function()
	{
		this.dx = this.speed;
		this.movingRight = true;
	}
	
	this.stopLeft = function()
	{
		if(!this.movingRight)
			this.dx = 0;
		this.movingLeft = false;
	}
	
	this.stopRight = function()
	{
		if(!this.movingLeft)
			this.dx = 0;
		this.movingRight = false;
	}
}