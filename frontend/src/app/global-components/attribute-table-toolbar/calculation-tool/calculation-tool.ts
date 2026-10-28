import { Component, computed, effect, inject, input, OnDestroy, signal } from '@angular/core';
import { AttributeTableToolbarService } from '../../../services/attribute-table-toolbar-service/attribute-table-toolbar-service';
import { FormsModule, NgModel } from '@angular/forms';
import { AsyncPipe, KeyValuePipe } from '@angular/common';
import { TranslatePipe } from '../../../pipes/translate.pipe';

@Component({
  selector: 'app-calculation-tool',
  imports: [FormsModule, KeyValuePipe, TranslatePipe, AsyncPipe],
  templateUrl: './calculation-tool.html',
  styleUrl: './calculation-tool.scss',
})
export class CalculationTool implements OnDestroy {
  public shownTable = input<Promise<Record<string, unknown>[]>>(Promise.resolve([]));
  public ToolbarService = inject(AttributeTableToolbarService);
  public expression = this.ToolbarService.userExpression;
  public expressionScrollTop = signal(0);
  public expressionLines = computed(() =>
    this.expression().split('\n').map((text, index) => ({ number: index + 1, text })),
  );

  public shownTableKeys = computed(() => {
    return this.shownTable().then(table => {
      if (table.length === 0) return [];
      return (Object.keys(table[0]).filter(key => key !== 'wkb_geometry'));
    });
  })

  ngOnDestroy() {
    this.ToolbarService.resetCalculateFieldTool();
  }


  constructor() {
    effect(() => {
      this.functionsModelCreate();
    });
  }

  public functionsModel = signal<Record<string, string[]>>({});
  public async functionsModelCreate(): Promise<void> {
    this.functionsModel.set({
      'ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.CONTENT.FUNCTIONS-NAMES.FIELDS-AND-VALUES': await this.shownTableKeys(),
      'ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.CONTENT.FUNCTIONS-NAMES.DATE-AND-TIME': [
        'age',
        'datetime_from_epoch',
        'day',
        'day_of_week',
        'epoch',
        'format_date',
        'hour',
        'make_date',
        'make_datetime',
        'make_interval',
        'make_time',
        'minute',
        'month',
        'now',
        'second',
        'to_date',
        'to_datetime',
        'to_interval',
        'to_time',
        'week',
        'year'
      ],
      'ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.CONTENT.FUNCTIONS-NAMES.MATH': [
        'abs',
        'acos',
        'asin',
        'atan',
        'atan2',
        'actg',
        'actg2',
        'ceil',
        'clamp',
        'sin',
        'cos',
        'tan',
        'ctg',
        'degrees',
        'exp',
        'floor',
        'ln',
        'log',
        'log10',
        'max',
        'min',
        'pi',
        'pow',
        'radians',
        'rand',
        'randf',
        'round',
        'scale_exponential',
        'scale_linear',
        'scale_polynomial',
        'scale_logarithmic',
        'sqrt',
        
      ],
      'ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.CONTENT.FUNCTIONS-NAMES.OPERATORS': [
        '−', // -
        '+', // +
        '×', // *
        '÷', // /
        '÷÷', // //
        '[]', // []
        '%', // %
        '^', // ^
        '=', // =
        '≠', // !=
        '<', // <
        '>', // >
        '≤', // <=
        '≥', // >=
        '||', // ||
        '∼', // ~
        'AND',
        'OR',
        'IN',
        'IS',
        'IS NOT',
        'LIKE',
        'ILIKE',
        'NOT',
        'BETWEEN',
        'NOT BETWEEN',
      ],
      'ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.CONTENT.FUNCTIONS-NAMES.MAPS-OPERATORS': [
        'from_json',
        'hstore_to_map',
        'map',
        'map_akeys',
        'map_avals',
        'map_concat',
        'map_delete',
        'map_exist',
        'map_get',
        'map_insert',
        'map_prefix_keys',
        'map_to_hstore',
        'map_to_html_dl',
        'map_to_html_table',
        'to_json',
        'url_encode'
      ],
      'ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.CONTENT.FUNCTIONS-NAMES.STRING-OPERATORS': [
        'ascii',
        'char',
        'concat',
        'format',
        'format_date',
        'format_number',
        'left',
        'length',
        'lower',
        'lpad',
        'ltrim',
        'regexp_match',
        'regexp_replace',
        'regexp_substr',
        'replace',
        'right',
        'rpad',
        'rtrim',
        'strpos',
        'substr',
        'title',
        'to_string',
        'trim',
        'upper',
        'wordwrap'
      ]
    });
  }
  
}
