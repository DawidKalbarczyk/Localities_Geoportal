import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MapInfo } from './map-info';

describe('MapInfo', () => {
  let component: MapInfo;
  let fixture: ComponentFixture<MapInfo>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MapInfo],
    }).compileComponents();

    fixture = TestBed.createComponent(MapInfo);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
