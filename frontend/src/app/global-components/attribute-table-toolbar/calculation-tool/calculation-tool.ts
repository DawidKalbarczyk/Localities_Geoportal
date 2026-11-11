import { Component, computed, effect, inject, input, OnDestroy, signal, untracked } from '@angular/core';
import { AttributeTableToolbarService } from '../../../services/attribute-table-toolbar-service/attribute-table-toolbar-service';
import { FormsModule, NgModel } from '@angular/forms';
import { AsyncPipe, KeyValuePipe } from '@angular/common';
import { TranslatePipe } from '../../../pipes/translate.pipe';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { HttpErrorResponse } from '@angular/common/http';
import { LanguageService } from '../../../services/language/language-service';

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
    this.hideFunctionTooltip();
    this.ToolbarService.resetCalculateFieldTool();
  }


  constructor() {
    effect(() => {
      this.functionsModelCreate();
    });
    effect(() => {
      const result = this.parserResult();
      untracked(() => {
        this.ToolbarService.setParserResult(result);
      });
    })
    effect(() => {
      if (!this.ToolbarService.ToolbarTools['calculateFieldTool']()) {
        this.hideFunctionTooltip();
      }
    });
  }
  private http = inject(HttpClient);
  private languageService = inject(LanguageService);
  public parserResult = signal<Record<string, unknown> | null>(null);
  public parserError = signal<string>('');

  public async submitExpression(): Promise<void> {
    let checked_keys = []
    for (const key of await this.shownTableKeys()) {
      if (this.expression().includes(key)) {
        checked_keys.push(key);
      }
    }
    const table = (await this.shownTable()).map(row => 
      Object.fromEntries(
        Object.entries(row).filter(([key]) => 
          key !== 'wkb_geometry' &&
          checked_keys.includes(key)
        )
      )
    )
    console.log(table);
    try {
      const result = await firstValueFrom(this.http.post<Record<string, unknown>>('/calculate-tool/calculate-field', { 
        expression: this.expression(), 
        table: table, 
        tableKeys: await this.shownTableKeys() 
      }));
      this.parserResult.set(result);
      this.parserError.set('');
    } catch (error: unknown) {
      const detail = error instanceof HttpErrorResponse 
        ? error.error?.detail
        : 'Unknown error';

      if (typeof detail === 'object' && detail !== null && typeof detail.code === 'string') {
        this.parserError.set(this.languageService.translate(detail.code, detail.params));
      } else {
        this.parserError.set(typeof detail === 'string' ? detail : 'Nie udało się wykonać obliczenia.');
      }
    }
    
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
        '!=', // !=
        '<', // <
        '>', // >
        '<=', // <=
        '>=', // >=
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



  public model: Record<string, string> = {
    'ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.CONTENT.FUNCTIONS-NAMES.FIELDS-AND-VALUES': "FIELDS-AND-VALUES",
    'ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.CONTENT.FUNCTIONS-NAMES.DATE-AND-TIME': "DATE-AND-TIME",
    'ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.CONTENT.FUNCTIONS-NAMES.MATH': "MATH",
    'ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.CONTENT.FUNCTIONS-NAMES.OPERATORS': "OPERATORS",
    'ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.CONTENT.FUNCTIONS-NAMES.MAPS-OPERATORS': "MAPS-OPERATORS",
    'ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.CONTENT.FUNCTIONS-NAMES.STRING-OPERATORS': "STRING-OPERATORS"
  };

  private timeout: ReturnType<typeof setTimeout> | null = null;
  public functionTooltip = signal<string | null>(null);

  public functionHoverEnter(
    category: string,
    func: string,
  ): void {
    this.hideFunctionTooltip();
    this.timeout = setTimeout(() => {
      const group = this.model[category];

      this.functionTooltip.set(
        group === 'FIELDS-AND-VALUES'
          ? 'ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.TOOLTIPS.FIELDS-AND-VALUES.TITLE'
          : `ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.TOOLTIPS.${group}.${func.toUpperCase()}.TITLE`,
      );
      this.timeout = null;
    }, 500);
  }

  public functionHoverLeave(): void {
    this.keepFunctionTooltipOpen();
    this.timeout = setTimeout(() => {
      this.hideFunctionTooltip();
    }, 250);
  }

  public keepFunctionTooltipOpen(): void {
    if (this.timeout !== null) {
      clearTimeout(this.timeout);
      this.timeout = null;
    }
  }

  public hideFunctionTooltip(): void {
    this.keepFunctionTooltipOpen();
    this.functionTooltip.set(null);
  }
  

}
