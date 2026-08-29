import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';

import { AuditProgress } from './audit-progress';

describe('AuditProgress', () => {
  let component: AuditProgress;
  let fixture: ComponentFixture<AuditProgress>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AuditProgress],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();

    fixture = TestBed.createComponent(AuditProgress);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
