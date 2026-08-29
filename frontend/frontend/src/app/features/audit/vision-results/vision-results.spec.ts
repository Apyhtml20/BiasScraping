import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VisionResults } from './vision-results';

describe('VisionResults', () => {
  let component: VisionResults;
  let fixture: ComponentFixture<VisionResults>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [VisionResults],
    }).compileComponents();

    fixture = TestBed.createComponent(VisionResults);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
