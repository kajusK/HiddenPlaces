var map = L.map('map').setView([49.8, 15.5], 8);

L.tileLayer('https://mapserver.mapy.cz/turist-m/{z}-{x}-{y}', {
	attribution: '&copy; <a href="https://www.mapy.cz">Mapy.cz</a>',
	minZoom: 7,
	maxZoom: 19
}).addTo(map);

scale = L.control.scale({
	imperial: false,
    maxWidth: 200
}).addTo(map);

var markers = L.markerClusterGroup();

let request = new XMLHttpRequest();
request.onload = function() {
    let data = JSON.parse(this.responseText);
    data.locations.forEach(location => {
        let marker = L.marker([location.latitude, location.longitude], {title: location.name});
        marker.bindPopup(`
            <div style="min-width: 200px">
                <img src="${location.image}" style="width: 100%">
                <h4 class="mt-2">
                    <a href="/location/${location.id}">${location.name}</a>
                </h4>
                <p class="overflow-hidden" style="display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 4;">
                    ${location.description}
                </p>
            </div>
        `);
        markers.addLayer(marker);
    })
    map.addLayer(markers);
}

request.open("GET", map_api_url)
request.send();
