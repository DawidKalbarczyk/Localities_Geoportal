import { afterNextRender, Component, effect, input, signal, inject, Injector } from '@angular/core';
import { AsyncPipe, KeyValuePipe, SlicePipe } from '@angular/common';
import { CdkScrollable } from '@angular/cdk/scrolling';
import { MAT_TOOLTIP_DEFAULT_OPTIONS, MatTooltipModule } from '@angular/material/tooltip';
import { TranslatePipe } from '../../../../../pipes/translate.pipe';
import { AttributeTableToolbar } from '../../../../../global-components/attribute-table-toolbar/attribute-table-toolbar';
import { AttributeTableToolbarService } from '../../../../../services/attribute-table-toolbar-service/attribute-table-toolbar-service';

@Component({
  selector: 'app-attribute-table',
  imports: [AsyncPipe, KeyValuePipe, SlicePipe, CdkScrollable, MatTooltipModule, TranslatePipe, AttributeTableToolbar],
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

  constructor() {
    effect(() => {
      this.shownTable();
      this.isShownTableEmpty();
      this.visibleRowCount.set(this.batchSize);
    });
  }

  public revealRow(row: Record<string, unknown>, table: Record<string, unknown>[], container: HTMLElement, toolbar: AttributeTableToolbar): void {
    this.visibleRowCount.update(count => Math.max(count, table.indexOf(row) + 1));
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
    const distanceToBottom = container.scrollHeight - container.scrollTop - container.clientHeight;

    if (distanceToBottom <= 80 && this.visibleRowCount() < totalRows) {
      this.visibleRowCount.update(count => Math.min(count + this.batchSize, totalRows));
    }
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
