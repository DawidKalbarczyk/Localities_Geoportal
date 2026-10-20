import { Service, signal, inject, effect } from '@angular/core';
import BaseLayer from 'ol/layer/Base';
import { Collection } from 'ol';
import { getAuth} from 'firebase/auth';
import { LayerVisibility } from '../layer-visibility/layer-visibility';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs/internal/firstValueFrom';
import TileLayer from 'ol/layer/Tile';
import TileWMS from 'ol/source/TileWMS';

@Service()
export class ObjSelection {
    public SLD: string = ``;
    public getSLD(userId: string, time: string, layer: string): string {
        let sld: string = ``;
        if (layer === 'vectorLayer') {
            sld = `<StyledLayerDescriptor version="1.0.0"
            xsi:schemaLocation="http://www.opengis.net/sld http://schemas.opengis.net/sld/1.0.0/StyledLayerDescriptor.xsd"
            xmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc"
            xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">

            <NamedLayer>
                <Name>user_${userId}_temp_table_${time}</Name>
                <UserStyle>
                <Title>Selection style for all users</Title>
                <FeatureTypeStyle>
                    <Rule>
                    <Title>Selection polygon</Title>
                    <PointSymbolizer>
                        <Graphic>
                            <Mark>
                                <WellKnownName>circle</WellKnownName>
                                <Fill>
                                    <CssParameter name="fill">#ebd834</CssParameter>
                                </Fill>
                                <Stroke>
                                    <CssParameter name="stroke">#000000</CssParameter>
                                    <CssParameter name="stroke-width">2</CssParameter>
                                </Stroke>
                            </Mark>
                            <Size>30</Size>
                        </Graphic>
                    </PointSymbolizer>
                    <TextSymbolizer>
                        <Label>
                            <ogc:PropertyName>nazwa</ogc:PropertyName>
                        </Label>
                        <Font>
                            <CssParameter name="font-family">Arial</CssParameter>
                            <CssParameter name="font-size">35</CssParameter>
                            <CssParameter name="font-weight">bold</CssParameter>
                        </Font>
                        <LabelPlacement>
                            <PointPlacement>
                                <AnchorPoint>
                                    <AnchorPointX>0.5</AnchorPointX>
                                    <AnchorPointY>0.0</AnchorPointY>
                                </AnchorPoint>
                                <Displacement>
                                    <DisplacementX>0</DisplacementX>
                                    <DisplacementY>35</DisplacementY>
                                </Displacement>
                            </PointPlacement>
                        </LabelPlacement>
                        <Fill>
                            <CssParameter name="fill">#000000</CssParameter>
                        </Fill>
                        <Halo>
                            <Radius>2</Radius>
                            <Fill>
                                <CssParameter name="fill">#ebd834</CssParameter>
                            </Fill>
                        </Halo>
                        <VendorOption name="conflictResolution">false</VendorOption>
                        <VendorOption name="partials">true</VendorOption>
                    </TextSymbolizer>

                    </Rule>

                </FeatureTypeStyle>
                </UserStyle>
            </NamedLayer>
            </StyledLayerDescriptor>`;
        } else {
            sld = `<StyledLayerDescriptor version="1.0.0"
            xsi:schemaLocation="http://www.opengis.net/sld http://schemas.opengis.net/sld/1.0.0/StyledLayerDescriptor.xsd"
            xmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc"
            xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">

            <NamedLayer>
                <Name>user_${userId}_temp_table_${time}</Name>
                <UserStyle>
                <Title>Selection style for all users</Title>
                <FeatureTypeStyle>
                    <Rule>
                    <Title>Selection polygon</Title>
                    <PolygonSymbolizer>
                        <Fill>
                        <CssParameter name="fill">#ebd834</CssParameter>
                        </Fill>
                        <Stroke>
                        <CssParameter name="stroke">#000000</CssParameter>
                        <CssParameter name="stroke-width">0.5</CssParameter>
                        </Stroke>
                    </PolygonSymbolizer>
                    </Rule>
                </FeatureTypeStyle>
                </UserStyle>
            </NamedLayer>
            </StyledLayerDescriptor>`;
        }
        
        return sld.replace(/>\s+</g, '><').trim();
    }

