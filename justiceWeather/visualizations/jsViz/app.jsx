import React, { useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import { Map } from 'react-map-gl';
import maplibregl from 'maplibre-gl';
import DeckGL from '@deck.gl/react';
import { GridLayer } from '@deck.gl/aggregation-layers';

const MALE_COLOR = [0, 128, 255];
const FEMALE_COLOR = [255, 0, 128];

const DATA_URL = 'http://127.0.0.1:5000/get_data';

const INITIAL_VIEW_STATE = {
    longitude: -74,
    latitude: 40.7,
    zoom: 11,
    maxZoom: 16,
    pitch: 0,
    bearing: 0
};

export default function App({
    radius = 30,
    maleColor = MALE_COLOR,
    femaleColor = FEMALE_COLOR,
    mapStyle = 'https://basemaps.cartocdn.com/gl/positron-nolabels-gl-style/style.json'
}) {
    const [data, setData] = useState([]);

    useEffect(() => {
        // Fetch data when the component mounts
        const fetchData = async () => {
            try {
                console.log("fetching data");
                const response = await fetch(DATA_URL);
                console.log('resonse codde: ', response.status);
                console.log("response: ", response);
                const jsonData = await response.json();
                console.log("jsonData: ", jsonData);
                setData(jsonData);
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        };

        fetchData();
    }, []); // Empty dependency array ensures that this effect runs once on mount

    const layers = [
        new GridLayer({
            id: 'grid-of-emotions',
            data,
            radiusScale: radius,
            radiusMinPixels: 0.25,
            getPosition: d => [d["Latitude"], d["Longitude"], 0],
            getFillColor: d => (d['color']),
            getRadius: 1,
            updateTriggers: {
                getFillColor: [maleColor, femaleColor]
            }
        })
    ];

    return (
        <DeckGL layers={layers} initialViewState={INITIAL_VIEW_STATE} controller={true}>
            <Map reuseMaps mapLib={maplibregl} mapStyle={mapStyle} preventStyleDiffing={true} />
        </DeckGL>
    );
}

export function renderToDOM(container) {
    createRoot(container).render(<App />);
}
