import { Component, input, inject, OnDestroy, signal } from '@angular/core';
import { MatTooltipModule } from '@angular/material/tooltip';
import { AttributeTableToolbarService } from '../../services/attribute-table-toolbar-service/attribute-table-toolbar-service';
import { TranslatePipe } from '../../pipes/translate.pipe';
import Feature from 'ol/Feature';
import GeoJSON from 'ol/format/GeoJSON';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';

@Component({
  selector: 'app-attribute-table-toolbar',
  imports: [MatTooltipModule, TranslatePipe],
  templateUrl: './attribute-table-toolbar.html',
  styleUrl: './attribute-table-toolbar.scss',
})
export class AttributeTableToolbar implements OnDestroy {
  shownTable = input<Promise<Record<string, unknown>[]>>(Promise.resolve([]));
  attributeSuggestionsTableSearch = input<string[]>([]);
  public ToolbarService = inject(AttributeTableToolbarService);

  private ToolbarTools = this.ToolbarService.ToolbarTools;
  public ToolbarMatTooltip = this.ToolbarService.ToolbarMatTooltip;
  public toggleTool(tool: string): void {
    this.ToolbarService.toggleActivationTool(tool);
    if (!this.isSelectionToolActive()) this.highlightLayer.getSource()?.clear();
  }

  // SELECTION TOOL
  public isSelectionToolActive = this.ToolbarTools['selectionTool'];
  public map = this.ToolbarService.mainMap;
  private readonly highlightLayer = new VectorLayer({
    source: new VectorSource(),
    zIndex: 9999,
    style: {
      'fill-color': 'rgba(255, 195, 51, 0.35)',
      'stroke-color': '#ffc333', 'stroke-width': 4,
      'circle-radius': 10, 'circle-fill-color': '#ffc333',
      'circle-stroke-color': '#fff', 'circle-stroke-width': 3,
    },
  });

  public locateRowStyleOn = signal<boolean>(false);
  public locateRow(row: Record<string, unknown>): void {
    this.locateRowStyleOn.set(true);
    if (!this.isSelectionToolActive() || !this.map || !row['wkb_geometry']) return;

    const geometry = new GeoJSON().readGeometry(row['wkb_geometry'], {
      dataProjection: 'EPSG:4326', featureProjection: this.map.getView().getProjection(),
    });
    this.highlightLayer.getSource()?.clear();
    this.highlightLayer.getSource()?.addFeature(new Feature(geometry));
    if (!this.map.getLayers().getArray().includes(this.highlightLayer)) {
      this.map.addLayer(this.highlightLayer);
    }
    this.map.getView().cancelAnimations();
    this.map.getView().fit(geometry.getExtent(), {
      padding: [100, 100, 100, 100], maxZoom: geometry.getType() === 'Point' ? 10 : 12, duration: 1000,
    });
  }

  public ngOnDestroy(): void {
    this.map?.removeLayer(this.highlightLayer);
  }

  
  // SEARCH TOOL
  public isSearchToolActive = this.ToolbarTools['searchTool'];

  // FITLER TOOL
  public isFilterToolActive = this.ToolbarTools['filterTool'];

  // RESET FILTER TOOL

  // CALCULATE FIELD TOOL
  public isCalculateFieldToolActive = this.ToolbarTools['calculateFieldTool'];

}
