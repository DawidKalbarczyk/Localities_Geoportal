import { Component, computed, effect, inject, signal} from '@angular/core';
import { GeoserverService } from '../../../../services/GeoserverService/geoserver-service';
import { ObjSelection } from '../../../../services/obj-selection/obj-selection';
import { TranslatePipe } from '../../../../pipes/translate.pipe';
import { ZoomToObject } from '../../../../services/zoom-to-object/zoom-to-object';
import { CommonModule } from '@angular/common';
import { PopUpService } from '../../../../services/pop-up-service/pop-up-service';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { AMService } from '../../../../services/a-m-service/a-m-service';
import { FormsModule, NgForm, NgModel } from '@angular/forms';
import { LoginService } from '../../../../services/login-service/login-service';
import TileLayer from 'ol/layer/Tile';
import VectorImageLayer from 'ol/layer/VectorImage';
import TileWMS from 'ol/source/TileWMS';
import VectorSource from 'ol/source/Vector';
import GeoJSON from 'ol/format/GeoJSON';
import Style from 'ol/style/Style';
import CircleStyle from 'ol/style/Circle';
import Fill from 'ol/style/Fill';
import Stroke from 'ol/style/Stroke';
import Text from 'ol/style/Text';
import { LayerVisibility } from '../../../../services/layer-visibility/layer-visibility';
import { AttributeTable } from './attribute-table/attribute-table';

@Component({
  selector: 'app-analysys-component',
  imports: [TranslatePipe, FormsModule, CommonModule, AttributeTable],
  templateUrl: './analysys-component.html',
  styleUrl: './analysys-component.scss',
})
export class AnalysysComponent {
  public inputText = signal<string>('');

  public zoomToObject = inject(ZoomToObject);
  public GeoserverService = inject(GeoserverService);
  public loginService = inject(LoginService);
  
  public userCreation(userId: string, func: 'createWorkspace' | 'createTempWorkspace' | 'createDatastore' | 'createTempDatastore' ) {
    this.GeoserverService[func](userId).subscribe({
      next: (response) => {
        console.log('Workspace created successfully:', response);
      },
      error: (error) => {
        console.error('Error creating workspace:', error);
      }
    })
  }

  public objectSelection = inject(ObjSelection);
  private http = inject(HttpClient);
  
  

  public popUpService = inject(PopUpService);
  public AMService = inject(AMService);
/* =============================================================================
                        1. LAYER INFO FOR USER ATTRIBUTE ANALYSIS
============================================================================= */
  public async getLayerInfo(layerName: string): Promise<void> {
    let realGeoserverLayerName = '';
    switch (layerName) {
      case 'vectorLayer':
        realGeoserverLayerName = 'sql_data';
        break;
      case 'boundsLayerCities':
        realGeoserverLayerName = 'boundscities';
        break;
      case 'boundsLayerGminy':
        realGeoserverLayerName = 'boundsgminy';
        break;
      case 'boundsLayerPowiaty':
        realGeoserverLayerName = 'boundspowiaty';
        break;
      case 'boundsLayerWojewodz':
        realGeoserverLayerName = 'boundswojewodz';
        break;
      case 'boundsLayerPanstwo':
        realGeoserverLayerName = 'boundspanstwo';
        break;
      default:
        console.warn('Unknown layer name:', layerName);
    }

    const workspace = "AngularLocal";
    const layer = realGeoserverLayerName;

    const url = `http://geoserver:8080/geoserver/rest/workspaces/${workspace}/featuretypes/${layer}.json`;
    const response = await firstValueFrom(this.http.get<any>('/save/get-xml-as-json?url=' + url));
    
    let data: any;
    const argumentName = layer;
    if (response?.featureType?.name === argumentName) {
        data = response;
    }
    console.log(data);
    const filteredData = data
      ? {
          ...data,
          featureType: {
            ...data.featureType,
            attributes: {
              ...data.featureType.attributes,
              attribute: data.featureType.attributes.attribute.filter(
                (attribute: { name?: string }) => attribute.name !== 'wkb_geometry'
              ),
            },
          },
        }
      : data;
    this.responseData.set(filteredData);
    };

    private numericAttributes = 
    ['jpt_powier', 'jpt_powi_1', 'wspgeog', 'wspxy',
      'shape_leng', 'shape_le_1', 'shape_area', 'liczbamies'];

    public disableOption = computed(() =>
      !this.numericAttributes.includes(this.attributeAttribute())
    );
   


