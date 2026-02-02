## NVR Pattern Schema (Canonical)

Each pattern must define:

- question_type
- base_shapes
- transformations (ordered)
- distractor_rules
- difficulty

Example:

{
  "pattern_id": "NVR_ROT_001",
  "question_type": "ANALOGY",
  "base_shapes": ["triangle"],
  "transformations": [
    {"type": "rotation", "value": 90}
  ],
  "distractor_rules": [
    "wrong_rotation",
    "no_rotation"
  ],
  "difficulty": "medium"
}
