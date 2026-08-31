import { Component, computed, input, signal } from '@angular/core';

import { AuditImage, Representation } from '../../../core/models/audit.model';

@Component({
  selector: 'app-vision-results',
  imports: [],
  templateUrl: './vision-results.html',
  styleUrl: './vision-results.css',
})
export class VisionResults {
  readonly images = input<AuditImage[]>([]);
  readonly representation = input<Representation | null>(null);

  protected readonly brokenIds = signal<Set<string>>(new Set());

  protected readonly withPeopleCount = computed(
    () => this.images().filter((image) => image.people_count > 0).length,
  );

  protected readonly presentationCategories = computed(() => {
    const rep = this.representation();
    if (!rep || rep.faces_detected === 0) return [];
    return (Object.entries(rep.category_ratios) as [string, number][])
      .filter(([, ratio]) => ratio > 0)
      .sort(([, a], [, b]) => b - a)
      .map(([category, ratio]) => ({
        label: this.categoryLabel(category),
        percent: Math.round(ratio * 100),
      }));
  });

  private categoryLabel(category: string): string {
    switch (category) {
      case 'feminine_presenting':
        return 'Feminine-presenting';
      case 'masculine_presenting':
        return 'Masculine-presenting';
      case 'androgynous_presenting':
        return 'Androgynous-presenting';
      default:
        return 'Undetermined';
    }
  }

  protected markBroken(imageId: string): void {
    this.brokenIds.update((set) => new Set(set).add(imageId));
  }

  protected prominencePercent(image: AuditImage): number {
    return Math.round(image.people_prominence * 100);
  }
}