    private map = this.AMService.map;
    private attributeTileLayer!: TileLayer;
    private attributeVectorLayer!: VectorImageLayer;
    private layerVisibility = inject(LayerVisibility);
    public submitType = signal<'new' | 'update'>('new');

    public responseData = signal<any>(null);
    public attributeLayer = signal<string>('');
    public attributeAttribute = signal<string>('');
    public attributeSign: string = "=";
    public attributeCondition: string = "";
    public attributeSQLResponse = signal<string>('');
    private oldTime: string = '';
    private oldUserId: string = '';
    private oldAttributeLayer: string = '';

/* =============================================================================
                          2. CLEAR ATTRIBUTE SELECTION
 ============================================================================= */
    
    public async clearAttributeSelection(): Promise<void> {
      if (this.attributeTileLayer) {
        this.map.removeLayer(this.attributeTileLayer);
      }
      if (this.attributeVectorLayer) {
        this.map.removeLayer(this.attributeVectorLayer);
      }
      this.attributeLayer.set('');
      this.objectSelection.onLayerSelectChange('');
      this.attributeSelectedLayer.set('');
      this.attributeAttribute.set('');
      this.attributeSign = '=';
      this.attributeCondition = '';
      this.AMService.showResolution('map');
      await this.deleteAttributeSelection();
    }

    private async deleteAttributeSelection(): Promise<void> {
      if (this.oldTime !== '' && this.oldUserId !== '') {
        await firstValueFrom(this.http.delete(`/attribute-analysis/delete-attribute-selection?oldUserId=${this.oldUserId}&oldTime=${this.oldTime}`, { responseType: 'text' }));
      }
    }
    public attributeSelectedLayer = signal<string>('');
    private addSelectedLayerToList(): void {
      let text = "";
      if (this.attributeTileLayer || this.attributeVectorLayer) {
        text = "Attribute Selection";
      } else {
        this.attributeSelectedLayer.set('');
        return;
      }
      this.attributeSelectedLayer.set(text);
    }
  

/* =============================================================================
                        3. NEW ATTRIBUTE SELECTION
============================================================================= */
    private async createNewAttributeSelection(): Promise<void> {
      if (this.attributeLayer()) {
        this.map.removeLayer(this.attributeTileLayer || this.attributeVectorLayer);
      }


      // Osobny czas, aby reset ręcznej selekcji nie usunął tabeli analizy atrybutowej.
      const newTime = Date.now().toString();
      const newUserId = this.objectSelection.getUserId();
      //this.map.removeLayer('attributeSelectionLayer'); - to nie dziala
      const formData = new FormData();
      formData.append('attributeLayer', this.attributeLayer());
      formData.append('attributeAttribute', this.attributeAttribute());
      formData.append('attributeSign', this.attributeSign);
      formData.append('attributeCondition', (() => {
        if (this.attributeAttribute() === 'shape_leng' || this.attributeAttribute() === 'shape_le_1' || this.attributeAttribute() === 'shape_area') {
          return String(Number(this.attributeCondition) * 1_000_000);
        } else {
          return this.attributeCondition;
        }
      })());

      formData.append('userId', newUserId);
      formData.append('time', newTime);

      
      try {
        const response = await firstValueFrom(this.http.post('/attribute-analysis/new-attribute-selection', formData, { responseType: 'text' }));
        console.log("Happily returning from backend: ", response);
      } catch (error) {
        console.error('Error submitting new attribute selection:', error);
      }

      if (this.attributeLayer() !== 'vectorLayer') {
        this.attributeTileLayer = new TileLayer({
          properties: { layerName: 'attributeSelectionLayer'},
          source: new TileWMS({
            url: `${window.location.origin}/geoserver/user_${newUserId}_temp/wms?`,
            params: {
              'LAYERS': `user_${newUserId}_temp_table_${newTime}`,
              'TILED': true,
              'SLD_BODY': this.objectSelection.getSLD(newUserId, newTime, this.attributeLayer())
            },
            serverType: 'geoserver',
            crossOrigin: 'anonymous'
          }),
          visible: true
        });
        this.map.addLayer(this.attributeTileLayer);

      /// Specjalnie robię jako VectorImageLayer aby w przyszłości móc rozszerzyć o edycję zapisanej już warstwy
      ///
      ///
      ///
      } else if (this.attributeLayer() === 'vectorLayer') {
        this.attributeVectorLayer = new VectorImageLayer({
          properties: { layerName: 'attributeSelectionLayer'},
          source: new VectorSource({
            format: new GeoJSON(),
            url: `${window.location.origin}/geoserver/user_${newUserId}_temp/ows?` +
              `service=WFS&version=1.0.0&request=GetFeature` +
              `&typeName=user_${newUserId}_temp:user_${newUserId}_temp_table_${newTime}` +
              `&outputFormat=application/json&srsname=EPSG:3857`
          }),
          visible: true,
          style: (feature, resolution) => {
            const showText = resolution < this.AMService.analysisResolution();

            return new Style({
              image: new CircleStyle({
                radius: 15,
                fill: new Fill({ color: '#36f1b9' }),
                stroke: new Stroke({ color: '#fff', width: 1.5 }),
              }),
              text: showText
                ? new Text({
                text: String(feature.get('nazwa') ?? ''),
                fill: new Fill({ color: '#ffffff' }),
                stroke: new Stroke({ color: '#000', width: 2 }),
                offsetY: -15
              }) : undefined,
              zIndex: 99999,
            });
          },
          declutter: false,
          
        });


        
        this.map.addLayer(this.attributeVectorLayer);
        this.AMService.showResolution('analysys');

      } else {
        console.log("Unknown layer type selected at analysys-component: ", this.attributeLayer());
      }

    
      this.layerVisibility.setLayerVisibility('vectorLayer', false);

      this.oldTime = newTime;
      this.oldUserId = newUserId;
      this.oldAttributeLayer = this.attributeLayer();
      this.addSelectedLayerToList();
      
      await this.checkForEmptyAttributeSelection();
    }



/* =============================================================================
                          4. UPDATE ATTRIBUTE SELECTION
 ============================================================================= */

