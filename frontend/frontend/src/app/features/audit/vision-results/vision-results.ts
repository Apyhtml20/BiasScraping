import { Component, computed, input, signal } from '@angular/core';

import { AuditImage } from '../../../core/models/audit.model';

@Component({
  selector: 'app-vision-results',
  imports: [],
  templateUrl: './vision-results.html',
  styleUrl: './vision-results.css',
})
export class VisionResults {
  readonly images = input<AuditImage[]>([]);

  protected readonly brokenIds = signal<Set<string>>(new Set());

  protected readonly withPeopleCount = computed(
    () => this.images().filter((image) => image.people_count > 0).length,
  );

  protected markBroken(imageId: string): void {
    this.brokenIds.update((set) => new Set(set).add(imageId));
  }

  protected prominencePercent(image: AuditImage): number {
    return Math.round(image.people_prominence * 100);
  }
}
