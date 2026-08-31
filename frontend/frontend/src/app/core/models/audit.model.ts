export type IssueSeverity = 'high' | 'medium' | 'low';

export interface AuditIssue {
  module: 'nlp' | 'computer_vision' | 'representation';
  paragraph_id?: string;
  text?: string;
  type: string;
  confidence?: number;
  severity: IssueSeverity;
  message?: string;
}

export interface AuditRecommendation {
  module: 'nlp' | 'computer_vision' | 'representation';
  type: string;
  message: string;
}

export interface AuditImage {
  image_id: string;
  image_url: string;
  alt: string | null;
  people_count: number;
  people_prominence: number;
  image_quality: number;
  brightness: number;
  contrast: number;
  sharpness: number;
  edge_density: number;
  contours: number;
  width: number;
  height: number;
}

export interface AuditSummary {
  nlp_score: number;
  vision_score: number;
  representation_score: number | null;
  total_issues: number;
}

export interface AuditMetadata {
  paragraphs_analyzed: number;
  images_found: number;
  images_analyzed: number;
}

export interface ScoreBreakdownEntry {
  component: 'nlp' | 'vision' | 'representation';
  score: number;
  weight: number;
  contribution: number;
}

export type PresentationCategory =
  | 'feminine_presenting'
  | 'masculine_presenting'
  | 'androgynous_presenting'
  | 'undetermined';

export interface Representation {
  faces_detected: number;
  category_counts: Record<PresentationCategory, number>;
  category_ratios: Record<PresentationCategory, number>;
  diversity_index: number | null;
  balance_index: number | null;
  representation_score: number | null;
  note?: string;
  images_with_faces: number;
  disclaimer: string;
}

export interface BiasStateVector {
  nlp_health: number;
  vision_health: number;
  representation_balance: number;
  people_image_ratio: number;
  diversity: number;
  inclusivity: number;
}

export interface WorldModelAction {
  id: number;
  name: string;
  description: string;
}

export interface WorldModelRollout {
  action: number;
  future_state: number[];
  reward: number;
  terminated: boolean;
  truncated: boolean;
}

export interface WorldModel {
  current_state: BiasStateVector;
  recommended_action: WorldModelAction;
  predicted_future_state: BiasStateVector;
  expected_reward: number;
  improvement: BiasStateVector;
  rollouts: WorldModelRollout[];
}

export interface AuditReport {
  audit_id: string;
  url: string;
  title: string | null;
  inclusivity_score: number;
  score_breakdown: ScoreBreakdownEntry[];
  score_explanation: string[];
  summary: AuditSummary;
  representation: Representation;
  issues: AuditIssue[];
  recommendations: AuditRecommendation[];
  images: AuditImage[];
  metadata: AuditMetadata;
  agent_analysis: string;
  world_model: WorldModel | null;
}