    private async updateAttributeSelection(): Promise<void> {
      if (this.oldAttributeLayer && this.attributeSelectedLayer() === 'Attribute Selection') {
        this.map.removeLayer(this.attributeTileLayer || this.attributeVectorLayer);
      }

      // NIe ma newTime i newUser bo operacja na tej samej tabeli
      if (this.attributeLayer() !== this.oldAttributeLayer) {
        console.error('Cannot update attribute selection: attribute layer has changed.');
        return;
      }
      const formData = new FormData();
      formData.append('attributeLayer', this.attributeLayer());
      formData.append('attributeAttribute', this.attributeAttribute());
      formData.append('attributeSign', this.attributeSign);
      formData.append('attributeCondition', (() => {
        if (this.attributeAttribute() === 'shape_leng' || this.attributeAttribute() === 'shape_le_1' || this.attributeAttribute() === 'shape_area') {
          return String(Number(this.attributeCondition) * 1_000_000);
        } else {
          return this.attributeCondition;
        }
      })());
      formData.append('userId', this.oldUserId);
      formData.append('time', this.oldTime);
      try {
        const response = await firstValueFrom(this.http.post('/attribute-analysis/update-attribute-selection', formData, { responseType: 'text' }));
        console.log("Happily returning UPDATE from backend: ", response);
      } catch (error) {
        console.error('Error submitting update attribute selection:', error);
      }

      if (this.attributeLayer() !== 'vectorLayer') {
        this.attributeTileLayer = new TileLayer({
          properties: { layerName: 'attributeSelectionLayer'},
          source: new TileWMS({
            url: `${window.location.origin}/geoserver/user_${this.oldUserId}_temp/wms?`,
            params: {
              'LAYERS': `user_${this.oldUserId}_temp_table_${this.oldTime}`,
              'TILED': true,
              'SLD_BODY': this.objectSelection.getSLD(this.oldUserId, this.oldTime, this.attributeLayer()),

              // "Jeżeli nie wiesz jak coś działa to lepiej tego nie ruszać...."
              // Nie wiem dlaczego, ale powoduje to wywalenie cache'a z geoservera i wczytanie nowej warstwy
              '_v': Date.now()

              /////////////////////////////////////
            },
            serverType: 'geoserver',
            crossOrigin: 'anonymous'
          }),
          visible: true
        });
        this.map.removeLayer(this.attributeTileLayer);
        this.map.addLayer(this.attributeTileLayer);
      } else if (this.attributeLayer() === 'vectorLayer') {
        this.attributeVectorLayer = new VectorImageLayer({
          properties: { layerName: 'attributeSelectionLayer'},
          source: new VectorSource({
            format: new GeoJSON(),
            url: `${window.location.origin}/geoserver/user_${this.oldUserId}_temp/ows?` +
              `service=WFS&version=1.0.0&request=GetFeature` +
              `&typeName=user_${this.oldUserId}_temp:user_${this.oldUserId}_temp_table_${this.oldTime}` +
              `&outputFormat=application/json&srsname=EPSG:3857`
          }),
          visible: true,
          style: (feature, resolution) => {
            const showText = resolution < this.AMService.analysisResolution();

            return new Style({
              image: new CircleStyle({
                radius: 15,
                fill: new Fill({ color: '#36f1b9' }),
                stroke: new Stroke({ color: '#fff', width: 1.5 }),
              }),
              text: showText
                ? new Text({
                  text: String(feature.get('nazwa') ?? ''),
                  fill: new Fill({ color: '#ffffff' }),
                  stroke: new Stroke({ color: '#000', width: 2 }),
                  offsetY: -15
                }) : undefined,
              zIndex: 99999,
                });
          },
          declutter: false,
        });
        this.map.removeLayer(this.attributeVectorLayer);
        this.map.addLayer(this.attributeVectorLayer);
        this.AMService.showResolution('analysys');
        this.addSelectedLayerToList();
      } else {
        console.log("Unknown layer type selected at analysys-component: ", this.attributeLayer());
      }

      this.layerVisibility.setLayerVisibility('vectorLayer', false);
   
      await this.checkForEmptyAttributeSelection();
    }

