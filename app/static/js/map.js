class MyMap {
    /**
     * Creates leaflet map tied to given div
     *
     * @param {str} divId   ID of the div to draw map to
     */
    constructor(divId) {
        const opacity = 0.8

        const tourist = L.tileLayer('https://mapserver.mapy.cz/turist-m/{z}-{x}-{y}', {
            attribution: '&copy; <a href="https://www.mapy.cz">Mapy.cz</a>',
            minZoom: 3,
            maxZoom: 19
        })

        const baseMaps = {
            "Tourists": tourist,
            "Aerial": L.esri.dynamicMapLayer({
                url: 'https://ags.cuzk.cz/arcgis/rest/services/ortofoto/MapServer',
            }),
            "None":  L.tileLayer('')
        }

        const overlays = {
            "Relief": L.esri.imageMapLayer({
                    url: 'https://ags.cuzk.cz/arcgis/rest/services/3D/dmr5g_wm/ImageServer',
                    opacity: opacity
                }),
            "History": L.layerGroup([
                L.esri.tiledMapLayer({
                    url: 'https://gis.msk.cz/arcgis/rest/services/podklad/podklad_cis_otisky_wm/MapServer',
                    opacity: opacity
                }),
                L.esri.dynamicMapLayer({
                    url: 'https://gis.kraj-jihocesky.gov.cz/arcgis/rest/services/podkladove/Cisarske_otisky/MapServer',
                    opacity: opacity
                }),
            ]),
            "Mines": L.layerGroup([
                L.esri.dynamicMapLayer({
                    url: 'https://mapy.geology.cz/arcgis/rest/services/Dulni_Dila/dulni_dila/MapServer'
                }),
                L.esri.dynamicMapLayer({
                    url: 'https://ags.geology.sk/arcgis/rest/services/Geofond/sbd_vect/MapServer'
                }),
            ]),
            "Undermined": L.esri.dynamicMapLayer({
                url: 'https://mapy.geology.cz/arcgis/rest/services/Popularizace/pozustatky_po_tezbe/MapServer',
                layers: [2]
            }),
            "Quarries": L.esri.dynamicMapLayer({
                url: 'https://mapy.geology.cz/arcgis/rest/services/Popularizace/dekoracni_kameny/MapServer',
                layers: [0]
            }),
            "Geology": L.esri.tiledMapLayer({
                url: 'https://mapy.geology.cz/arcgis/rest/services/Geologie/GEOCR50_mobil/MapServer',
                opacity: opacity
            }),
        }

        this.map = L.map(divId, {
            center: [49.8, 15.5],
            zoom: 8,
            layers: [tourist]
        })
        L.control.layers(baseMaps, overlays).addTo(this.map);

        L.control.scale({
            imperial: false,
            maxWidth: 200
        }).addTo(this.map);

        L.control.locate({
            follow: true,
            locateOptions: {maxZoom: 14},
            icon: 'bi bi-geo-alt',
            enableHighAccuracy: true,
            maximumAge: 10000,
            timeout: 15000,
            strings: {
                title: "GPS"
            }
        }).addTo(this.map);

        L.control.ruler().addTo(this.map);

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
        const request = new XMLHttpRequest();
        const markers = this.markers
        const map = this.map

        request.onload = function() {
            const types = new Set()
            const states = new Set()
            const accessibility = new Set()
            const data = JSON.parse(this.responseText);

            data.locations.forEach(location => {
                let marker = L.marker([location.latitude, location.longitude], {
                    title: location.name,
                    tags: [location.type, location.state, location.accessibility]
                });
                types.add(location.type)
                states.add(location.state)
                accessibility.add(location.accessibility)

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
                marker.bindTooltip(location.name)
                markers.addLayer(marker);

            })

            /* Add filter buttons with types/states received */
            const clearText = "Reset"
            const typeFilter = L.control.tagFilterButton({
                data: [...types],
                icon: '<i class="bi bi-house-door">',
                filterOnEveryClick: true,
                clearText: clearText
            });
            const stateFilter = L.control.tagFilterButton({
                data: [...states],
                icon: '<i class="bi bi-wrench">',
                filterOnEveryClick: true,
                clearText: clearText
            });
            const accessibilityFilter = L.control.tagFilterButton({
                data: [...accessibility],
                icon: '<i class="bi bi-door-closed">',
                filterOnEveryClick: true,
                clearText: clearText
            });
            typeFilter.addTo(map)
            typeFilter.enableMCG(markers)
            stateFilter.addTo(map)
            stateFilter.enableMCG(markers)
            accessibilityFilter.addTo(map)
            accessibilityFilter.enableMCG(markers)

            /* Close filter for when other button is clicked */
            const elements = Array.from(document.getElementsByClassName("easy-button-button"))
            elements.forEach(button => {
                button.addEventListener("click", (event) => {
                    const containers = Array.from(document.getElementsByClassName("tag-filter-tags-container"))
                    containers.forEach(container => {
                        if (container.parentElement != event.currentTarget.parentElement) {
                            container.style.display = "none"
                        }
                    })
                })
            })

        }

        request.open("GET", url)
        request.send();
    }

    /**
     * Adds marker to given position
     *
     * @param {latlng} latlng       Position of marker
     * @param {str} title           Title of the marker
     */
    addMarker(latlng, title="", tooltip=false) {
        const marker = L.marker(latlng, {title: title})
        marker.bindTooltip(title, { permanent: tooltip })
        marker.addTo(this.markers)
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
