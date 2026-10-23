import { AfterViewInit, Component, effect, inject, signal} from '@angular/core';
import Map from 'ol/Map';
import OSM from 'ol/source/OSM';
import TileLayer from 'ol/layer/Tile';
import View from 'ol/View';
import { fromLonLat, get } from 'ol/proj';
import VectorImageLayer from 'ol/layer/VectorImage';
import VectorSource from 'ol/source/Vector';
import GeoJSON from 'ol/format/GeoJSON';
import { Style, Text, Fill, Stroke, Circle as CircleStyle } from 'ol/style';
import Feature, { FeatureLike } from 'ol/Feature';
import TileWMS from 'ol/source/TileWMS';
import { LayerVisibility, LayerKey } from '../../../services/layer-visibility/layer-visibility';
import { InfoToggle } from '../../../services/info-toggle/info-toggle';
import { InfoComponent } from '../geoportal-headbar/info-component/info-component';
import { InfoFeatures } from '../../../services/info-features/info-features';
import { ZoomToObject } from '../../../services/zoom-to-object/zoom-to-object';
import { ObjSelection } from '../../../services/obj-selection/obj-selection';
import { getAuth } from 'firebase/auth';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs/internal/firstValueFrom';
import { AMService } from '../../../services/a-m-service/a-m-service';
import { AttributeTableToolbarService } from '../../../services/attribute-table-toolbar-service/attribute-table-toolbar-service';

@Component({
  selector: 'app-map-component',
  imports: [InfoComponent],
  templateUrl: './map-component.html',
  styleUrl: './map-component.scss',
})
export class MapComponent implements AfterViewInit {
  private mapLayersVisibility = inject(LayerVisibility);
  private infoToggleService = inject(InfoToggle);
  public infoProperties = inject(InfoFeatures);
  private osmLayer!: TileLayer;
  private ortoLayer!: TileLayer;
  private budLayer!: TileLayer;
  private boundsLayerCities!: TileLayer;
  private boundsLayerGminy!: TileLayer;
  private boundsLayerPowiaty!: TileLayer;
  private boundsLayerWojewodz!: TileLayer;
  private boundsLayerPanstwo!: TileLayer;
  public map!: Map;
  private vectorLayer!: VectorImageLayer;
  private vectorSource!: VectorSource;
  private zoomToObject = inject(ZoomToObject);
  public vectorResults = inject(LayerVisibility).vectorResults;
  private AMService = inject(AMService);
  private ToolbarService = inject(AttributeTableToolbarService);

  private showLabel!: boolean;


  constructor() {
    effect(() => {
      if (this.objectSelection.passedId()) {
        const existing = this.map.getLayers().getArray().find((l) => l.get('layerKey') === 'highlightedObjectsLayer');
        if (existing) {
          this.map.removeLayer(existing);
        }
        this.objectSelection.deleteObjFromSelection(this.objectSelection.passedId()).then((newLayer) => {
          this.map.addLayer(newLayer);
        });
      }
    });

    effect(() => {
      const visibility = this.mapLayersVisibility.layersVisibility();
      this.vectorLayer?.setVisible(visibility.vectorLayer);
      this.osmLayer?.setVisible(visibility.osmLayer);
      this.ortoLayer?.setVisible(visibility.ortoLayer);
      this.budLayer?.setVisible(visibility.budLayer);
      this.boundsLayerCities?.setVisible(visibility.boundsLayerCities);
      this.boundsLayerGminy?.setVisible(visibility.boundsLayerGminy);
      this.boundsLayerPowiaty?.setVisible(visibility.boundsLayerPowiaty);
      this.boundsLayerWojewodz?.setVisible(visibility.boundsLayerWojewodz);
      this.boundsLayerPanstwo?.setVisible(visibility.boundsLayerPanstwo);
    });

    // Handling for analysis selection and map layers visibility
    effect(() => {
      this.mapLayersVisibility.layersVisibility();
      if (this.map) {
        this.objectSelection.resetMapLayers();
        this.objectSelection.getMapLayers(this.map.getLayers());
      }
    });
    effect(() => {
      this.objectSelection.selectedObjects();
      if (this.vectorLayer) {
        this.vectorLayer.changed();
      }
    });
    effect(() => {
      this.AMService.mapResolution();
      this.vectorLayer?.changed();
    })
  }


