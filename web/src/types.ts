export type Segment = { start: number; end: number; text: string; score: number; page: number | null };
export type ScanResult = {
  label: "benign" | "suspicious"; score: number; threshold: number; model_version: string;
  chunks_scanned: number; truncated: boolean; signals: string[]; segments: Segment[];
  source: { kind: string; name: string | null; chars: number };
};
