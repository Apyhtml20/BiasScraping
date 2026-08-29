export type IssueSeverity = 'high' | 'medium' | 'low';

export interface AuditIssue {
  module: 'nlp' | 'computer_vision';
  paragraph_id?: string;
  text?: string;
  type: string;
  confidence?: number;
  severity: IssueSeverity;
  message?: string;
}

export interface AuditRecommendation {
  module: 'nlp' | 'computer_vision';
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
  total_issues: number;
}

export interface AuditMetadata {
  paragraphs_analyzed: number;
  images_found: number;
  images_analyzed: number;
}

export interface AuditReport {
  audit_id: string;
  url: string;
  title: string | null;
  inclusivity_score: number;
  summary: AuditSummary;
  issues: AuditIssue[];
  recommendations: AuditRecommendation[];
  images: AuditImage[];
  metadata: AuditMetadata;
  agent_analysis: string;
}
