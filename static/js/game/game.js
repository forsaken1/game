function Game($http)
{
	var MAPS = Array(100);
	var MAP;

	//todo: синхронная загрузка
	$http.post(SERVER_URL, JSON.stringify(
	{
		'action': 'getMaps',
		'params':
		{
			sid: getCookie('sid')
		}
	})).success(function(data) 
	{
		for(var i = 0; i < data.maps.length; ++i)
		{
			MAPS[data.maps[i].id] = data.maps[i].map;
		}
		MAP = MAPS[getCookie('map_id')];

		canvas = document.getElementById('canvas');
		var CTX = canvas.getContext('2d');
		CTX.fillRect(0, 0, canvas.width, canvas.height);

		var block = new Image();
		block.src = '/graphics/map/block.jpg';

		block.onload = function() 
		{
			for(var i = 0; i < MAP.length; ++i)
			{
				for(var j = 0; j < MAP[i].length; ++j)
				{
					if(MAP[i][j] == '#')
						CTX.drawImage(block, j * 50, i * 50);
				}
			}
		}
	});
}