  public objectSelection = inject(ObjSelection);
  ngAfterViewInit(): void {
    this.osmLayer = new TileLayer({
      source: new OSM({attributions:[]}),
    });

    this.ortoLayer = this.tileLayer('ortoLayer', 'ORTOFOTOMAPA');
    this.budLayer = this.tileLayer('budLayer', 'budynki');
    this.boundsLayerPanstwo = this.tileLayer('boundsLayerPanstwo', 'boundspanstwo');
    this.boundsLayerWojewodz = this.tileLayer('boundsLayerWojewodz', 'boundswojewodz');
    this.boundsLayerPowiaty = this.tileLayer('boundsLayerPowiaty', 'boundspowiaty');
    this.boundsLayerGminy = this.tileLayer('boundsLayerGminy', 'boundsgminy');
    this.boundsLayerCities = this.tileLayer('boundsLayerCities', 'boundscities');
    this.vectorLayer = this.buildVectorLayer();

    this.zoomToObject.vectorLayer(this.vectorLayer);
    this.map = new Map({
      target: 'map',
      controls: [],
      layers: [
        this.osmLayer,
        this.ortoLayer,
        this.budLayer,
        this.boundsLayerPanstwo,
        this.boundsLayerWojewodz,
        this.boundsLayerPowiaty,
        this.boundsLayerGminy,
        this.boundsLayerCities,
        this.vectorLayer
      ],
      view: new View({
        center: fromLonLat([19.3, 52.2]),
        zoom: 7,
      }),
    });
    this.zoomToObject.setMap(this.map);
    this.AMService.getMap(this.map);
    this.ToolbarService.getMapComponent(this.map);
    this.objectSelection.getMapLayers(this.map.getLayers());
    
    this.map.on('singleclick', (event) => {
      this.objectSelection.isSelectionPicked.set(true);
      if (this.infoToggleService.isInfoClicked()) {
        this.infoProperties.clear(); // Reset properties before fetching new data
        this.infoProperties.isInfoReady.set(false); // Reset info ready state before fetching new data


        const viewResolution = this.map.getView().getResolution();
        if (!viewResolution) {
          this.infoProperties.isInfoReady.set(true); // Set info ready state to true if resolution is not available
          return;
        }

        // Łapanie kliknięcia warstwy miejscowości
        this.vectorResults.set([]); 
        this.map.forEachFeatureAtPixel(event.pixel, (feature, layer) => {
          if (layer === this.vectorLayer) {
            const feat = feature.getProperties();
            this.vectorResults.update(f => [...f, feat]);
            console.log("COKOLWIEKTRAFIONE", feature.getProperties())
            console.log(this.vectorResults())
          }
          return false;
          }, { hitTolerance: 50 }
       );
       // -----------------------------------------
       //Dodać do props to co jest w vectorResults



        const requests: Promise<void>[] = [];

        this.map.getLayers().forEach((layer) => {
          if (layer instanceof TileLayer && layer.getVisible()) {
            const source = layer.getSource();
            if (source instanceof TileWMS) {
              const url = source.getFeatureInfoUrl(
                event.coordinate,
                viewResolution,
                'EPSG:3857',
                { INFO_FORMAT: 'application/json' }
              );

              if (url) {
                const request = fetch(url)
                  .then((response) => response.json())
                  .then((data) => {
                    console.log('WMS Dane DATA dla debugu:', data);
                    if (data.features && data.features.length > 0 && data.features[0].id) {
                      this.infoProperties.updateLayerWithId(data.features[0].id);
                      console.log('Zebrane ID warstwy:', this.infoProperties.layerWithId());
                    } else {
                      console.log('Layer doesnt have an ID or features are missing:', data);
                    }
                    if (data.features && data.features.length > 0) {
                      data.features.forEach((feature: any) => {
                        this.infoProperties.updateProperties([feature.properties]);
                      });
                      console.log('Zebrane właściwości:', this.infoProperties.properties());
                    } else {
                      console.log('No features found at this location.');
                    }
                    console.log('WMS Feature Info NO IF:', data);
                  })
                  .catch((error) => {
                    console.error('Error fetching WMS Feature Info:', error);
                  });
                requests.push(request);
              }
            }
          }
        });
        Promise.all(requests).then(() => {
          this.infoProperties.isInfoReady.set(true); // Set the info ready state after fetching data
        });

















      } else if (this.objectSelection.analysisNrPicked() === 'selection' && this.objectSelection.selectedSelectOptionLayer() !== '' && this.objectSelection.isSelectionPicked()) {
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////// 
        console.log('YuupiCayo! Works for now');
        this.objectSelection.resetSelectedOption();
        const viewResolution = this.map.getView().getResolution();
        if (!viewResolution) return;
        // Widzialne warstwy:
        this.objectSelection.visibleMapLayers().forEach((layer) => {







          if (layer instanceof TileLayer && layer.getVisible()) {
            const source = layer.getSource();
            if (source instanceof TileWMS && this.objectSelection.selectedSelectOptionLayer() === layer.get('layerKey')) {
              const url = source.getFeatureInfoUrl(
                event.coordinate,
                viewResolution,
                'EPSG:3857',
                { INFO_FORMAT: 'application/json' }
                
            )

            //Dodać to gdyby było potrzebne sprawdzenie czy dane są gotowe do wyświetlenia
            const requests: Promise<void>[] = [];

            if (url) {
                fetch(url)
                .then((response) => response.json())
                .then((data) => {
                    if (data.features && data.features.length > 0) {``
                      this.toggleSelection(data, event.originalEvent.ctrlKey || event.originalEvent.metaKey);
                    }
                    console.log('WMS Feature Info for SELECTION:', data);
                })
                .catch((error) => {
                    console.error('Error fetching WMS Feature Info for SELECTION:', error);
                });
            }
          };
          }
          if (layer instanceof VectorImageLayer && layer.getVisible() && this.objectSelection.selectedSelectOptionLayer() === 'vectorLayer') {
            // Szukamy czy cokolwiek mieści się w tolerancji kliknięcia
            const hitFeatures = this.map.getFeaturesAtPixel(event.pixel, {
              layerFilter: (l) => l === layer,
              hitTolerance: 50
            });

            if (hitFeatures && hitFeatures.length > 0) {
              // Pobierz z warstwy obiekt, który znajduje się centralnie najbliżej punktu kliknięcia
              const clickedFeature = layer.getSource().getClosestFeatureToCoordinate(event.coordinate) as Feature;
              
              if (clickedFeature) {
                // Pobieramy ID w formacie 'layer.id' (np. 'sql_data.123') lub wyciągamy z właściwości
                let featureId = clickedFeature.getId() as string;
                if (!featureId) {
                   featureId = 'vectorLayer.' + clickedFeature.get('id'); // Próba ratunku, jeśli getId() jest puste
                }

              // Tworzymy mock-obiekt, by upodobnić odpowiedź do WMS GetFeatureInfo
              const mockData = {
                features: [
                  {
                    id: featureId,
                    properties: clickedFeature.getProperties()
                  }
                ]
              };
              this.toggleSelection(mockData, event.originalEvent.ctrlKey || event.originalEvent.metaKey);


              }
            }
          }
        });


























      } else {
        console.log('Info and selection by hand are not active, no action taken.');
      }
    });
    
  }

