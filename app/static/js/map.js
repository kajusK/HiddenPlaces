class MyMap {
    /**
     * Creates leaflet map tied to given div
     *
     * @param {str} divId   ID of the div to draw map to
     */
    constructor(divId) {
        this.map = L.map(divId).setView([49.8, 15.5], 8);

        L.tileLayer('https://mapserver.mapy.cz/turist-m/{z}-{x}-{y}', {
            attribution: '&copy; <a href="https://www.mapy.cz">Mapy.cz</a>',
            minZoom: 3,
            maxZoom: 19
        }).addTo(this.map);

        L.control.scale({
            imperial: false,
            maxWidth: 200
        }).addTo(this.map);

        this.markers = L.markerClusterGroup();
        this.map.addLayer(this.markers);
    }

    /**
     * Force map redrawing when parent container dimensions changed
     */
    redraw() {
        this.map.invalidateSize()
    }

    /**
     * Fetches data from JSON endpoint
     *
     * @param {str} url    URL of the endpoint to fetch data from
     */
    fetchLocations(url) {
        let request = new XMLHttpRequest();
        let markers = this.markers

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
        }

        request.open("GET", url)
        request.send();
    }

    /**
     * Shows current user location (must enable localization in browser)
     */
    showLocation(zoom=false) {
        /* TODO set icon */
        this.map.on('locationfound', (e) => {
            let radius = e.accuracy

            L.marker(e.latlng).addTo(this.map)
            L.circle(e.latlng, radius).addTo(this.map)
        })
        this.map.locate({setView: zoom, maxZoom: 14});
    }

    /**
     * Adds marker to given position
     *
     * @param {latlng} latlng       Position of marker
     * @param {str} title           Title of the marker
     */
    addMarker(latlng, title="") {
        L.marker(latlng, {title: title}).addTo(this.markers)
    }

    /**
     * Zoom to the given position on map
     *
     * @param {latlng} latlng       Position to zoom to
     */
    zoomPosition(latlng) {
        this.map.setView(latlng, 14)
    }

    /**
     * Removes all markers
     */
    clearMarkers() {
        this.map.removeLayer(this.markers);
        this.markers = L.markerClusterGroup();
        this.map.addLayer(this.markers);
    }
}
