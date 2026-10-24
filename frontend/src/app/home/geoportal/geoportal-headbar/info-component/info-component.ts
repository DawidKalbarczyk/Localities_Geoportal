import { Component, signal, inject, HostListener, effect, computed, Host } from '@angular/core';
import { InfoToggle } from '../../../../services/info-toggle/info-toggle';
import { InfoFeatures } from '../../../../services/info-features/info-features';
import {MatProgressSpinnerModule} from '@angular/material/progress-spinner';
import { LayerVisibility } from '../../../../services/layer-visibility/layer-visibility';
import { TranslatePipe } from '../../../../pipes/translate.pipe';

type LayerKey = 
    | 'vectorLayer'
    | 'boundscities'
    | 'boundsgminy'
    | 'boundspowiaty'
    | 'boundswojewodz'
    | 'boundspanstwo'
    | 'budLayer';



@Component({
  selector: 'app-info-component',
  imports: [MatProgressSpinnerModule, TranslatePipe],
  templateUrl: './info-component.html',
  styleUrl: './info-component.scss',
})

export class InfoComponent {
  infoToggleService = inject(InfoToggle);
  showMarker = signal<boolean>(false);
  turnMarkerUpsideDown = signal<boolean>(false);
  turnMarkerHorizontal = signal<boolean>(false);
  turnMarkerHorVer = signal<boolean>(false);
  markerX = signal<number>(0);
  markerY = signal<number>(0);
  isClickInsideTarget = signal<boolean>(false);

  public infoFeatures = inject(InfoFeatures);
  public layerWithId = this.infoFeatures.layerWithId;
  public properties = this.infoFeatures.properties;

  constructor() {
    effect(() => {
      if (this.infoFeatures.isCursorDragged()) {
        this.showMarker.set(false);
      }
    });
  }

  public markerReady = signal<boolean>(false);

  private layerPriority: Record<LayerKey, number> = {
    boundspanstwo: 6,
    boundswojewodz: 5,
    boundspowiaty: 4,
    boundsgminy: 3,
    boundscities: 2,
    vectorLayer: 0,
    budLayer: 1,
  };
  
  private vectorResults = inject(LayerVisibility).vectorResults;
  public sortedLayerData = computed(() => {
    const layers = this.layerWithId();
    const wmsProps = this.properties();
    const vectorProps = this.vectorResults();
    const combinedProps = [
      ...vectorProps.map((feat) => ({layer: 'vectorLayer', properties: feat})),
      ...layers.map((layer, index) => ({layer, properties: wmsProps[index] || []})),
    ];
  
    return combinedProps.sort((a, b) => {
      const keyA = a.layer.split('.')[0] as LayerKey;
      const keyB = b.layer.split('.')[0] as LayerKey;

      const priorityA = this.layerPriority[keyA] ?? 999;
      const priorityB = this.layerPriority[keyB] ?? 999;

      return priorityA - priorityB;

    });
  });

  private layerType = signal<Record<LayerKey, string>>({
    vectorLayer: 'Miejscowości',
    boundscities: 'Miasta',
    boundsgminy: 'Gminy',
    boundspowiaty: 'Powiaty',
    boundswojewodz: 'Województwa',
    boundspanstwo: 'Państwo',
    budLayer: 'Budynki',
  });
  private objectType = signal<Record<LayerKey, string>>({
    vectorLayer: 'Miejscowość',
    boundscities: 'Miasto',
    boundsgminy: 'Gmina',
    boundspowiaty: 'Powiat',
    boundswojewodz: 'Województwo',
    boundspanstwo: 'Państwo',
    budLayer: 'Budynek',
  });