  private addOrReplaceHighlightedLayer(newLayer: TileLayer): void {
    const existing = this.map.getLayers().getArray().find((l) => l.get('layerKey') === 'highlightedObjectsLayer');
    if (existing) {
      this.map.removeLayer(existing);
    }
    this.map.addLayer(newLayer);
  }

private toggleSelection(featureData: any, isMultiSelect: boolean): void {
    let isAlreadySelected = false;
    const currentSelected = this.objectSelection.selectedObjects();
    let newSelected = [...currentSelected];

    const newIdNum = featureData.features[0].id.split('.')[1];

    // Sprawdź czy kliknięty obiekt jest już zaznaczony (niezależnie od prefiksu warstwy)
    for (let i = 0; i < currentSelected.length; i++) {
        const currentIdNum = currentSelected[i].features[0].id.split('.')[1];
        if (currentIdNum === newIdNum) {
            isAlreadySelected = true;
            if (isMultiSelect) {
                // Jeśli CTRL i był zaznaczony -> odznaczamy
                newSelected.splice(i, 1);
                console.log('Obiekt odznaczony.');
            }
            break;
        }
    }

    if (!isMultiSelect && !isAlreadySelected) {
        // Jeśli brak CTRL i nie był zaznaczony -> zaznacz tylko jego
        newSelected = [featureData];
        console.log('Zaznaczanie pojedyncze - czyszczenie poprzednich.');
    } else if (!isMultiSelect && isAlreadySelected) {
        // Jeśli brak CTRL i był zaznaczony -> zostawiamy tylko jego
        newSelected = [featureData];
    } else if (isMultiSelect && !isAlreadySelected) {
        // Jeśli CTRL i nie był zaznaczony -> dodajemy do grupy
        newSelected.push(featureData);
        console.log('Obiekt dodany do multi-selekcji.');
    }

    if (newSelected.length === 0) {
        // Jeśli odznaczyliśmy ostatni obiekt, usuwamy całą tabelę/warstwę
        this.objectSelection.clearAllSelectedVariables();
    } else {
        // Aktualizujemy zaznaczone obiekty i wywołujemy GeoServer
        this.objectSelection.selectedObjects.set(newSelected);
        this.objectSelection.selectedNumberOfObjects.set(newSelected.length);
        this.highlightSelectedObjectsTileLayer().then((layer) => {
            this.addOrReplaceHighlightedLayer(layer);
        });
    }

    // Wymuszamy natychmiastowe odświeżenie oryginalnej warstwy punktowej, by ukryć/pokazać punkty
    if (this.vectorLayer) {
        this.vectorLayer.changed();
    }
  }



