import { Component, inject, OnDestroy, input, computed, signal, effect} from '@angular/core';
import { AttributeTableToolbarService } from '../../../services/attribute-table-toolbar-service/attribute-table-toolbar-service';
import { AsyncPipe, KeyValuePipe, SlicePipe } from '@angular/common';
import { Form, NgModel } from '@angular/forms';
import { TranslatePipe } from '../../../pipes/translate.pipe';
import { PopUpService } from '../../../services/pop-up-service/pop-up-service';

@Component({
  selector: 'app-filter-tool',
  imports: [AsyncPipe, KeyValuePipe, TranslatePipe, SlicePipe],
  templateUrl: './filter-tool.html',
  styleUrl: './filter-tool.scss',
})
export class FilterTool implements OnDestroy {
  public ToolbarService = inject(AttributeTableToolbarService);
  public PopUpService = inject(PopUpService);
  public shownTable = input<Promise<Record<string, unknown>[]>>(Promise.resolve([]));

  constructor() {
    effect(() => {
      this.ToolbarService.setShownTable(this.shownTable());
    })
  }

  ngOnDestroy(): void {
    this.ToolbarService.resetToolbarTools('filterTool');
  }

  public shownTableKeys = computed(() => {
    return this.shownTable().then(table => {
      if (table.length === 0) return [];
      return (Object.keys(table[0]).filter(key => key !== 'wkb_geometry'));
    });
  })

  testFunc(): void {
    console.log("Applying filters to table:", this.shownTableKeys());
  }

  public showStaticHelp(): void {
    this.PopUpService.typeOfPopUp.set('info');
    this.PopUpService.getDescriptionsJSON();
  }

  searchInput = signal<string>('');
}
