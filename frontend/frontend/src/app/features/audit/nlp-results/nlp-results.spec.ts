import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NlpResults } from './nlp-results';

describe('NlpResults', () => {
  let component: NlpResults;
  let fixture: ComponentFixture<NlpResults>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NlpResults],
    }).compileComponents();

    fixture = TestBed.createComponent(NlpResults);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
