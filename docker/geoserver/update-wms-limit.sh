#!/bin/bash

# Uaktualnij zapisany limit WMS wartością ustawioną w Compose.
config="${GEOSERVER_DATA_DIR}/controlflow.properties"
sed -i "s|^user\.ows\.wms\.getmap=.*|user.ows.wms.getmap=${USER_WMS_REQUEST}|" "$config"
