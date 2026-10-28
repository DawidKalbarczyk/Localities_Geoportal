import { ComponentFixture, TestBed } from '@angular/core/testing';
import { signal } from '@angular/core';

import { CalculationTool } from './calculation-tool';
import { AttributeTableToolbarService } from '../../../services/attribute-table-toolbar-service/attribute-table-toolbar-service';

describe('CalculationTool', () => {
  let component: CalculationTool;
  let fixture: ComponentFixture<CalculationTool>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CalculationTool],
      providers: [{
        provide: AttributeTableToolbarService,
        useValue: {
          ToolbarTools: { calculateFieldTool: signal(true) },
          calculationType: signal('new'),
        },
      }],
    }).compileComponents();

    fixture = TestBed.createComponent(CalculationTool);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