  private http = inject(HttpClient);
  private async highlightSelectedObjectsTileLayer(): Promise<TileLayer> {
    const auth = getAuth();
    await auth.authStateReady();
    const userId = auth.currentUser?.uid ?? '';
    //Tutaj stworzyć nową warstwę i wbić ją do temp usera

    // Usuń poprzednią tabelę tylko jeśli już istnieje (time nie jest pustym stringiem)
    if (this.objectSelection.time !== '') {
      await firstValueFrom(
        this.http.delete('/analysys/delete-table-from-selection', {
          params: {
            userId: userId,
            time: this.objectSelection.time
          }
        })
      );
    }
    

    await this.objectSelection.sqlSelectObjects(this.objectSelection.selectedSelectOptionLayer(), this.objectSelection.getTime());

    return new TileLayer({
      properties: { layerKey: 'highlightedObjectsLayer' },
      source: new TileWMS({
        url: `${window.location.origin}/geoserver/user_${userId}_temp/wms?`,
        params: {
          'LAYERS': `user_${userId}_temp:user_${userId}_temp_table_${this.objectSelection.time}`, //tutaj specjalnie time zamiast getTime
          'TILED': true,
          'VERSION': '1.1.1',
          'BUFFER': 100,
          'SLD_BODY': this.objectSelection.getSLD(userId, this.objectSelection.time, this.objectSelection.selectedSelectOptionLayer()) //tutaj specjalnie time zamiast getTime
        },
        serverType: 'geoserver',
        hidpi: false,
        transition: 300,
        crossOrigin: 'anonymous',
      }),
      visible: true,
    })

  }

  

  private tileLayer(visibleLayer: LayerKey, layerName: string): TileLayer {
    const visibility = this.mapLayersVisibility.layersVisibility();
    return new TileLayer({
      properties: { layerKey: visibleLayer },
      source: new TileWMS({
        url: `${window.location.origin}/geoserver/AngularLocal/wms?`,
        // url: `${window.location.origin}/geoserver/AngularLocal/wms?`,
        params: {
          //'LAYERS': `AngularAppSpring:${layerName}`,
          'LAYERS': `AngularLocal:${layerName}`,
          'TILED': true,
          'VERSION': '1.1.1',
        },
        serverType: 'geoserver',
        hidpi: false,
        transition: 300,
        crossOrigin: 'anonymous',
      }),
      visible: visibility[visibleLayer],
    });
  }

