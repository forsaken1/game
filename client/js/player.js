function Player(startX, startY)
{
	this.x = startX;
	this.y = startY;
	this.dx = 0;
	this.dy = 0;
	this.speed = 6;
	this.moving = false;
	this.animationPicCount = 4;
	this.animationFrameNumber = 0;
	this.direction = 0; // to left == 0, right == 1
	
	this.animation = [];
	this.animation[0] = [];
	this.animation[1] = [];
	
	for(var i = 0; i < this.animationPicCount; ++i)
	{
		this.animation[0][i] = new Image();
		this.animation[0][i].src = 'graphics/pl' + (i + 1) + '.png';
		this.animation[1][i] = new Image();
		this.animation[1][i].src = 'graphics/pr' + (i + 1) + '.png';
	}
	
	this.getAnimationNumber = function()
	{
		if(!this.moving)
			return 0;
			
		if(this.animationFrameNumber >= this.animationPicCount - 1)
			return this.animationFrameNumber = 0;
		
		return ++this.animationFrameNumber;
	}
	
	this.getAnimationDirection = function()
	{
		return this.direction;
	}
	
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
		return this.animation[this.direction][this.getAnimationNumber()];
	}
	
	this.moveLeft = function()
	{
		this.direction = 0;
		this.dx = - this.speed;
		this.moving = true;
	}
	
	this.moveRight = function()
	{
		this.direction = 1;
		this.dx = this.speed;
		this.moving = true;
	}
	
	this.stopLeft = function()
	{
		if(this.dx < 0)
			this.dx = 0;
		this.moving = false;
	}
	
	this.stopRight = function()
	{
		if(this.dx > 0)
			this.dx = 0;
		this.moving = false;
	}
}