    private http = inject(HttpClient);
    public analysysPicked = signal<boolean>(false);
    public analysisNrPicked = signal<string>('none');
    public toolPicked = signal<string>('Błąd');
    public mapLayers = signal<Collection<BaseLayer>>(new Collection<BaseLayer>());   
    public visibleMapLayers = signal<any[]>([]);
     public async clearAllSelectedVariables(...args: any[]): Promise<void> {
        this.selectedObjects.set([]);
        this.selectedNumberOfObjects.set(0);

        // Usuń żółtą warstwę z mapy, jeśli istnieje
        const layers = this.mapLayers();
        if (layers) {
            const existingLayer = layers.getArray().find((l) => l.get('layerKey') === 'highlightedObjectsLayer');
            if (existingLayer) {
                layers.remove(existingLayer);
            }
        }

        if (args.length > 0) {
            const check = args[0];
            const oldUserId = args[1];
            const oldTime = args[2];
            if (check === 'deleteFromAttributeSelection') {
                await firstValueFrom(this.http.delete('/attribute-analysis/delete-attribute-selection?oldUserId=' + 
                    oldUserId + '&oldTime=' + oldTime, { responseType: 'text' }));
            }
        }

        if (this.time !== '') {
            await this.http.delete('/analysys/delete-table-from-selection', {
                params: {
                    userId: this.userId,
                    time: this.time
                }
            }).toPromise().then(() => {
                console.log('Temporary table ALL VARIABLES CLEAR deleted successfully.');
                this.time = '';
            }).catch((error) => {
                console.error('Error deleting ALL VARIABLES CLEAR temporary table:', error);
            });
        }
    }

    private layerVisibility = inject(LayerVisibility);
    
    // Słownik mapujący klucze warstw na końcówki kluczy tłumaczeń (np. LAY1, LAY2)
    public layerTranslations: Record<string, string> = {
        'vectorLayer': 'LAY1',
        'boundsLayerCities': 'LAY2',
        'boundsLayerGminy': 'LAY3',
        'boundsLayerPowiaty': 'LAY4',
        'boundsLayerWojewodz': 'LAY5',
        'boundsLayerPanstwo': 'LAY6',
        'excludedObjectsLayer': 'LAY1' // Ta warstwa zastępuje vectorLayer, więc tłumaczymy ją tak samo
    };

    public getMapLayers(layers: Collection<BaseLayer>): void {
        this.mapLayers.set(layers);
        let isSelectedLayerStillVisible = false;
        
        // ZAWSZE czyścimy listę przed nowym przeliczeniem!
        this.visibleMapLayers.set([]);

        this.mapLayers().forEach((layer) => {
            const layerKey = layer.get('layerKey');
            // Zabezpieczenie: bierzemy pod uwagę tylko warstwy, które mają ustawiony 'layerKey'
            if (layerKey && this.layerVisibility.isVisible(layerKey)) {
                this.visibleMapLayers.update((v) => [...v, layer]);
                if (layerKey === this.selectedSelectOptionLayer()) {
                    isSelectedLayerStillVisible = true;
                }
            }
        });

        // Zresetuj wybór, jeśli zaznaczona warstwa nagle zniknęła z widocznych
        if (this.selectedSelectOptionLayer() !== '' && !isSelectedLayerStillVisible) {
            this.selectedSelectOptionLayer.set('');
            this.clearAllSelectedVariables();
        }
    }
    public resetMapLayers(): void {
        this.visibleMapLayers.set([]);
    }
    public isSelectionPicked = signal<boolean>(false);
    public resetSelectedOption(): void {
        this.isSelectionPicked.set(false);
    }

    public userId: string = '';
    public getUserId(): string {
        const auth = getAuth();
        if (auth.currentUser) {
            this.userId = auth.currentUser.uid;
        }
        return this.userId;
    }
    public time: string = '';
    public getTime(): string {
        this.time = Date.now().toString();
        return this.time;
    }

    public async sqlSelectObjects(layer: string, time: string): Promise<void> {
        try {
            const auth = getAuth();
            
            // Czekamy ułamek sekundy, aż Firebase zainicjalizuje sesję (inaczej currentUser to null po odświeżeniu)
            await auth.authStateReady(); 

            let userId: string = '';
            if (auth.currentUser) {
                userId = this.getUserId();
            }

            const ids: string[] = [];
            this.selectedObjects().forEach((object) => {
                ids.push(object.features[0].id.split('.')[1]);
            });
            const idsString = ids.join(',');
            console.log('Creating table with query: ', `SELECT * FROM ${layer} WHERE id IN (${idsString})`);
            const formData = new FormData();
            formData.append('userId', userId);
            formData.append('layer', layer);
            formData.append('ids', `(${idsString})`);
            formData.append('time', time);

            await firstValueFrom(
                this.http.post('/analysys/create-table-from-selection', formData, { responseType: 'text' })
            );

            const tableName = `user_${userId}_temp_table_${time}`;
            await this.http.post('/analysys/create-layer', {
                tableName: tableName,
                title: tableName,
                sld: this.getSLD(userId, time, layer),
                userId: userId
            }).toPromise();
            
        } catch (error) {
            console.error('Error fetching user ID token:', error);
            throw error;
        }
    }

