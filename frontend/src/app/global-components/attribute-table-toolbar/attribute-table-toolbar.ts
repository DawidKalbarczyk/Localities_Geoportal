import { Component, input, inject, OnDestroy } from '@angular/core';
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
    if (!this.isSelectionToolActive()) {
      this.highlightLayer.getSource()?.clear();
      this.ToolbarService.highlightLayerRow.set(null);
    }
  }

  // SELECTION TOOL
  public isSelectionToolActive = this.ToolbarTools['selectionTool'];
  public map = this.ToolbarService.mainMap;
  private readonly highlightLayer = new VectorLayer({
    source: new VectorSource(),
    zIndex: 9999,
    style: {
      'fill-color': 'rgba(44, 44, 44, 0.5)',
      'stroke-color': '#2c2c2c', 'stroke-width': 5,
      'circle-radius': 20, 'circle-fill-color': '#2c2c2c',
      'circle-stroke-color': '#fff', 'circle-stroke-width': 3,
    },
  });

  public locateRowStyleOn = this.ToolbarService.locateRowStyleOn;
  public didUserClickedOffLocateRowStyle = this.ToolbarService.didUserClickedOffLocateRowStyle;
  public locateRow(row: Record<string, unknown>): void {
    if (!this.isSelectionToolActive() || !this.map || !row['wkb_geometry']) return;
    this.ToolbarService.highlightLayerRow.set(row);
    if (this.didUserClickedOffLocateRowStyle() === false) {
      this.locateRowStyleOn.set(true);
    }
    

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
    this.ToolbarService.showTransformButton.set(true);
  }

  public ngOnDestroy(): void {
    this.map?.removeLayer(this.highlightLayer);
    this.ToolbarService.resetToolbarTools();
  }

  
  // SEARCH TOOL
  public isSearchToolActive = this.ToolbarTools['searchTool'];

  // FITLER TOOL
  public isFilterToolActive = this.ToolbarTools['filterTool'];

  // RESET FILTER TOOL

  // CALCULATE FIELD TOOL
  public isCalculateFieldToolActive = this.ToolbarTools['calculateFieldTool'];

}
