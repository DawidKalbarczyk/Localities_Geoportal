import { Component, computed, effect, HostListener, input, signal, inject } from '@angular/core';
import proj4 from 'proj4';
import { register } from 'ol/proj/proj4';
import { fromLonLat, get, toLonLat, getPointResolution } from 'ol/proj';
import View from 'ol/View';
import { TranslatePipe } from '../../../../pipes/translate.pipe';
import { AMService } from '../../../../services/a-m-service/a-m-service';
import { AttributeTableToolbarService } from '../../../../services/attribute-table-toolbar-service/attribute-table-toolbar-service';

@Component({
  selector: 'app-map-info',
  host: {
    '[class.host-shifted]': 'doMapInfoHostShift() && !doMapInfoHostTransform()',
    '[class.host-transformed]': 'doMapInfoHostTransform() && doMapInfoHostShift()',
  },
  imports: [TranslatePipe],
  templateUrl: './map-info.html',
  styleUrl: './map-info.scss',
})
export class MapInfo {
  public mouseCoordinates = input<{ longitude: number; latitude: number } | null>();
  public mapView = input<View | null>();
  public scale = signal('—');
  private AMService = inject(AMService);
  public doMapInfoHostShift = signal<boolean>(false);
  private ToolbarService = inject(AttributeTableToolbarService);
  public doMapInfoHostTransform = signal<boolean>(false);

  constructor() {
    effect (() => {
      this.doMapInfoHostShift.set(
        this.AMService.showAttributeTable()
      );
    });
    effect (() => {
      this.doMapInfoHostTransform.set(
        this.ToolbarService.locateRowStyleOn()
      )
    });
    effect(onCleanup => {
      const view = this.mapView();
      if (!view) {
        this.scale.set('—');
        return;
      }

      const updateScale = () => {
        this.scale.set(this.calculateScale() ?? '—');
      };
      updateScale();
      view.on(['change:resolution', 'change:center'], updateScale);
      onCleanup(() => view.un(['change:resolution', 'change:center'], updateScale));
    });
  }

  public mouseCoordinates2180 = computed(() => {
    if (this.mouseCoordinates() === null) {
      return null;
    }
    const lon = this.mouseCoordinates()?.longitude;
    const lat = this.mouseCoordinates()?.latitude;

    proj4.defs(
      'EPSG:2180',
      '+proj=tmerc +lat_0=0 +lon_0=19 +k=0.9993 ' +
      '+x_0=500000 +y_0=-5300000 +ellps=GRS80 ' +
      '+towgs84=0,0,0,0,0,0,0 +units=m +no_defs'
    );

    register(proj4);

    const coords = fromLonLat([lon!, lat!], 'EPSG:2180');
    return { easting: coords[0].toFixed(3), northing: coords[1].toFixed(3)};
  })

  public mousePosition = signal<{ x: number; y: number }>({ x: 0, y: 0 });

  @HostListener('document:mousemove', ['$event'])
  getMousePosition(event: MouseEvent) {
    const x = event.clientX;
    const y = event.clientY;
    this.mousePosition.set({
      x: x,
      y: y
    });
  }

  private calculateScale(): string | undefined {
    const view = this.mapView();
    if (!view) return;
    const resolution = view.getResolution();
    const center = view.getCenter();
    if (resolution === undefined || !center) return;

    const metersPerPixel = getPointResolution(
      view.getProjection(),
      resolution,
      center,
      'm'
    );
    const scale = Math.round(metersPerPixel / 0.00028);
    return `1 : ${scale.toLocaleString('pl-PL')}`;
  }
}