    public selectedSelectOptionLayer = signal<string>('');
    public selectedObjects = signal<any[]>([]);
    public selectedNumberOfObjects = signal<number>(0);

    public onLayerSelectChange(newLayer: string): void {
        if (this.selectedSelectOptionLayer() !== newLayer) {
            this.selectedSelectOptionLayer.set(newLayer);
            this.selectedObjects.set([]);
            this.selectedNumberOfObjects.set(0);
        }
    }

    public analysisActive(): void {
        this.analysysPicked.set(true);
    }
    public analysisDeactive(): void {
        this.analysysPicked.set(false);
        this.analysisNrPicked.set('none');
        this.toolPicked.set('Błąd');
    }

    
    public pickAnalysys(param: string) {
        this.analysysPicked.set(!this.analysysPicked());
        switch (param) {
            case 'attribute':
                console.log('Attribute analysis selected');
                this.analysisNrPicked.set('attribute');
                this.toolPicked.set(this.changeTitle('attribute'));
                break;
            case 'spatial':
                console.log('Spatial analysis selected');
                this.analysisNrPicked.set('spatial');
                this.toolPicked.set(this.changeTitle('spatial'));
                break;
            case 'selection':
                console.log('Object selection selected');
                this.analysisNrPicked.set('selection');
                this.toolPicked.set(this.changeTitle('selection'));
                break;
            default:
                this.analysisNrPicked.set('none');
                this.toolPicked.set(this.changeTitle('error'));
        }
    }   
    public changeTitle(tool: string) {
        switch (tool) {
            case 'attribute':
                return 'GEOPORTAL.ANALYSIS-CONTENT.ATTRIBUTE-CONTENT.TITLE';
            case 'spatial':
                return 'GEOPORTAL.ANALYSIS-CONTENT.SPATIAL-CONTENT.TITLE';
            case 'selection':
                return 'GEOPORTAL.ANALYSIS-CONTENT.SELECTION-CONTENT.TITLE';
            default:
                return 'Błąd';
        }
    }

    public futon = signal<boolean>(false);
    public testFuton(): void {

        
    }

    public async deleteObjFromSelection(objectId: string): Promise<TileLayer> {
        for (let i = 0; i < this.selectedObjects().length; i++) {
            const obj = this.selectedObjects()[i];
            if (obj.features[0].id === objectId) {
                this.selectedNumberOfObjects.update(n => n - 1);
                this.selectedObjects.update(objects => {
                    return objects.filter(ob => ob.features[0].id !== objectId);
                })

                await firstValueFrom(
                    this.http.delete('/analysys/delete-table-from-selection', {
                    params: {
                        userId: this.userId,
                        time: this.time,
                    }
                    })
                ).catch((error) => {
                    console.error('Error deleting object from selection:', error);
                });
                

                const idsString = this.selectedObjects().map(obj => obj.features[0].id.split('.')[1]).join(',');
                const newUserId = this.getUserId();
                const newTime = this.getTime();
                const formData = new FormData();
                formData.append('userId', newUserId);
                formData.append('layer', this.selectedSelectOptionLayer());
                formData.append('ids', `(${idsString})`);
                formData.append('time', newTime);
                await firstValueFrom(
                    this.http.post('/analysys/create-table-from-selection', formData, {responseType: 'text'})
                );

                const tableName = `user_${newUserId}_temp_table_${newTime}`;
                await this.http.post('/analysys/create-layer', {
                    tableName: tableName,
                    title: tableName,
                    sld: this.getSLD(newUserId, newTime, this.selectedSelectOptionLayer()),
                    userId: newUserId,
                }).toPromise();
                //Obsluga http rquest do backendu w celu usuniecia obiektu z bazy danych
                return new TileLayer({
                    properties: { layerKey: 'highlightedObjectsLayer' },
                    source: new TileWMS({
                        url: `${window.location.origin}/geoserver/user_${newUserId}_temp/wms?`,
                        params: {
                        'LAYERS': `user_${newUserId}_temp:user_${newUserId}_temp_table_${newTime}`, //tutaj specjalnie time zamiast getTime
                        'TILED': true,
                        'VERSION': '1.1.1',
                        'BUFFER': 100,
                        'SLD_BODY': this.getSLD(newUserId, newTime, this.selectedSelectOptionLayer()) //tutaj specjalnie time zamiast getTime
                        },
                        serverType: 'geoserver',
                        transition: 300,
                        crossOrigin: 'anonymous',
                    }),
                    visible: true,
                })
            } else {
                continue;
            }
        }
        throw new Error(`Object with ID ${objectId} not found in selectedObjects.`); 
    }
    public passedId = signal<string>('');
}
