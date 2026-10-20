import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AttributeTable } from './attribute-table';

describe('AttributeTable', () => {
  let component: AttributeTable;
  let fixture: ComponentFixture<AttributeTable>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AttributeTable],
    }).compileComponents();

    fixture = TestBed.createComponent(AttributeTable);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