  private buildVectorLayer(): VectorImageLayer {
    const wfsUrl =
      `${window.location.origin}/geoserver/AngularLocal/ows?` +
      `service=WFS&version=1.0.0&request=GetFeature` +
      `&typeName=AngularLocal:sql_data` +
      `&outputFormat=application/json&srsname=EPSG:3857`;

    

    this.vectorSource = new VectorSource({
      format: new GeoJSON(),
      url: wfsUrl,
    });

    this.vectorSource.once('featuresloadend', () => {
      const features = this.vectorSource.getFeatures();

      features.sort((a, b) => {
        const popA = Number(a.get('liczbamies')) || 0;
        const popB = Number(b.get('liczbamies')) || 0;
        return popB - popA; 
      });

      features.forEach((f, i) => f.set('__idx', i));
    });

    return new VectorImageLayer({
      properties: { layerKey: 'vectorLayer' },
      source: this.vectorSource,
      visible: this.mapLayersVisibility.isVisible('vectorLayer'),
      style: (feature, resolution) => this.decimatedStyle(feature, resolution),
      declutter: false,
    });
  }


  private readonly ALWAYS_SHOW_TOP_N = 60;

  private SelectedObjectsVectorLayer(): VectorImageLayer { 
    const wfsUrl = `${window.location.origin}/geoserver/AngularLocal/ows?` +
      `service=WFS&version=1.0.0&request=GetFeature` +
      `&typeName=AngularLocal:${this.objectSelection.selectedSelectOptionLayer()}` +
      `&outputFormat=application/json&srsname=EPSG:3857`;

    const vectorSource = new VectorSource({
      format: new GeoJSON(),
      url: wfsUrl,
    });

    return new VectorImageLayer({
      source: vectorSource,
      visible: true,
      style: (feature) => {
        return new Style({
          image: new CircleStyle({
            radius: 25,
            fill: new Fill({ color: 'orange' }),
            stroke: new Stroke({ color: '#000', width: 3 }),
          })
        })
      },
      declutter: false,
    });
  }

  private decimatedStyle(feature: FeatureLike, resolution: number): Style | undefined {
    // Sprawdź czy obiekt jest zaznaczony (aby ukryć go pod "żółtym" podświetleniem WMS)
    const featureIdStr = String(feature.getId());
    const featureIdNum = featureIdStr.includes('.') ? featureIdStr.split('.')[1] : featureIdStr;
    const isSelected = this.objectSelection.selectedSelectOptionLayer() === 'vectorLayer' && this.objectSelection.selectedObjects().some(obj => {
      const selectedIdNum = obj.features[0].id.split('.')[1];
      return selectedIdNum === featureIdNum;
    });
    
    if (isSelected) {
      return undefined; // Obiekt zaznaczony -> ukrywamy z oryginalnej warstwy!
    }

    const idx = feature.get('__idx') ?? 0;

    const skip = this.getSkipFactor(resolution);
    const isGuaranteed = idx < this.ALWAYS_SHOW_TOP_N;
    if (!isGuaranteed && (idx % skip !== 0)) {
      return undefined; 
    }

    const showLabel = resolution < this.AMService.mapResolution(); 
    const population = Number(feature.get('liczbamies')) || 0;
    const {radius, fontSize} = this.getSizeByPopulatiuon(population);

    return new Style({
      image: new CircleStyle({
        radius,
        fill: new Fill({ color: '#3399CC' }),
        stroke: new Stroke({ color: '#fff', width: 1.5 }),
      }),
      text: showLabel
        ? new Text({
          text: feature.get('nazwa'),
          offsetY: -(radius + 10),
          font: `${fontSize}px Roboto Flex`,
          fill: new Fill({ color: '#000' }),
          stroke: new Stroke({ color: '#fff', width: 3 }),
        })
        : undefined,
      zIndex: population,
    });
  }

  private getSizeByPopulatiuon(population: number): { radius: number; fontSize: number } {
    const minPop = 0;
    const maxPop = 2_000_000;
    const minRadius = 3;
    const maxRadius = 15;
    const minFont = 13;
    const maxFont = 26;

    const safePop = Math.max(0, Math.min(population, maxPop));

    const t = Math.pow(safePop / maxPop, 1 / 3);

    const radius = minRadius + t * (maxRadius - minRadius);
    const fontSize = minFont + t * (maxFont - minFont);

    return { radius, fontSize: Math.round(fontSize) };
  }

  private getSkipFactor(resolution: number): number {
    if (resolution > 3000) return 100;  
    if (resolution > 1500) return 50;
    if (resolution > 750) return 25;
    if (resolution > 350) return 10;
    if (resolution > 200) return 5;
    if (resolution > 100) return 2;
    return 1;
  }


}