"""
Export HeteroData graph to JSON format for D3.js visualization
This script extracts the graph data and prepares it for web visualization
"""

import torch
import json
import pandas as pd
import numpy as np
from pathlib import Path

def export_hetero_graph_to_json(
    hg, 
    airport_to_idx, 
    lineage_to_idx,
    idx_to_airport=None,
    idx_to_lineage=None,
    flights_df=None,
    metadata_df=None,
    output_file='graph_data.json',
    sample_size=None
):
    """
    Export HeteroData graph to JSON format for D3.js visualization
    
    Parameters:
    -----------
    hg : HeteroData
        The heterogeneous graph object
    airport_to_idx : dict
        Mapping from airport code to index
    lineage_to_idx : dict
        Mapping from lineage name to index
    idx_to_airport : dict (optional)
        Reverse mapping from index to airport code
    idx_to_lineage : dict (optional)
        Reverse mapping from index to lineage name
    flights_df : DataFrame (optional)
        Flight data with airport coordinates
    metadata_df : DataFrame (optional)
        Genome metadata
    output_file : str
        Output JSON filename
    sample_size : dict (optional)
        Dictionary with keys 'airports', 'lineages', 'edges' to sample data
        Example: {'airports': 500, 'lineages': 500, 'edges': 5000}
    """
    
    # Create reverse mappings if not provided
    if idx_to_airport is None:
        idx_to_airport = {v: k for k, v in airport_to_idx.items()}
    if idx_to_lineage is None:
        idx_to_lineage = {v: k for k, v in lineage_to_idx.items()}
    
    print("Exporting graph data...")
    
    # ========== NODES ==========
    print("Processing airport nodes...")
    airports = []
    airport_coords = {}
    
    # Try to get airport coordinates from flights_df
    if flights_df is not None:
        # Assuming flights_df has columns like 'Country', 'City'
        for _, row in flights_df.drop_duplicates('origin').iterrows():
            if row['origin'] in airport_to_idx:
                airport_coords[row['origin']] = {
                    'lat': row.get('Latitude', 0),
                    'lon': row.get('Longitude', 0),
                    'city': row.get('City', 'Unknown City'),      # Added Metadata
                    'country': row.get('Country', 'Unknown Country'), # Added Metadata
                    'region': row.get('Region', '')               # Added Metadata (if exists)
                }
        
        for _, row in flights_df.drop_duplicates('destination').iterrows():
            if row['destination'] in airport_to_idx:
                if row['destination'] not in airport_coords:
                    airport_coords[row['destination']] = {
                        'lat': row.get('Latitude_destination', 0),
                        'lon': row.get('Longitude_destination', 0),
                        'city': row.get('City_destination', ''),
                        'country': row.get('Country_destination', '')
                    }
    
    # Sample airports if requested
    airport_indices = list(range(len(airport_to_idx)))
    if sample_size and 'airports' in sample_size:
        airport_indices = np.random.choice(
            airport_indices, 
            min(sample_size['airports'], len(airport_indices)), 
            replace=False
        )
        airport_indices = set(airport_indices)
    else:
        airport_indices = set(airport_indices)
    
    for idx in sorted(airport_indices):
        airport_code = idx_to_airport[idx]
        coords = airport_coords.get(airport_code, {})
        
        airports.append({
            'id': f'airport_{idx}',
            'index': idx,
            'code': airport_code,
            'type': 'airport',
            'lat': float(coords.get('lat', 0)),
            'lon': float(coords.get('lon', 0)),
            'city': coords.get('city', ''),       # Export it
            'country': coords.get('country', '')  # Export it
        })
    
    print(f"Exported {len(airports)} airport nodes")
    
    # Process lineage nodes
    print("Processing lineage nodes...")
    lineages = []
    
    # Sample lineages if requested
    lineage_indices = list(range(len(lineage_to_idx)))
    if sample_size and 'lineages' in sample_size:
        lineage_indices = np.random.choice(
            lineage_indices, 
            min(sample_size['lineages'], len(lineage_indices)), 
            replace=False
        )
        lineage_indices = set(lineage_indices)
    else:
        lineage_indices = set(lineage_indices)
    
    for idx in sorted(lineage_indices):
        lineage_name = idx_to_lineage[idx]
        lineages.append({
            'id': f'lineage_{idx}',
            'index': idx,
            'name': lineage_name,
            'type': 'lineage'
        })
    
    print(f"Exported {len(lineages)} lineage nodes")
    
    # ========== EDGES ==========
    edges = []
    
    # Helper function to sample edges
    def sample_edges(edge_index, edge_type, max_edges=None):
        num_edges = edge_index.shape[1]
        if max_edges and num_edges > max_edges:
            indices = np.random.choice(num_edges, max_edges, replace=False)
            return edge_index[:, indices]
        return edge_index
    
    max_edges_per_type = sample_size.get('edges', None) if sample_size else None
    
    # 1. Airport -> Airport (flights)
    print("Processing flight edges...")
    if ('airport', 'flight', 'airport') in hg.edge_types:
        edge_index = hg['airport', 'flight', 'airport'].edge_index
        edge_attr = hg['airport', 'flight', 'airport'].edge_attr
        
        # Sample edges
        edge_index_sampled = sample_edges(edge_index, 'flight', max_edges_per_type)
        
        for i in range(edge_index_sampled.shape[1]):
            src = int(edge_index_sampled[0, i].item())
            dst = int(edge_index_sampled[1, i].item())
            
            # Only include if nodes are in our sample
            if src in airport_indices and dst in airport_indices:
                edges.append({
                    'source': f'airport_{src}',
                    'target': f'airport_{dst}',
                    'type': 'flight',
                    'weight': float(edge_attr[i, 0].item()) if edge_attr is not None else 1.0
                })
    
    print(f"Added {sum(1 for e in edges if e['type'] == 'flight')} flight edges")
    
    # 2. Lineage -> Airport (sampled_at)
    print("Processing sampling edges...")
    if ('lineage', 'sampled_at', 'airport') in hg.edge_types:
        edge_index = hg['lineage', 'sampled_at', 'airport'].edge_index
        edge_attr = hg['lineage', 'sampled_at', 'airport'].edge_attr
        
        edge_index_sampled = sample_edges(edge_index, 'sampled_at', max_edges_per_type)
        
        for i in range(edge_index_sampled.shape[1]):
            src = int(edge_index_sampled[0, i].item())
            dst = int(edge_index_sampled[1, i].item())
            
            if src in lineage_indices and dst in airport_indices:
                time_info = edge_attr[i].tolist() if edge_attr is not None else [0, 0]
                edges.append({
                    'source': f'lineage_{src}',
                    'target': f'airport_{dst}',
                    'type': 'sampled_at',
                    'weight': float(time_info[0]) if len(time_info) > 0 else 1.0,
                    'week': int(time_info[1]) if len(time_info) > 1 else 0
                })
    
    print(f"Added {sum(1 for e in edges if e['type'] == 'sampled_at')} sampling edges")
    
    # 3. Lineage -> Lineage (evolves_from)
    print("Processing evolution edges...")
    if ('lineage', 'evolves_from', 'lineage') in hg.edge_types:
        edge_index = hg['lineage', 'evolves_from', 'lineage'].edge_index
        edge_attr = hg['lineage', 'evolves_from', 'lineage'].edge_attr
        
        edge_index_sampled = sample_edges(edge_index, 'evolves_from', max_edges_per_type)
        
        for i in range(edge_index_sampled.shape[1]):
            src = int(edge_index_sampled[0, i].item())
            dst = int(edge_index_sampled[1, i].item())
            
            if src in lineage_indices and dst in lineage_indices:
                edges.append({
                    'source': f'lineage_{src}',
                    'target': f'lineage_{dst}',
                    'type': 'evolves_from',
                    'weight': float(edge_attr[i, 0].item()) if edge_attr is not None else 1.0
                })
    
    print(f"Added {sum(1 for e in edges if e['type'] == 'evolves_from')} evolution edges")
    
    # 4. Lineage -> Lineage (temporal)
    print("Processing temporal edges...")
    if ('lineage', 'temporal', 'lineage') in hg.edge_types:
        edge_index = hg['lineage', 'temporal', 'lineage'].edge_index
        edge_attr = hg['lineage', 'temporal', 'lineage'].edge_attr
        
        edge_index_sampled = sample_edges(edge_index, 'temporal', max_edges_per_type)
        
        for i in range(edge_index_sampled.shape[1]):
            src = int(edge_index_sampled[0, i].item())
            dst = int(edge_index_sampled[1, i].item())
            
            if src in lineage_indices and dst in lineage_indices:
                time_info = edge_attr[i].tolist() if edge_attr is not None else [0, 0, 0]
                edges.append({
                    'source': f'lineage_{src}',
                    'target': f'lineage_{dst}',
                    'type': 'temporal',
                    'weight': float(time_info[2]) if len(time_info) > 2 else 1.0,
                    'time_start': int(time_info[0]) if len(time_info) > 0 else 0,
                    'time_end': int(time_info[1]) if len(time_info) > 1 else 0
                })
    
    print(f"Added {sum(1 for e in edges if e['type'] == 'temporal')} temporal edges")
    
    # ========== CREATE OUTPUT ==========
    output_data = {
        'nodes': airports + lineages,
        'links': edges,
        'metadata': {
            'num_airports': len(airports),
            'num_lineages': len(lineages),
            'num_edges': len(edges),
            'edge_types': list(set(e['type'] for e in edges)),
            'sampled': sample_size is not None
        }
    }
    
    # Save to JSON
    output_path = Path(output_file)
    print(f"\nSaving to {output_path}...")
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"✓ Successfully exported graph data!")
    print(f"  - {len(airports)} airports")
    print(f"  - {len(lineages)} lineages")
    print(f"  - {len(edges)} edges")
    print(f"  - File size: {output_path.stat().st_size / 1024:.1f} KB")
    
    return output_data


# Example usage (add this to your notebook):
"""
# After creating the HeteroData object, export it:

# Create reverse mappings
idx_to_airport = {v: k for k, v in airport_to_idx.items()}
idx_to_lineage = {v: k for k, v in lineage_to_idx.items()}

# Export with sampling for better performance (recommended for large graphs)
export_hetero_graph_to_json(
    hg=hg,
    airport_to_idx=airport_to_idx,
    lineage_to_idx=lineage_to_idx,
    idx_to_airport=idx_to_airport,
    idx_to_lineage=idx_to_lineage,
    flights_df=flights_with_airport_info_df,
    metadata_df=metadata_df,
    output_file='visualization/graph_data.json',
    sample_size={'airports': 1000, 'lineages': 500, 'edges': 10000}  # Adjust as needed
)

# Or export full graph (might be large):
# export_hetero_graph_to_json(
#     hg=hg,
#     airport_to_idx=airport_to_idx,
#     lineage_to_idx=lineage_to_idx,
#     idx_to_airport=idx_to_airport,
#     idx_to_lineage=idx_to_lineage,
#     flights_df=flights_with_airport_info_df,
#     output_file='visualization/graph_data_full.json'
# )
"""

