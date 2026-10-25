"""Descriptive, denominator-aware insights. No causal or business-success claims."""
from __future__ import annotations
import pandas as pd

def trend_story(months: pd.DataFrame) -> dict:
    if months.empty:return {'headline':'No dated review activity','evidence':'No eligible dated reviews under current filters.','decision':'Broaden the date range or filters to examine review activity.','caution':'Review dates are posting dates, not visits.'}
    counts=months.copy(); counts['Reviews']=pd.to_numeric(counts['Reviews'],errors='coerce').fillna(0)
    peak=counts.loc[counts.Reviews.idxmax()]
    positive=counts[counts.Reviews>0]
    low=positive.loc[positive.Reviews.idxmin()] if len(positive) else peak
    return {'headline':f'Highest recorded month: {peak.Month}',
            'evidence':f'{int(peak.Reviews)} posted reviews in {peak.Month}; smallest nonzero observed month: {low.Month} ({int(low.Reviews)}). {len(counts)} calendar months displayed.',
            'decision':'A manager could inspect the original reviews from higher- and lower-activity periods to investigate service or marketing changes.',
            'caution':'These are platform review postings, not footfall or market demand. Partial months and coverage biases matter.'}

def review_story(freq: pd.DataFrame, eligible: int, measure: str) -> dict:
    if freq.empty:return {'headline':'No terms in this selection','evidence':'No eligible review terms.','decision':'Broaden the population or inspect raw review quality.','caution':'No text evidence available.'}
    top=freq.sort_values('Value',ascending=False).iloc[0]
    distinct=int(freq.Value.nunique())
    return {'headline':f'Most frequent displayed expression: {top.Term}',
            'evidence':f'{int(top.Value)} {"reviews contain it" if measure=="documents" else "occurrences"} across {eligible} selected reviews. {distinct} different frequency levels among displayed terms.',
            'decision':'Select a theme to inspect its original supporting reviews; compare businesses before making operational decisions.',
            'caution':'Word frequency is not sentiment, importance, service quality, or a validated customer need.'}

def cluster_story(groups: pd.DataFrame, n_noise: int, radius: int, min_n: int) -> dict:
    non=groups[groups['Spatial cluster']!=-1] if len(groups) else groups
    largest=non.sort_values('Restaurants',ascending=False).iloc[0] if len(non) else None
    return {'headline':f'{len(non)} geographic groups detected',
            'evidence':(f'Largest spatial group contains {int(largest.Restaurants)} restaurants; ' if largest is not None else 'No qualifying group at these settings; ')+f'{n_noise} mapped restaurants remain unassigned. Radius {radius} m; minimum {min_n} locations.',
            'decision':'Compare the locations and review evidence for each group; experiment with radius to understand the sensitivity of the result.',
            'caution':'Spatial density does not demonstrate demand, opportunity, ratings, or shared customers. DBSCAN group numbers are arbitrary.'}

def term_by_restaurant(reviews: pd.DataFrame, businesses: pd.DataFrame, terms: list[str], max_businesses: int = 8) -> pd.DataFrame:
    """Percent of selected eligible reviews containing each exact expression; no sentiment inference."""
    import re
    if reviews.empty or not terms:
        return pd.DataFrame(columns=['Restaurant', 'Term', 'Percent', 'Reviews'])
    chosen=reviews.groupby('business_id').size().sort_values(ascending=False).head(max_businesses).index
    names=businesses.set_index('business_id')['name'].to_dict()
    results=[]
    for bid in chosen:
        group=reviews.loc[reviews.business_id==bid,'text'].fillna('').astype(str)
        for term in terms:
            pattern=r'(?<!\w)'+re.escape(str(term))+r'(?!\w)'
            hits=int(group.str.contains(pattern,case=False,regex=True).sum())
            results.append({'Restaurant':names.get(bid,str(bid)),'Term':str(term),'Percent':100*hits/len(group), 'Reviews':len(group)})
    return pd.DataFrame(results)
