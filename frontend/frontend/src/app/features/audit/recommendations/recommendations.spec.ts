import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Recommendations } from './recommendations';

describe('Recommendations', () => {
  let component: Recommendations;
  let fixture: ComponentFixture<Recommendations>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Recommendations],
    }).compileComponents();

    fixture = TestBed.createComponent(Recommendations);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
