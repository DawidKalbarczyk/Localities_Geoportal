import { Component, input, inject, OnDestroy, output, signal } from '@angular/core';
import { FormsModule, NgForm, NgModel } from '@angular/forms'
import { MatTooltipModule } from '@angular/material/tooltip';
import { AttributeTableToolbarService } from '../../services/attribute-table-toolbar-service/attribute-table-toolbar-service';
import { TranslatePipe } from '../../pipes/translate.pipe';
import Feature from 'ol/Feature';
import GeoJSON from 'ol/format/GeoJSON';

@Component({
  selector: 'app-attribute-table-toolbar',
  imports: [MatTooltipModule, TranslatePipe, FormsModule],
  templateUrl: './attribute-table-toolbar.html',
  styleUrl: './attribute-table-toolbar.scss',
})
export class AttributeTableToolbar implements OnDestroy {
  shownTable = input<Promise<Record<string, unknown>[]>>(Promise.resolve([]));
  attributeSuggestionsTableSearch = input<string[]>([]);
  public rowLocated = output<Record<string, unknown>>();
  public ToolbarService = inject(AttributeTableToolbarService);

  private ToolbarTools = this.ToolbarService.ToolbarTools;
  public ToolbarMatTooltip = this.ToolbarService.ToolbarMatTooltip;
  public toggleTool(tool: string): void {
    this.ToolbarService.toggleActivationTool(tool);
    if (tool === 'searchTool' && !this.isSearchToolActive()) {
      this.searchInput.set('');
      this.ToolbarService.resetToolbarTools();
    }
    if (tool === 'selectionTool' && !this.isSelectionToolActive()) {
      this.ToolbarService.resetToolbarTools();
    }
  }

  // SELECTION TOOL
  public isSelectionToolActive = this.ToolbarTools['selectionTool'];
  public map = this.ToolbarService.mainMap;
  private readonly highlightLayer = this.ToolbarService.highlightLayer;

  public locateRowStyleOn = this.ToolbarService.locateRowStyleOn;
  public didUserClickedOffLocateRowStyle = this.ToolbarService.didUserClickedOffLocateRowStyle;
  public locateRow(row: Record<string, unknown>): void {
    if (!this.map || !row['wkb_geometry']) return;
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
    this.ToolbarService.showTransformButton.set(true);
    this.rowLocated.emit(row);
  }

  public animateToRow(row: Record<string, unknown>): void {
    if (!this.map || this.ToolbarService.highlightLayerRow() !== row) return;
    const geometry = this.highlightLayer.getSource()?.getFeatures()[0]?.getGeometry();
    if (!geometry) return;
    const view = this.map.getView();
    view.cancelAnimations();
    view.fit(geometry.getExtent(), {
      padding: [100, 100, 100, 100], maxZoom: geometry.getType() === 'Point' ? 10 : 12, duration: 1000,
    });
  }

  public ngOnDestroy(): void {
    this.ToolbarService.resetToolbarTools();
  }

  
  // SEARCH TOOL
  public isSearchToolActive = this.ToolbarTools['searchTool'];
  public searchInput = signal<string>('');
  public async locateSearchRow(): Promise<void> {
    const query = this.searchInput().trim().toLowerCase();
    if (!query) return;
    const table = this.shownTable();
    const rows = await table;
    if (!this.isSearchToolActive() || table !== this.shownTable() || query !== this.searchInput().trim().toLowerCase()) return;
    const row = rows.find(row => String(row['nazwa'] ?? row['jpt_nazwa_'] ?? '').trim().toLowerCase() === query);
    if (row) this.locateRow(row);
  }

  // FITLER TOOL
  public isFilterToolActive = this.ToolbarTools['filterTool'];

  // RESET FILTER TOOL

  // CALCULATE FIELD TOOL
  public isCalculateFieldToolActive = this.ToolbarTools['calculateFieldTool'];

}