    private async checkForEmptyAttributeSelection(): Promise<void> {
      await this.getUserLayer(this.oldUserId, this.oldTime);
      if (this.rowCount() === 0) {
        this.PopUpService.typeOfPopUp.set('empty-table');
      }
    }

    private resetAttributeLayerChoice(): void {
      this.attributeSelectedLayer.set('');
      this.objectSelection.onLayerSelectChange('');
      this.attributeLayer.set('');
      this.oldAttributeLayer = '';
      this.attributeAttribute.set('');
      this.attributeSign = '=';
      this.attributeCondition = '';
      this.responseData.set(null);
      this.isHelpButtonEnabled.set(false);
    }

    public attributeFormSubmit(type: 'new' | 'update'): void {
      if (type === 'new') {
        this.createNewAttributeSelection();
        console.log('Submitting new attribute form with values:');
      } else if (type === 'update') {
        this.updateAttributeSelection();
        console.log('Submitting update attribute form with values:');
      }
    }


    private PopUpService = inject(PopUpService);
    private pendingAttributeLayer = '';
    private pendingLayerModel?: NgModel;

    constructor() {
      effect(() => {
        const deleteItems = this.PopUpService.attributeSelectionDeleteHandler();
        if (deleteItems === null || !this.pendingAttributeLayer) {
          return;
        }

        if (deleteItems === true) {
          this.attributeLayer.set(this.pendingAttributeLayer);
          this.pendingLayerModel?.control.setValue(this.pendingAttributeLayer, { emitViewToModelChange: false });
          this.objectSelection.onLayerSelectChange(this.pendingAttributeLayer);
          this.getLayerInfo(this.objectSelection.selectedSelectOptionLayer());
          this.objectSelection.clearAllSelectedVariables('deleteFromAttributeSelection', this.oldUserId, this.oldTime);
          this.clearAttributeSelection();
        }

        this.pendingAttributeLayer = '';
        this.pendingLayerModel = undefined;
        this.PopUpService.typeOfPopUp.set('');
        this.PopUpService.attributeSelectionPopUpOn.set(false);
        this.PopUpService.attributeSelectionDeleteHandler.set(null);
      });
      effect(() => {
        if (this.PopUpService.newSubmitPopUpDeleteBool()) {
          this.submitType.set('new');
          this.attributeFormSubmit(this.submitType());
          this.PopUpService.newSubmitPopUpDeleteBool.set(null);
          this.PopUpService.newSubmitPopUpOn.set(false);
        } 
      })
      effect(() => {
        if (this.PopUpService.emptyTablePopUpClosed()) {
          this.resetAttributeLayerChoice();
          this.PopUpService.emptyTablePopUpClosed.set(false);
        }
      });
    }

    async ngOnDestroy() {
      await this.deleteAttributeSelection();
    }

    handleLayerChange(event: string, layerModel: NgModel): void {
      if (this.attributeSelectedLayer() === 'Attribute Selection') {
        layerModel.control.setValue(this.attributeSelectedLayer(), { emitViewToModelChange: false });
        this.pendingAttributeLayer = event;
        this.pendingLayerModel = layerModel;
        this.PopUpService.attributeSelectionDeleteHandler.set(null);
        this.PopUpService.attributeSelectionPopUpOn.set(true);
        this.PopUpService.typeOfPopUp.set('delete');
      } else {
        this.PopUpService.setAttributeLayerIntoPopUp(event);
        this.attributeLayer.set(event);
        this.objectSelection.onLayerSelectChange(event);
        this.getLayerInfo(this.objectSelection.selectedSelectOptionLayer());
        this.setHelpButtonEnabled();
      }
    }


