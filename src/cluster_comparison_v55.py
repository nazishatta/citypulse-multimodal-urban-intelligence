"""CityPulse v5.5: alternative, non-causal profiles for geographic restaurant groups."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

GENERIC_CATEGORIES = {'restaurants', 'restaurant', 'food', 'dining', 'eating places'}
PALETTE = ['#55D0BE', '#F6B86F', '#A99AF8', '#F08DB2', '#7CB9ED', '#DDD08A']
BG = '#191F27'


def normalize_business_schema(grouped: pd.DataFrame) -> pd.DataFrame:
    """Use the actual available business fields; do not fill in missing measurements."""
    d = grouped.copy()
    aliases = {'stars': ('business_stars', 'business_rating', 'snapshot_stars'),
               'review_count': ('business_review_count', 'snapshot_review_count'),
               'categories': ('business_categories',), 'name': ('business_name',)}
    for target, candidates in aliases.items():
        if target not in d:
            for candidate in candidates:
                if candidate in d:
                    d[target] = d[candidate]
                    break
    return d

def _listed_categories(raw):
    if isinstance(raw, str):
        result = [part.strip() for part in raw.split(',')]
    elif isinstance(raw, (list, tuple, set)):
        result = [str(part).strip() for part in raw]
    else:
        result = []
    return [part for part in result if part]

def informative_category(raw):
    listed = _listed_categories(raw)
    return next((part for part in listed if part.lower() not in GENERIC_CATEGORIES),
                'Not recorded' if not listed else 'Other restaurant')

def build_profiles(grouped: pd.DataFrame) -> pd.DataFrame:
    """Aggregate distinct businesses per DBSCAN label; noise is retained separately."""
    cols = ['Group', 'Restaurants', 'Mean snapshot stars', 'Mean snapshot review count', 'Total snapshot reviews', 'Dominant category', 'Example restaurants']
    if grouped.empty:
        return pd.DataFrame(columns=cols)
    data = normalize_business_schema(grouped).drop_duplicates('business_id').copy()
    if 'Group' not in data:
        data['Group'] = data['Spatial cluster'].map(lambda n: 'Unassigned (−1)' if n == -1 else f'Spatial group {n + 1}')
    records = []
    for group, members in data.groupby('Group', sort=True):
        stars = pd.to_numeric(members['stars'], errors='coerce') if 'stars' in members else pd.Series(dtype=float)
        reviews = pd.to_numeric(members['review_count'], errors='coerce') if 'review_count' in members else pd.Series(dtype=float)
        categories = category_counts(members)
        records.append({
            'Group': group,
            'Restaurants': len(members),
            'Mean snapshot stars': round(float(stars.mean()), 2) if stars.notna().any() else float('nan'),
            'Mean snapshot review count': round(float(reviews.mean()), 1) if reviews.notna().any() else float('nan'),
            'Total snapshot reviews': int(reviews.fillna(0).sum()) if len(reviews) else 0,
            'Dominant category': categories.iloc[0]['Category'] if not categories.empty else 'Not recorded',
            'Example restaurants': ', '.join(members['name'].astype(str).head(3)) if 'name' in members else ', '.join(members.business_id.astype(str).head(3)),
        })
    return pd.DataFrame(records, columns=cols).sort_values(['Restaurants', 'Group'], ascending=[False, True]).reset_index(drop=True)


def category_counts(members: pd.DataFrame) -> pd.DataFrame:
    """Count each restaurant once in each of its listed categories; categories may overlap."""
    members = normalize_business_schema(members)
    if 'categories' not in members:
        return pd.DataFrame(columns=['Category', 'Restaurants'])
    counts: dict[str, int] = {}
    for raw in members['categories']:
        cats = [c for c in _listed_categories(raw) if c.lower() not in GENERIC_CATEGORIES]
        for cat in set(cats):
            counts[cat] = counts.get(cat, 0) + 1
    return pd.DataFrame([{'Category': k, 'Restaurants': v} for k, v in counts.items()]).sort_values(['Restaurants', 'Category'], ascending=[False, True]).reset_index(drop=True) if counts else pd.DataFrame(columns=['Category', 'Restaurants'])


def category_composition(grouped: pd.DataFrame, max_categories: int = 6) -> pd.DataFrame:
    """Mutually exclusive *primary-category* composition for 100% stack."""
    grouped = normalize_business_schema(grouped)
    if grouped.empty or 'categories' not in grouped:
        return pd.DataFrame(columns=['Group', 'Category', 'Restaurants', 'Percent'])
    d = grouped.drop_duplicates('business_id').copy()
    if 'Group' not in d:
        d['Group'] = d['Spatial cluster'].map(lambda n: 'Unassigned (−1)' if n == -1 else f'Spatial group {n + 1}')
    d['Category'] = d['categories'].map(informative_category)
    common = set(d['Category'].value_counts().head(max_categories).index)
    d.loc[~d.Category.isin(common), 'Category'] = 'Other'
    out = d.groupby(['Group', 'Category']).size().rename('Restaurants').reset_index()
    total = out.groupby('Group')['Restaurants'].transform('sum')
    out['Percent'] = (100 * out.Restaurants / total).round(2)
    return out


def comparison_figure(profiles: pd.DataFrame, grouped: pd.DataFrame, view: str, active: str | None = None) -> tuple[go.Figure, pd.DataFrame]:
    """Provide one of four complementary analytical encodings with accessible hover labels."""
    p = profiles.copy()
    p = p[~p.Group.str.startswith('Unassigned')]
    if p.empty:
        return go.Figure(), p
    colors = {g: PALETTE[i % len(PALETTE)] for i, g in enumerate(p.Group)}
    focus = active if active in colors else None
    if view == 'Bubble profile':
        usable = p.dropna(subset=['Mean snapshot stars', 'Mean snapshot review count'])
        if usable.empty:
            return go.Figure(), usable
        fig = px.scatter(usable, x='Mean snapshot stars', y='Mean snapshot review count', color='Group',
            size='Restaurants', size_max=66, text='Group', color_discrete_map=colors,
            hover_data={'Restaurants': True, 'Total snapshot reviews': True, 'Dominant category': True, 'Example restaurants': True},
            title='Cluster profiles · ratings, review activity and group size')
        fig.update_traces(textposition='top center', marker={'line': {'width': 1.5, 'color': '#EAF2F5'}})
        for trace in fig.data:
            trace.opacity = 1.0 if focus is None or trace.name == focus else .17
        fig.update_xaxes(range=[1, 5.1], title='Mean business snapshot stars (1–5)')
        fig.update_yaxes(title='Mean business snapshot review count')
    elif view == 'Treemap':
        fig = px.treemap(p, path=['Group'], values='Restaurants', color='Group',
                         color_discrete_map=colors, hover_data=['Dominant category', 'Total snapshot reviews'],
                         title='Share of restaurants by geographic cluster')
    elif view == 'Category mix':
        frame = category_composition(grouped)
        frame = frame[frame.Group.isin(p.Group)]
        if frame.empty:
            return go.Figure(), frame
        fig = px.bar(frame, x='Percent', y='Group', color='Category', orientation='h', barmode='stack',
                     hover_data=['Restaurants'], title='Primary listed category composition by cluster')
        fig.update_xaxes(range=[0, 100], title='Restaurants in group (%)')
        fig.update_yaxes(title='')
        p = frame
        if focus:
            fig.add_shape(type='rect', x0=0, x1=100, y0=focus, y1=focus, line=dict(color='#FFFFFF',width=2))
    else:
        fig = px.bar(p, x='Restaurants', y='Group', orientation='h', color='Group',
                     text='Restaurants', color_discrete_map=colors, title='Exact restaurants per spatial group')
        fig.update_yaxes(categoryorder='total ascending', title='')
        for trace in fig.data:
            trace.opacity = 1.0 if focus is None or trace.name == focus else .2
    if focus:
        fig.add_annotation(text=f'Focused: {focus}', x=.99, y=1.11, xref='paper', yref='paper', xanchor='right', showarrow=False, font=dict(color='#55D0BE',size=13))
    fig.update_layout(paper_bgcolor=BG, plot_bgcolor=BG, font={'color': '#EDF5F8'},
                      hoverlabel={'bgcolor': '#111A23', 'font': {'color': '#FFFFFF'}}, height=430,
                      margin={'l': 20, 'r': 25, 't': 65, 'b': 35})
    return fig, p


def group_takeaway(profiles: pd.DataFrame, active: str | None) -> tuple[str, str, str]:
    """Generate a factual, qualification-aware comparison from the selected group."""
    valid = profiles[~profiles.Group.str.startswith('Unassigned')]
    if valid.empty:
        return ('No detected spatial groups at the selected DBSCAN settings.', 'The current settings do not establish a cluster comparison.', 'Try changing radius or minimum group size; do not force cluster assignments.')
    chosen = valid[valid.Group == active]
    row = chosen.iloc[0] if not chosen.empty else valid.iloc[0]
    s = f"{row['Group']} has {int(row['Restaurants'])} selected restaurants"
    if pd.notna(row['Mean snapshot stars']):
        s += f" and mean business snapshot stars of {row['Mean snapshot stars']:.2f}/5"
    if pd.notna(row['Mean snapshot review count']):
        s += f"; mean recorded review count {row['Mean snapshot review count']:.1f}"
    s += f"; leading category: {row['Dominant category']}."
    why = 'Compare the composition and recorded platform activity of nearby restaurant groups to prioritize follow-up investigation.'
    use = 'Select a group, inspect its named members and categories, and validate local demand with independent market and foot-traffic evidence before making expansion decisions.'
    return s, why, use
