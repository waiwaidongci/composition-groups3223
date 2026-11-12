-- First schema bootstraps via metadata. Optional upgrade indexes:
CREATE INDEX sample_study_group_idx ON composition_samples (study_id,`group`);
CREATE INDEX note_run_status_idx ON resample_notes (run_id,status);
CREATE INDEX comparison_study_status_idx ON sensitivity_comparisons (study_id,status);
CREATE INDEX comparison_retry_idx ON sensitivity_comparisons (retry_of);
