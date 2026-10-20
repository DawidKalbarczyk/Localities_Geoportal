import { inject, Service, signal } from '@angular/core';
import { ObjSelection } from '../obj-selection/obj-selection';

@Service()
export class PopUpService {
    private objectSelection = inject(ObjSelection);
    public typeOfPopUp = signal<'' | 'login' | 'save' | 'delete' | 'info' | 'empty-table'>('');

    public showPopUpSave = (): void  => {
        this.typeOfPopUp.set('save');
    }

    public showPopUpDelete = (): void  => {
        this.typeOfPopUp.set('delete');
    }

    public showPopUpInfo = (): void  => {
        this.typeOfPopUp.set('info');
    }

    public showPopUpLogin = (): void => {
        this.typeOfPopUp.set('login');
    }

    public resetPopUp = (agree: boolean): void => {
        this.typeOfPopUp.set('');
        agree ? this.objectSelection.clearAllSelectedVariables() : null;
    }

    public attributeSelectionPopUpOn = signal<boolean>(false);
    public attributeSelectionDeleteHandler = signal<true | false| null>(null);
    
    
    public attributeDescriptions = signal<Record<string, string>>({});
    public async getDescriptionsJSON(): Promise<void> {
        const response = await fetch('/i18n/pl.json');

        if (!response.ok) {
            throw new Error('Failed to fetch language JSON');
        }

        const data = await response.json();
        this.attributeDescriptions.set(data['GEOPORTAL']['ANALYSIS-CONTENT']['ATTRIBUTE-CONTENT']['ATTRIBUTE-DESCRIPTIONS']);
    }


    public attributeLayer = signal<string>('');
    public setAttributeLayerIntoPopUp(attributeL: string): void {
        this.attributeLayer.set(attributeL);
    }

    public newSubmitPopUpOn = signal<boolean>(false);
    public newSubmitPopUpDeleteBool = signal<true | false | null>(null);
    public newSubmitPopUpHandler(bool: boolean): void {
        this.newSubmitPopUpDeleteBool.set(bool);
    }
}