  getLayerLabel(layer: string): string {
    const layerName = layer.split('.')[0] as LayerKey;
    if (layerName in this.layerType()) {
      return this.layerType()[layerName];
    } else {
      return '';
    }
  }
  getObjectLabel(layer: string): string {
    const layerName = layer.split('.')[0] as LayerKey;
    if (layerName in this.objectType()) {
      switch (this.objectType()[layerName]) {
        case 'Miejscowość':
          return 'GEOPORTAL.INFO-DETAILS.LOCALITY';
        case 'Miasto':
          return 'GEOPORTAL.INFO-DETAILS.CITY';
        case 'Gmina':
          return 'GEOPORTAL.INFO-DETAILS.COMMUNE';
        case 'Powiat':
          return 'GEOPORTAL.INFO-DETAILS.DISTRICT';
        case 'Województwo':
          return 'GEOPORTAL.INFO-DETAILS.VOIVODESHIP';
        case 'Państwo':
          return 'GEOPORTAL.INFO-DETAILS.COUNTRY';
        case 'Budynek':
          return 'GEOPORTAL.INFO-DETAILS.BUILDING';
        default:
          return '';
      }
    } else {
      return '';
    }
  }

  private mouseDownX = 0;
  private mouseDownY = 0;
  private dragThreshold = 20;
  private isMouseDown = false;
  private hasDraggedThisPress = false;
  private mouseDownInsidePanel = false;
  @HostListener('document:mousedown', ['$event'])
  onMouseDown(event: MouseEvent): void {
    const target = event.target as HTMLElement;
    this.mouseDownInsidePanel = !!target.closest('.marker, app-attribute-table');

    this.mouseDownX = event.clientX;
    this.mouseDownY = event.clientY;
    this.isMouseDown = true;
    this.hasDraggedThisPress = false;
    this.infoFeatures.resetDragged();
  }
  
  @HostListener('document:mousemove', ['$event'])
  onMouseMove(event: MouseEvent): void {
    if (!this.isMouseDown || this.hasDraggedThisPress || this.mouseDownInsidePanel) {
      return;
    }

    const deltaX = Math.abs(event.clientX - this.mouseDownX);
    const deltaY = Math.abs(event.clientY - this.mouseDownY);

    if (deltaX > this.dragThreshold || deltaY > this.dragThreshold) {
      this.infoFeatures.isDragged();
      this.hasDraggedThisPress = true;
    }
  }

  @HostListener('document:mouseup', ['$event'])
  onMouseUp(event: MouseEvent): void {
    this.isMouseDown = false;
  }

  @HostListener('document:click', ['$event'])
  setMarkerPosition(event: MouseEvent): void {
    const target = event.target as HTMLElement;
    if (target.closest('.marker, app-attribute-table')) {
      this.mouseDownInsidePanel = false;
      return;
    }

    const deltaX = Math.abs(event.clientX - this.mouseDownX);
    const deltaY = Math.abs(event.clientY - this.mouseDownY);

    if (this.mouseDownInsidePanel) {
      this.mouseDownInsidePanel = false;
      return;
    }

    if (deltaX > this.dragThreshold || deltaY > this.dragThreshold) {
      this.showMarker.set(false);
      return;
    }

    if (!this.infoToggleService.isInfoClicked()) {
      this.showMarker.set(false);
      return;
    }

    const mapEl = document.getElementById('map');
    if (!mapEl) return;

    const rect = mapEl.getBoundingClientRect();

    const insideTarget =
      event.clientX >= rect.left &&
      event.clientX <= rect.right &&
      event.clientY >= rect.top &&
      event.clientY <= rect.bottom;

    this.isClickInsideTarget.set(insideTarget);

    if (insideTarget) {
      this.markerX.set(event.clientX);
      this.markerY.set(event.clientY);
      this.showMarker.set(true);
    } else {
      this.showMarker.set(false);
    }

    const isRightHalf = event.clientX > window.innerWidth / 2;
    const isBottomHalf = event.clientY > window.innerHeight / 2;

    this.turnMarkerHorVer.set(isRightHalf && isBottomHalf);
    this.turnMarkerUpsideDown.set(!isRightHalf && isBottomHalf);
    this.turnMarkerHorizontal.set(isRightHalf && !isBottomHalf);


  
  }
}
