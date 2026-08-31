import { DecimalPipe } from '@angular/common';
import { Component, computed, input } from '@angular/core';

import { BiasStateVector, WorldModel, WorldModelRollout } from '../../../core/models/audit.model';

const ACTION_NAMES: Record<number, string> = {
  0: 'Reduce language bias',
  1: 'Diversify sources',
  2: 'Add balanced viewpoint',
  3: 'Improve visual representation',
};

interface StateDimension {
  key: keyof BiasStateVector;
  label: string;
}

const DIMENSIONS: StateDimension[] = [
  { key: 'nlp_health', label: 'Language health' },
  { key: 'vision_health', label: 'Visual quality' },
  { key: 'representation_balance', label: 'Representation balance' },
  { key: 'people_image_ratio', label: 'People / image ratio' },
  { key: 'diversity', label: 'Diversity' },
  { key: 'inclusivity', label: 'Inclusivity' },
];

@Component({
  selector: 'app-world-model',
  imports: [DecimalPipe],
  templateUrl: './world-model.html',
  styleUrl: './world-model.css',
})
export class WorldModelCard {
  readonly worldModel = input<WorldModel | null>(null);

  protected readonly dimensions = DIMENSIONS;

  protected readonly otherRollouts = computed<WorldModelRollout[]>(() => {
    const wm = this.worldModel();
    if (!wm) return [];
    return wm.rollouts.filter((rollout) => rollout.action !== wm.recommended_action.id);
  });

  protected actionName(actionId: number): string {
    return ACTION_NAMES[actionId] ?? `Action ${actionId}`;
  }

  protected percent(value: number): number {
    return Math.round(Math.max(0, Math.min(1, value)) * 100);
  }
}
