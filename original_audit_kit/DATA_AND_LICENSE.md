# Dataset provenance, keys and practical caveats

## Verified directory references
- Official Yelp entry: https://business.yelp.com/data/resources/open-dataset/
- Yelp download: https://www.yelp.com/dataset/download
- Yelp's Kaggle listing: https://www.kaggle.com/yelp-dataset/yelp-dataset/data
- NetworkX projected graph docs: https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.bipartite.projection.weighted_projected_graph.html

The public Kaggle listing identifies **five JSON files and a user agreement**: business, review, user, tip, checkin. The separate Yelp photo assets must be sourced, validated and permitted independently; a third-party replica is not permission to republish.

## Common JSONL keys (verify your own archive)
- Business: `business_id`, `city`, `state`, `categories`, `latitude`, `longitude`, `stars`, `review_count`, `name`.
- Review: `review_id`, `business_id`, `user_id`, `date`, `stars`, `text`.
- User: `user_id`, `friends`, `review_count`; users are NOT needed for reviewer-business connections because reviews contain both IDs.
- Tip: `business_id`, `user_id`, `text`, `date`.
- Checkin: `business_id`, `date` (often comma-separated timestamps).
- Separate photo metadata: `photo_id`, `business_id`, `caption`, `label` and photo file bytes (`photo_id.jpg`) when available.

## Join correctness
`review.business_id → business.business_id`; `review.user_id → user.user_id` if user table needed; `photo.business_id → business.business_id`. A photo links to a **business**, not a specific review.

## Governance
Record official user agreement review, allowed scope, source download date, file checksum, applicable redistribution/display limitations, and public-dashboard compliance approval. Avoid displaying identifiable reviewer profiles; publish aggregates or explicitly permitted samples. Never treat the blanket label “open dataset” as permission to redistribute content or images.
