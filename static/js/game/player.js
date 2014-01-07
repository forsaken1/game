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

	this.weapon = [];
	this.weapon[0] = [];
	this.weapon[1] = [];
	this.weaponCount = 1;
	this.currentWeapon = 0;
	this.weaponDirection = 0;
	this.weaponDirectionX = 0;
	this.weaponDirectionY = 0;

	this.healthBar = new Image();
	this.healthBar.src = '/graphics/players/healthBar.png';
	
	for(var i = 0; i < this.animationPicCount; ++i)
	{
		this.animation[0][i] = new Image();
		this.animation[0][i].src = '/graphics/players/pl' + i + '.png';
		this.animation[1][i] = new Image();
		this.animation[1][i].src = '/graphics/players/pr' + i + '.png';
	}

	for(var i = 0; i < this.weaponCount; ++i)
	{
		this.weapon[0][i] = new Image();
		this.weapon[0][i].src = '/graphics/weapons/wl' + i + '.png';
		this.weapon[1][i] = new Image();
		this.weapon[1][i].src = '/graphics/weapons/wr' + i + '.png';
	}

	this.setCurrentWeapon = function(currWeapon)
	{

	}

	this.setWeaponDirection = function(mousePos)
	{
		this.weaponDirectionX = mousePos.x;
		this.weaponDirectionY = mousePos.y;
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

	this.setVars = function(vars)
	{
		handler.x = vars[0];
		handler.y = vars[1];
		handler.health = vars[7];
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
		var x = isUser ? SCREEN_MIDDLE_X : handler.x + dx;
		var y = isUser ? SCREEN_MIDDLE_Y : handler.y + dy;

		if(handler.moving)
			handler.incAnimationCurrentNumber();
		else
			handler.animationCurrentNumber = 3 * handler.animSpeed;
		
		var y_ = y + 20;
		var x_ = x + 30;
		handler.ctx.save()
		handler.ctx.translate(x_, y_);
		handler.weaponDirection = handler.weaponDirectionX > x_ ? 1 : 0;
		handler.ctx.rotate(Math.atan2(handler.weaponDirectionY - y_, handler.weaponDirectionX - x_) + Math.PI);
		handler.ctx.drawImage(handler.weapon[handler.weaponDirection][handler.currentWeapon], -25, -10);
		handler.ctx.restore();

		handler.incAnimationCurrentNumber();
		handler.ctx.drawImage(handler.animation[handler.direction][parseInt(handler.animationCurrentNumber / handler.animSpeed)], x, y, 59, 59);

		handler.ctx.drawImage(handler.healthBar, 0, 4 * handler.getHeathbar(), 32, 4, x + 10, y - 10, 32, 4);
	}

	this.getHeathbar = function()
	{
		if(handler.health > 85)
			return 0;
		else if(handler.health > 70)
			return 1;
		else if(handler.health > 55)
			return 2;
		else if(handler.health > 40)
			return 3;
		else if(handler.health > 25)
			return 4;
		else
			return 5;
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