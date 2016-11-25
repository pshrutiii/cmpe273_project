function addWayPoint() {
  myWayPointState.incr();
  var index = myWayPointState.get();
  document.getElementById("waypoint-holder-" + index).style="display:block";
  if (index == 3) {
    $("#addwaypoint_holder").toggle();
  } 
}
 
var myWayPointState = function() {
  // set up closure scope
  var state = 0;

  // return object with methods to manipulate closure scope
  return {
    incr: function() {
      state ++;
    }, 
    decr: function() {
      state--;
    },
    get: function() {
      return state;
    }
  };
}();

function initMap() {
  var origin_place_id = null;
  var destination_place_id = null;
  var travel_mode = 'DRIVING';
  var map = new google.maps.Map(document.getElementById('map'), {
    mapTypeControl: false,
    center: {lat: 37.3388, lng: -121.8895},
    zoom: 13
  });
  var directionsService = new google.maps.DirectionsService;
  var directionsDisplay = new google.maps.DirectionsRenderer;
  directionsDisplay.setMap(map);

  var origin_input = document.getElementById('origin-input');
  var destination_input = document.getElementById('destination-input');
  var waypoint1_input = document.getElementById('waypoint-input-1');
  var waypoint2_input = document.getElementById('waypoint-input-2');
  var waypoint3_input = document.getElementById('waypoint-input-3');

  var origin_autocomplete = new google.maps.places.Autocomplete(origin_input);
  origin_autocomplete.bindTo('bounds', map);
  var destination_autocomplete =
      new google.maps.places.Autocomplete(destination_input);
  destination_autocomplete.bindTo('bounds', map);
  var waypoint1_autocomplete =
      new google.maps.places.Autocomplete(waypoint1_input);
  waypoint1_autocomplete.bindTo('bounds', map);
  var waypoint2_autocomplete =
      new google.maps.places.Autocomplete(waypoint2_input);
  waypoint2_autocomplete.bindTo('bounds', map);
  var waypoint3_autocomplete =
      new google.maps.places.Autocomplete(waypoint3_input);
  waypoint3_autocomplete.bindTo('bounds', map);

  function expandViewportToFitPlace(map, place) {
    if (place.geometry.viewport) {
      map.fitBounds(place.geometry.viewport);
    } else {
      map.setCenter(place.geometry.location);
      map.setZoom(17);
    }
  }

  origin_autocomplete.addListener('place_changed', function() {
    var place = origin_autocomplete.getPlace();
    if (!place.geometry) {
      window.alert("Autocomplete's returned place contains no geometry");
      return;
    }
    expandViewportToFitPlace(map, place);

    // If the place has a geometry, store its place ID and route if we have
    // the other place ID
    origin_place_id = place.place_id;
    // route(origin_place_id, destination_place_id, [], travel_mode,
    //      directionsService, directionsDisplay);
  });

  destination_autocomplete.addListener('place_changed', function() {
    var place = destination_autocomplete.getPlace();
    if (!place.geometry) {
      window.alert("Autocomplete's returned place contains no geometry");
      return;
    }
    expandViewportToFitPlace(map, place);

    // If the place has a geometry, store its place ID and route if we have
    // the other place ID
    destination_place_id = place.place_id;
    // route(origin_place_id, destination_place_id, [], travel_mode,
    //      directionsService, directionsDisplay);
  });

  $('#compare_prices_button').click(function comparePrices() {
    var source = origin_autocomplete.getPlace();
    if (!source.geometry) {
      window.alert("Autocomplete's returned place contains no geometry");
      return;
    }
    expandViewportToFitPlace(map, source);
    var source_place_id = source.place_id;          

    var destination = destination_autocomplete.getPlace();
    if (!destination.geometry) {
      window.alert("Autocomplete's returned place contains no geometry");
      return;
    }
    expandViewportToFitPlace(map, destination);
    var destination_id = destination.place_id;
    
    way_point_ids = [];
    for (var i=1; i <= myWayPointState.get(); ++i) {
      var waypoint_name = eval("waypoint" + i + "_autocomplete");
      var waypoint = waypoint_name.getPlace();
      if (!waypoint.geometry) {
        window.alert("Autocomplete's returned place contains no geometry");
        return; 
      }
      
      expandViewportToFitPlace(map, waypoint);
      way_point_ids.push(waypoint.place_id);
    }
    route(origin_place_id, destination_place_id, way_point_ids, travel_mode,
          directionsService, directionsDisplay);

    document.getElementById('map_holder').style.width = "50%";
  });

  function route(origin_place_id, destination_place_id, way_point_ids,
                 travel_mode, directionsService, directionsDisplay) {
    if (!origin_place_id || !destination_place_id) {
      return;
    }
    waypoints = []
    for (var i=0; i < way_point_ids.length; ++i) {
      waypoints.push({'location': {'placeId': way_point_ids[i]}, 'stopover': true });
    }
    directionsService.route({
      origin: {'placeId': origin_place_id},
      destination: {'placeId': destination_place_id},
      waypoints: waypoints,
      optimizeWaypoints: true,
      travelMode: travel_mode
    }, function(response, status) {
      if (status === 'OK') {
        directionsDisplay.setDirections(response);
      } else {
        window.alert('Directions request failed due to ' + status);
      }
    });
  }
}

