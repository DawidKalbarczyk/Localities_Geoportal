import { TestBed } from '@angular/core/testing';

import { AttributeTableToolbarService } from './attribute-table-toolbar-service';

describe('AttributeTableToolbarService', () => {
  let service: AttributeTableToolbarService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(AttributeTableToolbarService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
