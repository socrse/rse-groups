/*
 * SPDX-FileCopyrightText: © 2022 Matt Williams <matt@milliams.com>
 * SPDX-License-Identifier: MIT
 */

async function create_map(div) {
    var map = L.map(div).setView([54, -4.], 6);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap contributors</a>',
        maxZoom: 18,
    }).addTo(map);
    const requestURL = 'groups.json';
    const request = new Request(requestURL);

    const response = await fetch(request);
    const rse_groups = await response.json();

    populateMap(map, rse_groups);
}

var headers = {
    "head" : "Head of RSE",
    "phone" : "Contact number",
    "email" : "Contact email",
    "postcode" : "Location",
    "website" : "Website",
    "twitter" : "Twitter Handle"
}

function onEachFeature(feature, layer) {
    // does this feature have a property named popupContent?
    if (feature.properties) {
        var html = [];
        html.push(`<b>${feature.properties["name"]}</b><br>\n`)
        html.push("<dl>")
        for (const header in headers) {
            if (feature.properties[header]) {
                html.push(`<dt>${headers[header]}</dt>`)
                html.push(`<dd>${feature.properties[header]}</dd>`)
            }
        }
        html.push("</dl>")
        layer.bindPopup(html.join("\n"));
    }
}

function populateMap(map, data) {
    for (const group of data) {
        L.geoJSON(group, {
            onEachFeature: onEachFeature
        }).addTo(map);
    }
}
