import { Component, effect, inject, signal } from '@angular/core';
import { PopUpService } from '../../../services/pop-up-service/pop-up-service';
import { ObjSelection } from '../../../services/obj-selection/obj-selection';
import { FormsModule } from '@angular/forms';
import { AMService } from '../../../services/a-m-service/a-m-service';
import { RouterLink } from '@angular/router';
import { KeyValuePipe } from '@angular/common';
import { TranslatePipe } from '../../../pipes/translate.pipe';
import { firstValueFrom } from 'rxjs/internal/firstValueFrom';
import { HttpClient } from '@angular/common/http';


@Component({
  selector: 'app-pop-up',
  imports: [FormsModule, RouterLink, KeyValuePipe, TranslatePipe],
  templateUrl: './pop-up.html',
  styleUrl: './pop-up.scss',
})
export class PopUp {
  public popUpService = inject(PopUpService);
  public objectSelection = inject(ObjSelection);
  userLayerName = '';
  public resetPopUp = (val: boolean) => this.popUpService.resetPopUp(val);
  public attributeSelectionHandler = (val: true | false | null) => this.popUpService.attributeSelectionDeleteHandler.set(val);

  public typeOfPopUp = this.popUpService.typeOfPopUp;  // signal, nie wywołanie

  public AMService = inject(AMService);


  private http = inject(HttpClient);
  public responseData = signal<any>(null);
  public async getLayerColumns(): Promise<void> {
    let realGeoserverLayerName = '';
    switch (this.popUpService.attributeLayer()) {
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
        console.warn('Unknown layer name:', this.popUpService.attributeLayer());
    }
    const layer = realGeoserverLayerName;

    const url = `http://geoserver:8080/geoserver/rest/workspaces/AngularLocal/featuretypes/${layer}.json`;
    const response = await firstValueFrom(this.http.get<any>('/save/get-xml-as-json?url=' + url));
    
    console.log('CHECKING LAYER IN POPUP:', response);
    let data: any;
    const argumentName = layer;
    if (response?.featureType?.name === argumentName) {
        data = response;
    }
    this.responseData.set(data);
    console.log("RESPONSE DATA IN POPUP:", this.responseData());
  }

  constructor() {
    effect(() => {
      if (this.popUpService.typeOfPopUp() === 'info') {
        this.getLayerColumns();
      }
    })
  }
}
