"""Clustering Lab: distinct spatial, shared-reviewer and document groupings."""
from __future__ import annotations
import pandas as pd
from src.analysis import spatial_clusters, restaurant_graph, graph_details


def geographic_summary(businesses: pd.DataFrame, radius_m: int, min_samples: int):
    """Return original-ID-preserving DBSCAN labels and per-group counts."""
    grouped=spatial_clusters(businesses, radius_m, min_samples)
    counts=(grouped.groupby('Spatial cluster').size().reset_index(name='Restaurants')
            .sort_values(['Restaurants','Spatial cluster'],ascending=[False,True]))
    return grouped, counts


def shared_audience_summary(reviews: pd.DataFrame, min_shared: int, max_per_reviewer: int):
    """Community membership for actual weighted shared-reviewer projection."""
    g, provenance=restaurant_graph(reviews[['user_id','business_id']],min_shared,max_per_reviewer)
    if not g.number_of_edges():
        return g, pd.DataFrame(columns=['business_id','Community','Connections','Shared-reviewer strength']), provenance
    ranking, details=graph_details(g)
    provenance={**provenance,'communities':details['communities']}
    return g,ranking,provenance


def text_group_summary(reviews: pd.DataFrame, assignments: pd.DataFrame | None, labels: pd.DataFrame | None):
    """Fixed NMF dominant-topic groups; explicitly not unsupervised cluster ground truth."""
    if assignments is None or labels is None:
        return pd.DataFrame(columns=['topic','Reviews','Label']),0
    eligible=reviews[['review_id']].merge(assignments[['review_id','topic']],on='review_id',how='inner',validate='one_to_one')
    summary=(eligible.groupby('topic').size().reset_index(name='Reviews')
             .merge(labels[['topic','Label']],on='topic',how='left',validate='many_to_one')
             .sort_values('Reviews',ascending=False))
    return summary,len(eligible)
