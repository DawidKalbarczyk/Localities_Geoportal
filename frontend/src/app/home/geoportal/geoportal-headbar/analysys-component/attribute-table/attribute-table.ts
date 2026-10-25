import { afterNextRender, Component, effect, input, signal, inject, Injector } from '@angular/core';
import { AsyncPipe, KeyValuePipe, SlicePipe } from '@angular/common';
import { CdkScrollable } from '@angular/cdk/scrolling';
import { MAT_TOOLTIP_DEFAULT_OPTIONS, MatTooltipModule } from '@angular/material/tooltip';
import { TranslatePipe } from '../../../../../pipes/translate.pipe';
import { AttributeTableToolbar } from '../../../../../global-components/attribute-table-toolbar/attribute-table-toolbar';
import { AttributeTableToolbarService } from '../../../../../services/attribute-table-toolbar-service/attribute-table-toolbar-service';
import { FilterTool } from '../../../../../global-components/attribute-table-toolbar/filter-tool/filter-tool';

@Component({
  selector: 'app-attribute-table',
  imports: [FilterTool, AsyncPipe, KeyValuePipe, SlicePipe, CdkScrollable, MatTooltipModule, TranslatePipe, AttributeTableToolbar],
  templateUrl: './attribute-table.html',
  styleUrl: './attribute-table.scss',
  providers: [{
    provide: MAT_TOOLTIP_DEFAULT_OPTIONS,
    useValue: {
      showDelay: 0,
      hideDelay: 0,
      touchendHideDelay: 1500,
      disableTooltipInteractivity: true,
    },
  }],
})
export class AttributeTable {
  private readonly injector = inject(Injector);
  shownTable = input<Promise<Record<string, unknown>[]>>(Promise.resolve([]));
  ToolbarService = inject(AttributeTableToolbarService);
  isShownTableEmpty = input<boolean>(false);
  attributeSuggestionsTableSearch = input<string[]>([]);
  private readonly batchSize = 100;
  public visibleRowCount = signal(this.batchSize);
  public rowStartIndex = signal(0);
  public readonly rowHeight = 32;

  constructor() {
    effect(() => {
      this.shownTable();
      this.isShownTableEmpty();
      this.visibleRowCount.set(this.batchSize);
      this.rowStartIndex.set(0);
    });
  }

  public revealRow(row: Record<string, unknown>, table: Record<string, unknown>[], container: HTMLElement, toolbar: AttributeTableToolbar): void {
    const index = table.indexOf(row);
    if (index === -1) return;
    this.rowStartIndex.set(Math.max(0, Math.min(index - 20, table.length - this.batchSize)));
    afterNextRender(() => {
      if (this.ToolbarService.highlightLayerRow() !== row) return;
      const element = container.querySelector('.highlighted-row');
      if (!element) return;
      element.scrollIntoView({ block: 'nearest', inline: 'nearest' });
      requestAnimationFrame(() => toolbar.animateToRow(row));
    }, { injector: this.injector });
  }

  public onTableScroll(event: Event, totalRows: number): void {
    const container = event.currentTarget as HTMLElement;
    const start = Math.floor(container.scrollTop / this.rowHeight) - 20;
    this.rowStartIndex.set(Math.max(0, Math.min(start, totalRows - this.batchSize)));
  }

  public columnCount(row: Record<string, unknown> | undefined): number {
    return row ? Object.keys(row).filter(key => key !== 'wkb_geometry').length : 1;
  }

///////////////// SORT VALUES IN THE ATTRIBUTE TABLE ////////////////////////

  private isSortedAscending = signal(false);
  public sortTableData(data: Record<string, unknown>[], attributeKey: string): Record<string, unknown>[] {
    const ascending = !this.isSortedAscending();
    this.isSortedAscending.set(ascending);

    return data.sort((a, b) => {
      const aValue = a[attributeKey] as string;
      const bValue = b[attributeKey] as string;

      if (aValue < bValue) return ascending ? -1 : 1;
      if (aValue > bValue) return ascending ? 1 : -1;
      return 0;
    });
  }

///////////////// SELECTION/MULTI-SELECTION HANDLING ////////////////////////

  
}
