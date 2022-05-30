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
            "Turistická": tourist,
            "Letecká": L.esri.dynamicMapLayer({
                url: 'https://ags.cuzk.cz/arcgis/rest/services/ortofoto/MapServer',
            }),
            "None":  L.tileLayer('')
        }

        const czechMines = L.esri.dynamicMapLayer({
            url: 'https://mapy.geology.cz/arcgis/rest/services/Dulni_Dila/dulni_dila/MapServer'
        })
        const slovakMines = L.esri.dynamicMapLayer({
            url: 'https://ags.geology.sk/arcgis/rest/services/Geofond/sbd_vect/MapServer'
        })
        const underminedAreas = L.esri.dynamicMapLayer({
            url: 'https://mapy.geology.cz/arcgis/rest/services/Popularizace/pozustatky_po_tezbe/MapServer',
            layers: [2]
        })
        const quaries = L.esri.dynamicMapLayer({
            url: 'https://mapy.geology.cz/arcgis/rest/services/Popularizace/dekoracni_kameny/MapServer',
            layers: [0]
        })
        const caves = L.esri.dynamicMapLayer({
            url: 'https://gis.nature.cz/arcgis/rest/services/JESO/JesoVerejnost/MapServer/',
            layers: [1,2,4,11]
        })

        const overlays = {
            "Relief": L.esri.imageMapLayer({
                    url: 'https://ags.cuzk.cz/arcgis/rest/services/3D/dmr5g_wm/ImageServer',
                    opacity: opacity
                }),
            "Geologická": L.esri.tiledMapLayer({
                url: 'https://mapy.geology.cz/arcgis/rest/services/Geologie/GEOCR50_mobil/MapServer',
                opacity: opacity
            }),
            "Císařské otisky": L.layerGroup([
                L.esri.tiledMapLayer({
                    url: 'https://gis.msk.cz/arcgis/rest/services/podklad/podklad_cis_otisky_wm/MapServer',
                    opacity: opacity
                }),
                L.esri.dynamicMapLayer({
                    url: 'https://gis.kraj-jihocesky.gov.cz/arcgis/rest/services/podkladove/Cisarske_otisky/MapServer',
                    opacity: opacity
                }),
            ]),
            "II. vojenské mapování": L.esri.dynamicMapLayer({
                url: 'http://ns.cenia.cz/arcgis/rest/services/CENIA/cenia_rt_II_vojenske_mapovani/MapServer'
            }),
            "III. vojenské mapování": L.esri.dynamicMapLayer({
                url: 'http://ns.cenia.cz/arcgis/rest/services/CENIA/cenia_rt_III_vojenske_mapovani/MapServer'
            }),
            "Katastr": L.tileLayer.wms('http://services.cuzk.cz/wms.asp', {
                layers: 'RST_KN,RST_KMD,dalsi_p_mapy,hranice_parcel,obrazy_parcel,parcelni_cisla',
                format: 'image/png',
                transparent: true
            }),
            "Doly": L.layerGroup([czechMines, slovakMines]),
            "Poddolovaná území": underminedAreas,
            "Lomy": quaries,
            "Jeskyně": caves,
        }

        this.map = L.map(divId, {
            renderer: L.canvas({tolerance: 40}),
            center: [49.8, 15.5],
            zoom: 8,
            layers: [tourist, overlays['Doly']]
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

        czechMines.bindPopup(this.showItemPopup)
        slovakMines.bindPopup(this.showItemPopup)
        underminedAreas.bindPopup(this.showItemPopup)
        quaries.bindPopup(this.showItemPopup)
        caves.bindPopup(this.showItemPopup)
    }

    /**
     * Show popup with item information
     */
    showItemPopup(error, collection) {
        if (error || collection.features.length == false) {
            return false
        }

        const feature = collection.features[0].properties
        if ('Názov ložiska' in feature) {
            return `
                Název: ${feature['Názov ložiska']}</br>
                Surovina: ${feature['Nerast']}</br>
                `
        } else if ('Prejav na povrchu' in feature) {
            return `
                Název: ${feature['Názov']}</br>
                Typ: ${feature['Typ objektu']}</br>
                Projev na povrchu: ${feature['Prejav na povrchu']}<br/>
                Surovina: ${feature['Špecifikácia suroviny']}</br>
                Sanace: ${feature['Sanácia']}</br>
                Rozměr objektu: ${feature['Odhadovaný rozmer objektu']}</br>
                `
        } else if ('ID důlního díla' in feature) {
            MyMap.fetchGeofondPhotos(feature['ID důlního díla'])
            return `
                Název: ${feature['Název']}</br>
                ID: <a href="https://app.geology.cz/dud_foto/foto_dd.php?id_=${feature['ID důlního díla']}" target="_blank">${feature['ID důlního díla']}</a><br/>
                Typ: ${feature['Druh díla']}<br/>
                Délka: ${feature['Hloubka / délka']}</br>
                Profil díla: ${feature['Profil díla']}</br>
                Rok ukončení provozu: ${feature['Rok ukončení provozu']}</br>
                Surovina: ${feature['Surovina']}</br>
                <div id='geofond_photos'>
                </div>
                `
        } else if ('Klíč' in feature) {
            return `
                Název: ${feature['Název']}</br>
                Surovina: ${feature['Surovina']}</br>
                Projevy: ${feature['Projevy']}<br/>
                Stáří: ${feature['Stáří']}</br>
                `
        } else if ('KOD_JESO' in feature) {
            console.log(feature)
            return `
                Kód JESO: <a href="https://jeso.nature.cz/?jeso=${feature['ID_JESO']}" target="_blank">${feature['KOD_JESO']}</a></br>
                Název: ${feature['NAZEV_JEVU'] || feature['NAZEV']}</br>
                Synonymum: ${feature['SYNONYMUM'] || feature['SYNONYMUM_JEVU']} </br>
                Typ: ${feature['GENEZE'] || feature['GENEZE_JEVU'] || "Speleologický objekt"}</br>
                `
        } else {
            return `
                Název: ${feature['Název']}</br>
                Popis: ${feature['Popis']}</br>
                Surovina: ${feature['Těžená surovina']}<br/>
            `
        }
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
     * Fetches list of geofond photos from JSON endpoint
     *
     * @param {str} object_id    ID of the location object
     */
    static fetchGeofondPhotos(object_id) {
        const request = new XMLHttpRequest();

        request.onload = function() {
            const data = JSON.parse(this.responseText);
            const el = document.getElementById('geofond_photos')
            let content = "<div class='row gallery'>"
            data.photos.forEach(photo => {
                content += `
                    <div class="col-6 p-1">
                        <div class="position-relative">
                            <a href="${photo.url}" data-caption="${photo.title}">
                                <div class="image-caption d-flex">
                                    <span class="text-truncate">${photo.title}</span>
                                </div>
                                <img src="${photo.thumbnail}" alt="${photo.title}" style="width: 100%"/>
                            </a>
                        </div>
                    </div>
                `
            })
            content += '</div>'
            el.innerHTML = content

            /* Reload baguette box, change filter to match href from geofond */
            baguetteBox.destroy()
            baguetteBox.run('.gallery', { filter: /download_file.php/i })
        }

        request.open("GET", `/api/geofond_photos/${object_id}`)
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
