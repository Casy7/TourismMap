$(document).ready(function() {
    $("button").click(function() {
        $("#apartado-api").toggle();
    });
});

function initMap() {
    var map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: 40.416775, lng: -3.703790 },
        zoom: 12
    });
    map.data.loadGeoJson('map.json');
}