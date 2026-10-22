import { Component, input } from '@angular/core';
import { MatTooltipModule } from '@angular/material/tooltip';

@Component({
  selector: 'app-attribute-table-toolbar',
  imports: [MatTooltipModule],
  templateUrl: './attribute-table-toolbar.html',
  styleUrl: './attribute-table-toolbar.scss',
})
export class AttributeTableToolbar {
  attributeSuggestionsTableSearch = input<string[]>([]);
}
