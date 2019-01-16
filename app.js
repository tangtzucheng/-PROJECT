var dList;
function findNearMarker(coords,rad) {
	dList=[]
	var Dist = rad;
	near_text = '*None*';
	markerDist=0;
	// get all objects added to the map
	objects = map.getObjects();
	len = map.getObjects().length;
	i=0;
	// iterate over objects and calculate distance between them
	for (i = 0; i < len; i += 1) {
	markerDist = objects[i].getPosition().distance(coords);
	if (markerDist < Dist) {
		near_text = objects[i].getData();
		dList.push(near_text);
    }
  }
}

//set to traditional chinese
function switchMapLanguage(map, platform){
  var mapTileService = platform.getMapTileService({
      type: 'base'
    }),
    // Our layer will load tiles from the HERE Map Tile API
    chineseMapLayer = mapTileService.createTileLayer(
      'maptile',
      'normal.day',
      256,
      'png8',
      {lg: 'CHT'}
    );
  map.setBaseLayer(chineseMapLayer);
  // Display default UI components on the map and change default
  // language to simplified Chinese.
  // Besides supported language codes you can also specify your custom translation
  // using H.ui.i18n.Localization.
  var ui = H.ui.UI.createDefault(map, defaultLayers, 'zh-CN');
  // Remove not needed settings control
  ui.removeControl('mapsettings');
}


/**
 * Boilerplate map initialization code starts below:
 */

//Step 1: initialize communication with the platform
var platform = new H.service.Platform({
  app_id: '3CBCpkkNcYmNBxj3CWuB',
  app_code: 'w_R30ZOaNaqLOjtkKrudZg',
  useCIT: true,
  useHTTPS: true
});
var defaultLayers = platform.createDefaultLayers();

//Step 2: initialize a map
var map = new H.Map(document.getElementById('map'),
  defaultLayers.normal.map,{
  center: {lat: 23.48132, lng:120.4536},
  zoom: 15
});

//Step 3: make the map interactive
// MapEvents enables the event system
// Behavior implements default interactions for pan/zoom (also on mobile touch environments)
var behavior = new H.mapevents.Behavior(new H.mapevents.MapEvents(map));

switchMapLanguage(map, platform);

// Set up markers.
var camData=JSON.parse(cams);
camData.forEach(function(value,index){
	pos={lat:value.lat,lng:value.lng};
	marker=new H.map.Marker(pos);
	marker.setData(value.location);
	map.addObject(marker);
});

function search(){
	var q=document.getElementById("searchText").value;
	if(q.length==0)
	{
		alert("請輸入搜尋項目");
		return;
	}
	else
	{
		var onResult = function(result) {
			try{
				var locations = result.Response.View[0].Result,position;
			}
			catch(err){
				alert("沒有結果!");
				return;
			}
			if(location.length>1){
				alert("搜尋到多個項目");
				return;
			}
			position = {
				lat: locations[0].Location.DisplayPosition.Latitude,
				lng: locations[0].Location.DisplayPosition.Longitude
			};
			map.setCenter(position);
		};
		var geoCoder=platform.getGeocodingService();
		geoCoder.geocode({searchText:q+",嘉義"},onResult,function(e){
			alert(e);
		});
	}
}
function getGPS(){
	if("geolocation" in navigator){
		navigator.geolocation.getCurrentPosition(function(pos){
			map.setCenter({lat: pos.coords.latitude,lng:pos.coords.longitude});
			})
	} else {
		alert("地理位置不可用!")
	}
}
function genList(){
	var l=document.getElementById("list");
	i=1;len=l.length;
	for(i=1;i<len;i++)
		l[i]=null;
	var rad=document.getElementById("radius");
	var r=parseInt(rad.options[rad.selectedIndex].value);
	if(r==0){
		alert("請選擇距離!");
		return;
	}
	else{
		findNearMarker(map.getCenter(),r);
		if(dList.length==0){
			alert("無資料!");
			return;
		}
		dList.forEach(function(value,index){
			var option=document.createElement("option");
			option.text=value;
			l.add(option);
		});
	}
}
