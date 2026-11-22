import { inject, Service, signal } from '@angular/core';
import { ObjSelection } from '../obj-selection/obj-selection';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { PopUpService } from '../pop-up-service/pop-up-service';

import { Map } from 'ol';


export interface HeadbarKeys {
  analysys: boolean;
  measure: boolean;
  save: boolean;
}

@Service()
export class AMService {
    private objectSelection = inject(ObjSelection);
    public headbarKeys: HeadbarKeys = {
        analysys: false,
        measure: false,
        save: false
    }


    public map!: Map;
    public getMap(map: Map): void {
      this.map = map;
    }
  
    public resetAMServiceVariables(): void{
        for (const key in this.headbarKeys) {
            this.headbarKeys[key as keyof HeadbarKeys] = false;
        }
    }

    checkButt(arg: keyof HeadbarKeys): void {
        for (const key in this.headbarKeys) {
        const typedKey = key as keyof HeadbarKeys;
        if (key !== arg) {
            this.headbarKeys[typedKey] = false;
        } else {
            this.headbarKeys[typedKey] = !this.headbarKeys[typedKey];
        }
        }
    }

    analysysOut(): void {
        this.checkButt('analysys');
    }

    measureOut(): void {
        this.checkButt('measure');
    }

    private http = inject(HttpClient);
    private popUpService = inject(PopUpService)

    public async getLayerBBox() {
        const jsonResponse = await this.getJson();
        let bboxArray: any[] = [];
        await Promise.all(jsonResponse.json.map(async (item: any) => {
            const workspace = `user_${item.userId}`;
            const layer = `user_${item.userId}_perm_table_${item.time}`;

            const url = `http://geoserver:8080/geoserver/rest/workspaces/${workspace}/featuretypes/${layer}.json`;
            const response = await firstValueFrom(this.http.get<any>('/save/get-xml-as-json?url=' + url));
            const bbox = response.featureType.latLonBoundingBox;
            bboxArray.push({
                userId: item.userId,
                time: item.time,
                bbox: bbox,
                title: item.title,
                type: item.type,
                layer: item.layer ?? item.layerFrom ?? 'Layer ERROR'
            });

        }));
        return bboxArray;
    }

    // Ta funkcja nie zwraca danych tylko metadane warstwy z Geoservera. 5
    // Zrobić Rest API do zapytania do bazy
    public async getLayerData(routerUserId: string, routerTime: string): Promise<any> {
        const jsonResponse = await this.getJson();
        let dataArray: any = [];
        await Promise.all(jsonResponse.json.map(async (item: any) => {
            const workspace = `user_${item.userId}`;
            const layer = `user_${item.userId}_perm_table_${item.time}`;

            const url = `http://geoserver:8080/geoserver/rest/workspaces/${workspace}/featuretypes/${layer}.json`;
            const response = await firstValueFrom(this.http.get<any>('/save/get-xml-as-json?url=' + url));
            
            const argumentName = `user_${routerUserId}_perm_table_${routerTime}`;
            if (response?.featureType?.name === argumentName) {
                dataArray = response;
            }
        }));
        return dataArray;
    }




    

    public async saveSelectedObjects(
        title: string,
        type: string = "selectedObjByHand",
        oldUserId: string = this.objectSelection.userId,
        oldTime: string = this.objectSelection.time,
        userId: string = this.objectSelection.getUserId(),
        time: string = this.objectSelection.getTime(),
        layer: string = this.objectSelection.selectedSelectOptionLayer(),
        ids: string = (() => {
            const selectedObjects = this.objectSelection.selectedObjects();
            if (!selectedObjects || selectedObjects.length === 0) {
            return '';
            }
            const idArray: string[] = [];
            selectedObjects.forEach((obj) => {
            idArray.push(obj.features[0].id.split('.')[1]);
            });
            return idArray.join(',');
        })()
        ): Promise<void> {
        try {
            const formData = new FormData();
            formData.append('title', title);
            formData.append('type', type);
            formData.append('oldUserId', oldUserId);
            formData.append('oldTime', oldTime);
            formData.append('userId', userId);
            formData.append('time', time);
            formData.append('layer', layer);
            formData.append('ids', ids);

            const response = await firstValueFrom(this.http.post('/save/selected-objects', formData, {responseType: 'text'}));
            if (response) {
                this.popUpService.resetPopUp(true);
                this.savePopUpOn();
                console.log('Response from saveSelectedObjects:', response);
            } else {
                console.error('No response from saveSelectedObjects');
            }

            await firstValueFrom(this.http.post(`/save/publish-layer?userId=${userId}&time=${time}&layer=${layer}`, {}));
            
        } catch (error) {
            console.error('Error creating FormData:', error);
        }
        }
    public async getJson(userId: string = this.objectSelection.getUserId()): Promise<any> {
        try {
            const response = await firstValueFrom(this.http.get(`/save/get-json?userId=${userId}`));
            return response;
        } catch (error) {
            console.error('Error fetching JSON:', error);
            throw error;
        }   
    }

    public wasSaved = signal<boolean>(false);
    public savePopUpOn(): void {
        this.wasSaved.set(true);
    }
    public savePopUpOff(): void {
        this.wasSaved.set(false);
    }

    public mapResolution = signal<number>(500);
    public analysisResolution = signal<number>(300);
    public showResolution(component: string): void {
        switch (component) {
            case 'map':
                this.mapResolution.set(500);
                break;
            case 'analysys':
                this.analysisResolution.set(300);
                this.mapResolution.set(-1); // nigdy się nie spełni 
                break;
            default:
                console.error('Unknown component for resolution display');
        }
    }

    public showAttributeTable = signal<boolean>(false);
}
