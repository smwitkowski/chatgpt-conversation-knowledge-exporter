export interface TopicSummary {
  topic_id: number;
  name: string;
  description: string;
  keywords: string[];
  conversation_count: number;
  atom_count: number;
  flagged_count: number;
}

export interface TopicDetail extends TopicSummary {
  representative_conversations: string[];
  conversations: ConversationSummary[];
}

export interface ConversationSummary {
  conversation_id: string;
  title: string;
  project_id?: string;
  project_name?: string;
  atom_count: number;
  review_flag: boolean;
  topics: TopicAssignment[];
}

export interface TopicAssignment {
  topic_id: number;
  name: string;
  score: number;
  rank: 'primary' | 'secondary';
}

export interface ConversationDetail extends ConversationSummary {
  facts: Atom[];
  decisions: DecisionAtom[];
  questions: OpenQuestion[];
  docs: DocInfo[];
}

export interface Atom {
  type: string;
  topic: string;
  statement: string;
  status: 'active' | 'deprecated' | 'uncertain';
  evidence: Evidence[];
  extracted_at: string;
}

export interface DecisionAtom extends Atom {
  type: 'decision';
  alternatives: string[];
  rationale?: string;
  consequences?: string;
}

export interface OpenQuestion {
  question: string;
  topic: string;
  context?: string;
  evidence: Evidence[];
  extracted_at: string;
}

export interface Evidence {
  message_id?: string;
  time_iso?: string;
  text_snippet?: string;
}

export interface DocInfo {
  name: string;
  path: string;
}

export interface ReviewQueueItem {
  conversation_id: string;
  title: string;
  project_id?: string;
  project_name?: string;
  primary_topic: string;
  primary_score: number;
  reason: 'low_confidence' | 'ambiguous';
}
