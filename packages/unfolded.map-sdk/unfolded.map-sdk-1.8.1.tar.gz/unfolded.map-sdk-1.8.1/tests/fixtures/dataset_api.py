DUMMY_MESSAGE_UUID = "ede3fafc-4945-41b7-ac64-16faa896a47a"
LAYER_UUID = "997c21eb-604b-49df-add9-b2fcc615a243"

LOCAL_RESPONSE = {
    "id": "2853b4cf-005f-47f5-a6f0-54d275e77d9c",
    "label": "earthquakes",
    "color": [0, 92, 255],
    "fields": [
        {
            "name": "DateTime",
            "label": "DateTime",
            "type": "timestamp",
            "timeFormat": "YYYY/M/D HH:mm:ss.SSSS",
        },
        {"name": "Latitude", "label": "Latitude", "type": "real"},
        {"name": "MagType", "label": "MagType", "type": "string"},
        {"name": "NbStations", "label": "NbStations", "type": "integer"},
    ],
    "type": "local",
}

VECTOR_TILE_RESPONSE = {
    "id": "56a78675-5729-449e-8961-1b0f30562f4f",
    "label": "Test",
    "color": [143, 47, 191],
    "fields": [
        {"name": "AGE_21_64", "label": "AGE_21_64", "type": "real"},
    ],
    "type": "vector-tile",
    "metadata": {
        "dataUrl": "https://storage.googleapis.com/unfolded_public/vector-tile/cb_v2",
        "metadataUrl": "https://storage.googleapis.com/unfolded_public/vector-tile/cb_v2/metadata.json",
        "id": "56a78675-5729-449e-8961-1b0f30562f4f",
        "format": "",
        "label": "Test",
        "metaJson": {
            "vector_layers": [
                {
                    "id": "ny_age_s20",
                    "description": "",
                    "minzoom": 7,
                    "maxzoom": 10,
                    "fields": {
                        "AGE_21_64": "Number",
                    },
                },
            ],
            "tilestats": {
                "layerCount": 53,
                "layers": [
                    {
                        "layer": "ny_age_s20",
                        "count": 241486,
                        "geometry": "Polygon",
                        "attributeCount": 4,
                        "attributes": [
                            {
                                "attribute": "AGE_21_64",
                                "count": 1000,
                                "type": "number",
                                "values": [
                                    0,
                                    0.002849002849002849,
                                    0.0034602076124567475,
                                    0.006289308176100629,
                                    0.007861635220125786,
                                    0.008,
                                    0.046822742474916385,
                                    0.048314606741573035,
                                ],
                                "min": 0,
                                "max": 1,
                            },
                        ],
                    },
                ],
            },
        },
        "bounds": [-176.684659, 17.926837, 174.144841, 71.334586],
        "center": [-74.003906, 40.846927, 10],
        "maxZoom": 10,
        "minZoom": 0,
        "fields": [
            {
                "name": "AGE_21_64",
                "id": "AGE_21_64",
                "format": "",
                "filterProps": {
                    "fieldType": "real",
                    "domain": [0, 1],
                    "histogram": None,
                    "value": [0, 1],
                    "type": "range",
                    "typeOptions": ["range"],
                    "gpu": True,
                    "step": 0.001,
                },
                "type": "real",
                "analyzerType": "FLOAT",
            },
        ],
        "name": "_DEL_POP/ALL",
        "description": "_DEL_POP/ALL",
    },
}

RASTER_TILE_RESPONSE = {
    "id": "f65ce936-cc3c-4de2-9914-290c93d786e6",
    "label": "Test",
    "color": [192, 108, 132],
    "fields": [],
    "type": "raster-tile",
    "metadata": {
        "metadataUrl": "https://raw.githubusercontent.com/UnfoldedInc/examples/master/raster/planet-skysat-opendata.json",
        "id": "20201213_045438_ss01_u0001",
        "format": "",
        "label": "Test",
        "type": "Feature",
        "stac_version": "1.0.0",
        "stac_extensions": [
            "https://stac-extensions.github.io/eo/v1.0.0/schema.json",
            "https://stac-extensions.github.io/raster/v1.0.0/schema.json",
            "https://stac-extensions.github.io/view/v1.0.0/schema.json",
        ],
        "properties": {
            "providers": [
                {
                    "name": "Planet",
                    "description": "Contact Planet at [planet.com/contact-sales](https://www.planet.com/contact-sales/)",
                    "roles": ["producer", "processor"],
                    "url": "http://planet.com",
                }
            ],
            "gsd": 1.01,
            "created": "2020-12-13T09:20:24Z",
            "updated": "2020-12-13T09:20:24Z",
            "constellation": "skysat",
            "platform": "SS01",
            "eo:cloud_cover": 0,
            "view:off_nadir": 25.5,
            "view:sun_azimuth": 159.8,
            "view:sun_elevation": 42.4,
            "pl:clear_confidence_percent": 59,
            "pl:clear_percent": 28,
            "pl:cloud_percent": 0,
            "pl:ground_control_ratio": 0.95,
            "pl:heavy_haze_percent": 0,
            "pl:item_type": "SkySatCollect",
            "pl:light_haze_percent": 72,
            "pl:pixel_resolution": 0.5,
            "pl:publishing_stage": "finalized",
            "pl:quality_category": "test",
            "pl:satellite_azimuth": 141.7,
            "pl:shadow_percent": 0,
            "pl:snow_ice_percent": 0,
            "pl:strip_id": "s1_20201213T045438Z",
            "pl:visible_confidence_percent": 59,
            "pl:visible_percent": 100,
            "datetime": "2020-12-13T04:54:38.312000Z",
        },
        "geometry": {
            "coordinates": [
                [
                    [88.80278308162045, 21.713415693279156],
                    [88.80313138501904, 21.71337310737007],
                    [88.80317550773762, 21.700562568435377],
                ]
            ],
            "type": "Polygon",
        },
        "links": [
            {"rel": "root", "href": "../collection.json", "type": "application/json"},
            {
                "rel": "collection",
                "href": "../collection.json",
                "type": "application/json",
            },
            {"rel": "parent", "href": "../collection.json", "type": "application/json"},
        ],
        "assets": {
            "visual:ortho_visual": {
                "href": "https://storage.googleapis.com/open-cogs/planet-stac/20201213_045438_ss01_u0001/20201213_045438_ss01_u0001_visual_file_format.tif",
                "type": "image/tiff; application=geotiff; profile=cloud-optimized",
                "roles": ["data"],
                "eo:bands": [
                    {"name": "Blue", "common_name": "blue"},
                ],
                "raster:bands": [
                    {"data_type": "uint8"},
                ],
            },
            "metadata": {
                "href": "https://storage.googleapis.com/open-cogs/planet-stac/20201213_045438_ss01_u0001/20201213_045438_ss01_u0001_metadata.json",
                "type": "application/json",
                "roles": ["metadata"],
            },
        },
        "bbox": [
            88.7123238494617,
            21.700562568435377,
            88.80317550773762,
            21.89915173899179,
        ],
        "collection": "planet-stac-skysat",
    },
}
