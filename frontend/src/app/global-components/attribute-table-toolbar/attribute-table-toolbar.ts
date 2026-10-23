import { Component, input, inject, signal } from '@angular/core';
import { MatTooltipModule } from '@angular/material/tooltip';
import { AttributeTableToolbarService } from '../../services/attribute-table-toolbar-service/attribute-table-toolbar-service';
import { TranslatePipe } from '../../pipes/translate.pipe';

@Component({
  selector: 'app-attribute-table-toolbar',
  imports: [MatTooltipModule, TranslatePipe],
  templateUrl: './attribute-table-toolbar.html',
  styleUrl: './attribute-table-toolbar.scss',
})
export class AttributeTableToolbar {
  attributeSuggestionsTableSearch = input<string[]>([]);
  public ToolbarService = inject(AttributeTableToolbarService);

  private ToolbarTools = this.ToolbarService.ToolbarTools;
  public ToolbarMatTooltip = this.ToolbarService.ToolbarMatTooltip;
  public toggleTool = this.ToolbarService.toggleActivationTool;

  // SELECTION TOOL
  public isSelectionToolActive = this.ToolbarTools['selectionTool'];
  
  // SEARCH TOOL
  public isSearchToolActive = this.ToolbarTools['searchTool'];

  // FITLER TOOL
  public isFilterToolActive = this.ToolbarTools['filterTool'];

  // RESET FILTER TOOL

  // CALCULATE FIELD TOOL
  public isCalculateFieldToolActive = this.ToolbarTools['calculateFieldTool'];
}
