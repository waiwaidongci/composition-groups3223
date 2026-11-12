-- First schema bootstraps via metadata. Optional upgrade indexes:
CREATE INDEX sample_study_group_idx ON composition_samples (study_id,`group`);
CREATE INDEX note_run_status_idx ON resample_notes (run_id,status);
