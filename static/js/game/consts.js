var SCREEN_WIDTH = 800;
var SCREEN_HEIGHT = 600;
var BLOCK_SIZE = 50;
var SCREEN_MIDDLE_X = SCREEN_WIDTH / 2 - BLOCK_SIZE / 2;
var SCREEN_MIDDLE_Y = SCREEN_HEIGHT / 2 - BLOCK_SIZE / 2;
var AIM_SIZE = 75;
var SPEED = 20;
var JUMP = 50;

var HEALTH  = new Image();
var PISTOL  = new Image();
var MINIGUN = new Image();
var RAILGUN = new Image();
var SWORD   = new Image();
var ROCKET  = new Image();
HEALTH.src  = '/graphics/map/health.png';
PISTOL.src  = '/graphics/weapons/pistol.png';
MINIGUN.src = '/graphics/weapons/minigun.png';
RAILGUN.src = '/graphics/weapons/railgun.png';
SWORD.src   = '/graphics/weapons/sword.png';
ROCKET.src  = '/graphics/weapons/rocket.png';

var IMAGES = {'h': HEALTH, 'P': PISTOL, 'M': MINIGUN, 'A': RAILGUN, 'K': SWORD, 'R': ROCKET};