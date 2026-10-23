import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AttributeTableToolbar } from './attribute-table-toolbar';

describe('AttributeTableToolbar', () => {
  let component: AttributeTableToolbar;
  let fixture: ComponentFixture<AttributeTableToolbar>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AttributeTableToolbar],
    }).compileComponents();

    fixture = TestBed.createComponent(AttributeTableToolbar);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
