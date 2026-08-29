import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ScoreCard } from './score-card';

describe('ScoreCard', () => {
  let component: ScoreCard;
  let fixture: ComponentFixture<ScoreCard>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ScoreCard],
    }).compileComponents();

    fixture = TestBed.createComponent(ScoreCard);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
