import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';

import { UrlInput } from './url-input';

describe('UrlInput', () => {
  let component: UrlInput;
  let fixture: ComponentFixture<UrlInput>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UrlInput],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();

    fixture = TestBed.createComponent(UrlInput);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
