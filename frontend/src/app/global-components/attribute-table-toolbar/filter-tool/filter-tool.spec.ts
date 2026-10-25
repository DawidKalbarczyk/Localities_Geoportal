import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FilterTool } from './filter-tool';

describe('FilterTool', () => {
  let component: FilterTool;
  let fixture: ComponentFixture<FilterTool>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FilterTool],
    }).compileComponents();

    fixture = TestBed.createComponent(FilterTool);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
