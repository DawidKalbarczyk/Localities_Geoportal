import { Component, computed, effect, inject, input, OnDestroy, output, signal, untracked } from '@angular/core';
import { AttributeTableToolbarService } from '../../../services/attribute-table-toolbar-service/attribute-table-toolbar-service';
import { FormsModule, NgModel } from '@angular/forms';
import { AsyncPipe, KeyValuePipe } from '@angular/common';
import { TranslatePipe } from '../../../pipes/translate.pipe';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { HttpErrorResponse } from '@angular/common/http';
import { LanguageService } from '../../../services/language/language-service';
import { PopUpService } from '../../../services/pop-up-service/pop-up-service';

type FunctionTooltipSelection = { category: string; func: string };

@Component({
  selector: 'app-calculation-tool',
  imports: [FormsModule, KeyValuePipe, TranslatePipe, AsyncPipe],
  templateUrl: './calculation-tool.html',
  styleUrl: './calculation-tool.scss',
})
export class CalculationTool implements OnDestroy {
  public shownTable = input<Promise<Record<string, unknown>[]>>(Promise.resolve([]));
  public calculationCompleted = output<void>();
  public PopUpService = inject(PopUpService);
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
      if (!this.ToolbarService.ToolbarTools['calculateFieldTool']()) {
        untracked(() => this.hideFunctionTooltip());
      }
    });
    effect(() => {
      this.ToolbarService.calculateFieldResetVersion();
      untracked(() => this.hideFunctionTooltip());
    });
  }
  private http = inject(HttpClient);
  private languageService = inject(LanguageService);
  public parserResult = signal<Record<string, unknown> | null>(null);
  public parserError = signal<string>('');

  public async submitExpression(): Promise<void> {
    this.hideFunctionTooltip();
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
      this.ToolbarService.setParserResult(result);
      this.parserResult.set(result);
      this.parserError.set('');
      this.calculationCompleted.emit();
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
        'map',
        'map_akeys',
        'map_avals',
        'map_concat',
        'map_delete',
        'map_exist',
        'map_get',
        'map_insert',
        'map_prefix_keys',
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
  private hoveredFunction: FunctionTooltipSelection | null = null;
  private pinnedFunction = signal<FunctionTooltipSelection | null>(null);
  private activeFunction = signal<FunctionTooltipSelection | null>(null);
  public functionTooltip = computed(() => {
    const selection = this.activeFunction();
    if (!selection) return null;
    const group = this.model[selection.category];
    return group === 'FIELDS-AND-VALUES'
      ? 'ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.TOOLTIPS.FIELDS-AND-VALUES.TITLE'
      : `ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.TOOLTIPS.${group}._${selection.func.toUpperCase()}.TITLE`;
  });
  public functionTooltipContent = computed(() => {
    const tooltipKey = this.functionTooltip();
    const selection = this.activeFunction();
    if (!tooltipKey || !selection) return null;
    const [, , , group, func] = tooltipKey.split('.');
    if (group === 'FIELDS-AND-VALUES') {
      const tooltip = {
        field_name: selection.func,
        info: 'ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.TOOLTIPS.FIELDS-AND-VALUES.INFO',
        title: 'ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.TOOLTIPS.FIELDS-AND-VALUES.TITLE',
        func_desc: 'ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.TOOLTIPS.FIELDS-AND-VALUES._DESC.DESCRIPTION',
        kind: 'fields' as const
      };
      return tooltip; 
    } else {
      const tooltip = {
        info: `ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.TOOLTIPS.${group}.INFO`,
        title: `ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.TOOLTIPS.${group}.TITLE`,
        func_title: `ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.TOOLTIPS.${group}.${func}.TITLE`,
        func_desc: `ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.TOOLTIPS.${group}.${func}.DESCRIPTION`,
        func_syntax: `ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.TOOLTIPS.${group}.${func}.SYNTAX`,
        func_arg_a: `ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.TOOLTIPS.${group}.${func}.ARGUMENTS.A-KEY`,
        func_arg_b: `ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.TOOLTIPS.${group}.${func}.ARGUMENTS.B-KEY`,
        func_arg_c: `ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.TOOLTIPS.${group}.${func}.ARGUMENTS.C-KEY`,
        func_arg_d: `ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.TOOLTIPS.${group}.${func}.ARGUMENTS.D-KEY`,
        func_arg_e: `ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.TOOLTIPS.${group}.${func}.ARGUMENTS.E-KEY`,
        func_arg_f: `ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.TOOLTIPS.${group}.${func}.ARGUMENTS.F-KEY`,
        func_desc_a: `ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.TOOLTIPS.${group}.${func}.ARGUMENTS.A-DESCRIPTION`,
        func_desc_b: `ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.TOOLTIPS.${group}.${func}.ARGUMENTS.B-DESCRIPTION`,
        func_desc_c: `ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.TOOLTIPS.${group}.${func}.ARGUMENTS.C-DESCRIPTION`,
        func_desc_d: `ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.TOOLTIPS.${group}.${func}.ARGUMENTS.D-DESCRIPTION`,
        func_desc_e: `ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.TOOLTIPS.${group}.${func}.ARGUMENTS.E-DESCRIPTION`,
        func_desc_f: `ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.TOOLTIPS.${group}.${func}.ARGUMENTS.F-DESCRIPTION`,
        func_ex_1: `ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.TOOLTIPS.${group}.${func}.EXAMPLES.EX1`,
        func_ex_2: `ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.TOOLTIPS.${group}.${func}.EXAMPLES.EX2`,
        func_ex_3: `ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.TOOLTIPS.${group}.${func}.EXAMPLES.EX3`,
        func_res_1: `ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.TOOLTIPS.${group}.${func}.EXAMPLES.RES1`,
        func_res_2: `ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.TOOLTIPS.${group}.${func}.EXAMPLES.RES2`,
        func_res_3: `ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.TOOLTIPS.${group}.${func}.EXAMPLES.RES3`,
        kind: 'rest' as const
      };
      return tooltip;
    }
  })

  public functionHoverEnter(
    category: string,
    func: string,
  ): void {
    const selection = { category, func };
    this.hoveredFunction = selection;
    this.keepFunctionTooltipOpen();
    this.activeFunction.set(this.pinnedFunction());
    this.timeout = setTimeout(() => {
      this.activeFunction.set(selection);
      this.timeout = null;
    }, 500);
  }

  public functionHoverLeave(): void {
    this.hoveredFunction = null;
    this.keepFunctionTooltipOpen();
    if (this.activeFunction() === this.pinnedFunction()) return;
    this.timeout = setTimeout(() => {
      this.activeFunction.set(this.pinnedFunction());
      this.timeout = null;
    }, 500);
  }

  public toggleFunctionTooltip(category: string, func: string): void {
    if (this.isFunctionPinned(category, func)) {
      this.keepFunctionTooltipOpen();
      this.pinnedFunction.set(null);
      this.activeFunction.set(this.hoveredFunction);
      return;
    }
    this.keepFunctionTooltipOpen();
    const selection = { category, func };
    this.pinnedFunction.set(selection);
    this.activeFunction.set(selection);
  }

  public isFunctionPinned(category: string, func: string): boolean {
    const selection = this.pinnedFunction();
    return selection?.category === category && selection?.func === func;
  }

  public insertTooltipFunction(textarea: HTMLTextAreaElement): void {
    const selection = this.activeFunction();
    if (selection) {
      this.ToolbarService.insertFunctionIntoExpression(selection.func, textarea);
    }
  }

  public keepFunctionTooltipOpen(): void {
    if (this.timeout !== null) {
      clearTimeout(this.timeout);
      this.timeout = null;
    }
  }

  public hideFunctionTooltip(): void {
    this.keepFunctionTooltipOpen();
    this.hoveredFunction = null;
    this.pinnedFunction.set(null);
    this.activeFunction.set(null);
  }
  

}
