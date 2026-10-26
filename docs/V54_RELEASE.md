# CityPulse v5.4 — Community Galaxy

## Changes
- Default PyVis moving network gains a minimum shared-reviewer cutoff to make dense projections understandable.
- Communities for the filtered *display graph* are recomputed from observed edges; full selected graph metrics remain unchanged and must not be mistaken for filtered counts.
- Computed community-aware initial positions give groups more breathing room; interactive physics remains enabled unless frozen or reduced-motion applies.
- A mild (2px) periodic browser simulation nudge helps avoid a completely frozen view. Hidden tabs and explicitly disabled physics do not receive nudges.
- The clustering tab now presents each modality's practical business interpretation, investigative next steps, and limitations.

## Validation and limitations
- This upgrade does not fabricate additional communities. Depending on review overlap and cutoff, the result can legitimately remain one connected/strongly mixed community.
- The periodic physics nudge is aesthetic; spatial positions are not measurements. Edge counts and hover evidence should drive conclusions.
- System reduced motion and the Freeze control should take precedence. Browser visual testing is essential.
- This is a synthetic demonstration until an authorized, audited real Yelp snapshot is loaded.
- No external resources required for this patch; existing Python/Streamlit/PyVis dependencies are used.
