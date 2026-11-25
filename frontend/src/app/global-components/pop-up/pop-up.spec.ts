import { ComponentFixture, TestBed } from '@angular/core/testing';
import { signal } from '@angular/core';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';

import { PopUp } from './pop-up';
import { PopUpService } from '../../services/pop-up-service/pop-up-service';
import { ObjSelection } from '../../services/obj-selection/obj-selection';
import { AMService } from '../../services/a-m-service/a-m-service';
import { LanguageService } from '../../services/language/language-service';

describe('PopUp', () => {
  let component: PopUp;
  let fixture: ComponentFixture<PopUp>;
  let http: HttpTestingController;
  let popupState: Pick<PopUpService, 'typeOfPopUp' | 'attributeLayer' | 'attributeDescriptions' | 'resetPopUp'>;

  beforeEach(async () => {
    popupState = {
      typeOfPopUp: signal(''),
      attributeLayer: signal('boundsLayerPanstwo'),
      attributeDescriptions: signal<Record<string, string>>({ jpt_nazwa_: 'Layer name' }),
      resetPopUp: vi.fn(),
    };
    await TestBed.configureTestingModule({
      imports: [PopUp],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
        { provide: PopUpService, useValue: popupState },
        { provide: ObjSelection, useValue: {} },
        { provide: AMService, useValue: { wasSaved: signal(false) } },
        { provide: LanguageService, useValue: { translate: (key: string) => key } },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(PopUp);
    component = fixture.componentInstance;
    http = TestBed.inject(HttpTestingController);
    await fixture.whenStable();
  });

  afterEach(() => http.verify());

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it.each(['info', 'filter'] as const)('loads attributes and shows the correct help for %s', async type => {
    popupState.typeOfPopUp.set(type);
    fixture.detectChanges();
    const request = http.expectOne('/save/get-xml-as-json?url=http://geoserver:8080/geoserver/rest/workspaces/AngularLocal/featuretypes/boundspanstwo.json');
    request.flush({
      featureType: {
        name: 'boundspanstwo',
        attributes: { attribute: [{ name: 'jpt_nazwa_' }] },
      },
    });
    await fixture.whenStable();
    fixture.detectChanges();

    const element = fixture.nativeElement as HTMLElement;
    expect(element.querySelector('.pop-up-title')?.textContent?.trim()).toBe(
      type === 'info' ? 'POP-UP.INFO.TITLE' : 'POP-UP.FILTER.TITLE',
    );
    expect(element.querySelector('.pop-up-desc') !== null).toBe(type === 'filter');
    expect(element.querySelector('.help-content')?.textContent).toContain('jpt_nazwa_');
    if (type === 'filter') {
      expect(element.querySelector('.pop-up-desc')?.textContent).toContain('POP-UP.FILTER.CONTENT.CON1');
      expect(element.textContent).not.toContain('POP-UP.INFO.');
    }
  });

  it('keeps calculator help separate from layer attribute requests', async () => {
    popupState.typeOfPopUp.set('calculate-tool');
    fixture.detectChanges();
    await fixture.whenStable();

    expect(fixture.nativeElement.querySelector('.pop-up-title')?.textContent?.trim()).toBe('POP-UP.CALC-TOOL.TITLE');
    http.expectNone(() => true);
  });
});