    public isUpdateButtonEnabled = computed(() => {
      return this.attributeSelectedLayer() === 'Attribute Selection' &&
             this.attributeLayer() === this.oldAttributeLayer &&
             (this.attributeAttribute() !== '' || this.attributeCondition !== '');
    });




    /* =============================================================================
                          5. HELP DYNAMIC HANDLER
 ============================================================================= */
    public optionsValue = signal<string>("");
    public showHelp = signal<boolean>(false);
    public timeoutId = signal<any>(null);
    public handleMouseEnter(attributeName: string): void {
      this.optionsValue.set(attributeName);
      if (this.optionsValue()) {
        this.timeoutId.set(setTimeout(() => {
          this.showHelp.set(true);
        }, 500));
      }
      
    }
    public handleMouseLeave(): void {
      this.showHelp.set(false);
      this.optionsValue.set("");
      this.timeoutId() ? clearTimeout(this.timeoutId()) : null;
    }

    /* =============================================================================
                          6. HELP STATIC HANDLER
 ============================================================================= */
    public showStaticHelp(): void {
      this.popUpService.typeOfPopUp.set('info');
      this.popUpService.getDescriptionsJSON();
    }
    public isHelpButtonEnabled = signal<boolean>(false);
    private setHelpButtonEnabled(): void {
      if (this.attributeLayer()) {
        this.isHelpButtonEnabled.set(true);
      } else {
        this.isHelpButtonEnabled.set(false);
      }
    }

    /* =============================================================================
                          7. SUBMIT BUTT POPUP HANDLER
 ============================================================================= */
    public newSubmit(attributeForm: NgForm): void {
      if (!attributeForm.valid) {
        attributeForm.control.markAllAsTouched();
        return;
      }
      if (this.attributeSelectedLayer() !== 'Attribute Selection' && this.attributeLayer() !== this.oldAttributeLayer) {
        this.submitType.set('new');
        this.attributeFormSubmit(this.submitType());
        return;
      }
      this.PopUpService.typeOfPopUp.set('delete');
      this.PopUpService.newSubmitPopUpOn.set(true);
      
    }







    /* =============================================================================
                          7. GET USER ATTRIBUTE SELECTION TABLE
 ============================================================================= */
    public rowCount = signal<number | null>(null);
    public rows = signal<Record<string, unknown>[]>([]);
    public async getUserLayer(oldUserId: string, oldTime: string): Promise<void> {
      const response = await firstValueFrom(this.http.get(`/attribute-analysis/get-attribute-selection?tableName=user_${oldUserId}_temp_table_${oldTime}`, { responseType: 'text' }));
      if (response.startsWith("Error")) {
        console.error('Error getting attribute selection:', response);
        return;
      }
      
      const rows = JSON.parse(response) as Record<string, unknown>[];
      this.rows.set(rows);
      this.rowCount.set(rows.length);
      console.log("Returning from backend: ", rows);
      console.log("Row count: ", this.rowCount());
      
    }

    public rowsPickedLayer = signal<Record<string, unknown>[]>([]);
    public async getPickedLayer(): Promise<void> {
      const response = await firstValueFrom(this.http.get('/attribute-analysis/get-picked-layer?pickedTable=' + this.attributeLayer(), { responseType: 'text' }));
      if (response.startsWith("Error")) {
        console.error('Error getting picked layer:', response);
        return;
      }

      const rowsPickedLayer = JSON.parse(response) as Record<string, unknown>[];
      this.rowsPickedLayer.set(rowsPickedLayer);
    }
        /* ============================SHOWN ATTRIBUTE TABLE==================================== */

    public showAttributeTable = signal<boolean>(false);
    public shownTable = computed(async () => {
      if (this.attributeSelectedLayer() === 'Attribute Selection') {
        return (this.rows());
      } else if (this.attributeSelectedLayer() !== 'Attribute Selection' && this.attributeLayer()) {
        await this.getPickedLayer();
        return this.rowsPickedLayer()
      } else {
        return [];
      }
    })

    public isShownTableEmpty = computed(() => this.attributeLayer() === '');
    public toggleAttributeTable(): void {  /// For HTML button
      if (this.showAttributeTable() === true) {
        this.rows.set([]);
        this.rowsPickedLayer.set([]);
      }
      this.showAttributeTable.set(!this.showAttributeTable());
    }

  }
  
