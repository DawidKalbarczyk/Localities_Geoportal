import { Component, effect, input, signal } from '@angular/core';
import { AsyncPipe, KeyValuePipe, SlicePipe } from '@angular/common';
import { CdkScrollable } from '@angular/cdk/scrolling';
import { MatTooltipModule } from '@angular/material/tooltip';
import { TranslatePipe } from '../../../../../pipes/translate.pipe';

@Component({
  selector: 'app-attribute-table',
  imports: [AsyncPipe, KeyValuePipe, SlicePipe, CdkScrollable, MatTooltipModule, TranslatePipe],
  templateUrl: './attribute-table.html',
  styleUrl: './attribute-table.scss',
})
export class AttributeTable {
  shownTable = input<Promise<Record<string, unknown>[]>>(Promise.resolve([]));
  isShownTableEmpty = input<boolean>(false);
  private readonly batchSize = 100;
  public visibleRowCount = signal(this.batchSize);

  constructor() {
    effect(() => {
      this.shownTable();
      this.isShownTableEmpty();
      this.visibleRowCount.set(this.batchSize);
    });
  }

  public onTableScroll(event: Event, totalRows: number): void {
    const container = event.currentTarget as HTMLElement;
    const distanceToBottom = container.scrollHeight - container.scrollTop - container.clientHeight;

    if (distanceToBottom <= 80 && this.visibleRowCount() < totalRows) {
      this.visibleRowCount.update(count => Math.min(count + this.batchSize, totalRows));
    }
  }
}
