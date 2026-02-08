# ChapterAuthorAgent Skill

**Skill Name**: `chapter-author`
**Single Responsibility**: Generate a complete, spec-compliant MDX chapter for the Physical AI textbook.

## Input

```yaml
chapter_title: string     # Full chapter title
module: string            # ros2 | simulation | isaac | vla | foundations | capstone
difficulty: string        # beginner | intermediate | advanced
hardware_tiers: string[]  # Required: [RTX-LOCAL, CLOUD] or [CPU-ONLY, CLOUD] etc.
order: number             # Chapter order (1-6)
key_topics: string[]      # 3-5 main concepts to cover
```

## Output

A complete MDX file following the chapter template:
- Valid frontmatter with all required fields
- 6 mandatory sections: Overview, Learning Outcomes (3 with Bloom's verbs),
  Concepts (3+ subsections), Lab (with hardware badges), Exercises (3), Summary
- Hardware-tagged lab blocks for every tier in `hardware_tiers`
- Cross-references to adjacent chapters where relevant

## Usage

```bash
# In Claude Code
/chapter-author --title "Sensor Fusion Deep Dive" --module ros2 --difficulty advanced --hardware RTX-LOCAL,CLOUD --order 7
```

## Constraints (from Constitution v1.0.0)

- HARD CONSTRAINT: Total chapters MUST remain exactly 6
- Every lab MUST have a [CLOUD] alternative path
- Bloom's taxonomy verbs required in Learning Outcomes
- No hallucinated technical content — all ROS 2 / Isaac / Gazebo details must be verified
