import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# Set style
plt.style.use('seaborn-v0_8-paper')
colors = {
    'data': '#E8F4F8',
    'process': '#B8E6F0',
    'model': '#FFE5B4',
    'output': '#D4F1D4',
    'node': '#FFB6C1',
    'edge': '#DDA0DD'
}

# ============================================
# DIAGRAM 1: Overall System Architecture
# ============================================
def create_system_architecture():
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(5, 9.5, 'COVID-19 Viral Spread Prediction System Architecture', 
            ha='center', fontsize=16, fontweight='bold')
    
    # Layer 1: Data Sources
    boxes = [
        {'xy': (0.5, 7.5), 'width': 2, 'height': 1, 'label': 'GISAID\nGenome\nMetadata\n(9.3M samples)', 'color': colors['data']},
        {'xy': (3, 7.5), 'width': 2, 'height': 1, 'label': 'Flight Data\n(OpenSky)\n4.5M flights', 'color': colors['data']},
        {'xy': (5.5, 7.5), 'width': 2, 'height': 1, 'label': 'Phylogenetic\nTree\n(.nwk)', 'color': colors['data']},
        {'xy': (8, 7.5), 'width': 1.5, 'height': 1, 'label': 'Airport\nCoordinates', 'color': colors['data']},
    ]
    
    for box in boxes:
        rect = FancyBboxPatch(box['xy'], box['width'], box['height'], 
                              boxstyle="round,pad=0.05", 
                              edgecolor='black', facecolor=box['color'], linewidth=2)
        ax.add_patch(rect)
        ax.text(box['xy'][0] + box['width']/2, box['xy'][1] + box['height']/2, 
                box['label'], ha='center', va='center', fontsize=9, fontweight='bold')
    
    # Layer 2: Data Processing
    ax.text(5, 6.8, 'Data Processing & Integration', ha='center', fontsize=12, 
            fontweight='bold', style='italic', color='#555')
    
    boxes2 = [
        {'xy': (0.5, 5.5), 'width': 2.5, 'height': 0.8, 'label': 'Temporal Filtering\n(Jan-Apr 2020)', 'color': colors['process']},
        {'xy': (3.5, 5.5), 'width': 2.5, 'height': 0.8, 'label': 'Spatial Mapping\n(KD-Tree)', 'color': colors['process']},
        {'xy': (6.5, 5.5), 'width': 2.5, 'height': 0.8, 'label': 'Lineage Extraction\n(Pango)', 'color': colors['process']},
    ]
    
    for box in boxes2:
        rect = FancyBboxPatch(box['xy'], box['width'], box['height'], 
                              boxstyle="round,pad=0.05", 
                              edgecolor='black', facecolor=box['color'], linewidth=2)
        ax.add_patch(rect)
        ax.text(box['xy'][0] + box['width']/2, box['xy'][1] + box['height']/2, 
                box['label'], ha='center', va='center', fontsize=9)
    
    # Layer 3: Graph Construction
    ax.text(5, 4.8, 'Heterogeneous Graph Construction', ha='center', fontsize=12, 
            fontweight='bold', style='italic', color='#555')
    
    graph_box = FancyBboxPatch((1, 3.2), 7.5, 1.3, boxstyle="round,pad=0.1", 
                               edgecolor='black', facecolor='#FFF8DC', linewidth=3)
    ax.add_patch(graph_box)
    
    ax.text(4.75, 4.2, 'Nodes: 12,900 Airports + 255 Lineages', ha='center', fontsize=10, fontweight='bold')
    ax.text(4.75, 3.85, 'Edges: Flight (1M) | Sampled_at (5.8K) | Evolves_from (54) | Temporal (3.4K)', 
            ha='center', fontsize=9)
    ax.text(4.75, 3.5, 'Features: One-hot encoding + Temporal attributes', ha='center', fontsize=9)
    
    # Layer 4: Model
    ax.text(5, 2.6, 'HGT Model Training', ha='center', fontsize=12, 
            fontweight='bold', style='italic', color='#555')
    
    model_box = FancyBboxPatch((2, 1.2), 5.5, 1.2, boxstyle="round,pad=0.1", 
                               edgecolor='black', facecolor=colors['model'], linewidth=3)
    ax.add_patch(model_box)
    
    ax.text(4.75, 2.1, 'Heterogeneous Graph Transformer (HGT)', ha='center', fontsize=11, fontweight='bold')
    ax.text(4.75, 1.75, '2 Layers | 2 Attention Heads | Hidden Dim: 32', ha='center', fontsize=9)
    ax.text(4.75, 1.45, 'Link Prediction: Lineage → Airport (Binary Cross-Entropy)', ha='center', fontsize=9)
    
    # Layer 5: Output
    boxes3 = [
        {'xy': (1.5, 0.1), 'width': 2.5, 'height': 0.8, 'label': 'Risk Scores\nper Airport', 'color': colors['output']},
        {'xy': (4.5, 0.1), 'width': 2.5, 'height': 0.8, 'label': 'Lineage Spread\nPrediction', 'color': colors['output']},
        {'xy': (7.5, 0.1), 'width': 1.5, 'height': 0.8, 'label': 'Evaluation\nMetrics', 'color': colors['output']},
    ]
    
    for box in boxes3:
        rect = FancyBboxPatch(box['xy'], box['width'], box['height'], 
                              boxstyle="round,pad=0.05", 
                              edgecolor='black', facecolor=box['color'], linewidth=2)
        ax.add_patch(rect)
        ax.text(box['xy'][0] + box['width']/2, box['xy'][1] + box['height']/2, 
                box['label'], ha='center', va='center', fontsize=9, fontweight='bold')
    
    # Add arrows
    arrow_props = dict(arrowstyle='->', lw=2, color='#333')
    
    # Data to Processing
    for x in [1.5, 4, 6.5, 8.75]:
        ax.annotate('', xy=(x, 6.3), xytext=(x, 7.5), arrowprops=arrow_props)
    
    # Processing to Graph
    ax.annotate('', xy=(4.75, 4.5), xytext=(4.75, 5.5), arrowprops=arrow_props)
    
    # Graph to Model
    ax.annotate('', xy=(4.75, 2.4), xytext=(4.75, 3.2), arrowprops=arrow_props)
    
    # Model to Output
    for x in [2.75, 5.75, 8.25]:
        ax.annotate('', xy=(x, 0.9), xytext=(x, 1.2), arrowprops=arrow_props)
    
    plt.tight_layout()
    plt.savefig('1_system_architecture.png', dpi=300, bbox_inches='tight', facecolor='white')
    print("✓ Created: 1_system_architecture.png")
    plt.close()

# ============================================
# DIAGRAM 2: Data Processing Pipeline
# ============================================
def create_data_pipeline():
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    ax.text(5, 11.5, 'Data Processing Pipeline', ha='center', fontsize=16, fontweight='bold')
    
    y_pos = 10.5
    steps = [
        {
            'title': '1. Load Raw Data',
            'items': ['• GISAID Metadata: 9.3M genome samples', 
                     '• Flight Data: 4.5M flights (Jan-Apr 2020)',
                     '• Phylogenetic Tree: Newick format',
                     '• Airport Coordinates: 12,900 airports'],
            'color': colors['data']
        },
        {
            'title': '2. Temporal Filtering',
            'items': ['• Filter genomes: 2020-01-01 to 2020-04-30',
                     '• Result: 65,215 samples → 64,504 (after removing unclassifiable)',
                     '• Extract Pango lineages',
                     '• Parse dates and create weekly periods'],
            'color': colors['process']
        },
        {
            'title': '3. Spatial Mapping (KD-Tree)',
            'items': ['• Build KD-Tree from airport coordinates',
                     '• Map each genome location to nearest airport',
                     '• Distance threshold: < 500 km',
                     '• Result: 402 unique locations mapped'],
            'color': colors['process']
        },
        {
            'title': '4. Edge Construction',
            'items': ['• Flight edges: Origin → Destination (weekly aggregation)',
                     '• Sample edges: Lineage → Airport (weekly counts)',
                     '• Phylogenetic edges: Parent lineage → Child lineage',
                     '• Temporal edges: Same lineage across consecutive weeks'],
            'color': colors['process']
        },
        {
            'title': '5. Graph Aggregation',
            'items': ['• Weekly aggregation: Reduce temporal granularity',
                     '• Filter rare lineages: ≥10 samples globally',
                     '• Result: 255 lineages, 12,900 airports, 18 weeks',
                     '• Create node indices and mappings'],
            'color': colors['process']
        },
        {
            'title': '6. Train/Test Split',
            'items': ['• Temporal split: First 14 weeks (training)',
                     '• Last 4 weeks (testing)',
                     '• Prevent data leakage: Filter future edges',
                     '• Result: 3,657 train edges, 2,205 test edges'],
            'color': colors['output']
        },
    ]
    
    for step in steps:
        # Box
        rect = FancyBboxPatch((0.5, y_pos-1.3), 9, 1.2, boxstyle="round,pad=0.1", 
                              edgecolor='black', facecolor=step['color'], linewidth=2)
        ax.add_patch(rect)
        
        # Title
        ax.text(1, y_pos-0.3, step['title'], fontsize=11, fontweight='bold')
        
        # Items
        for i, item in enumerate(step['items']):
            ax.text(1.2, y_pos-0.6-i*0.25, item, fontsize=8)
        
        # Arrow to next
        if y_pos > 2:
            arrow = FancyArrowPatch((5, y_pos-1.35), (5, y_pos-1.55), 
                                   arrowstyle='->', mutation_scale=20, lw=2, color='#333')
            ax.add_patch(arrow)
        
        y_pos -= 1.8
    
    plt.tight_layout()
    plt.savefig('2_data_pipeline.png', dpi=300, bbox_inches='tight', facecolor='white')
    print("✓ Created: 2_data_pipeline.png")
    plt.close()

# ============================================
# DIAGRAM 3: Heterogeneous Graph Structure
# ============================================
def create_graph_structure():
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    ax.text(7, 9.5, 'Heterogeneous Graph Structure', ha='center', fontsize=16, fontweight='bold')
    
    # Node Types
    ax.text(7, 8.8, 'Node Types', ha='center', fontsize=13, fontweight='bold', style='italic')
    
    # Airport Node
    circle1 = plt.Circle((3, 7.5), 0.8, color=colors['node'], ec='black', linewidth=3)
    ax.add_patch(circle1)
    ax.text(3, 7.5, 'Airport', ha='center', va='center', fontsize=11, fontweight='bold')
    ax.text(3, 6.3, 'Count: 12,900\nFeatures: One-hot (12,900-dim)\nAttributes: Lat, Lon, City, Country', 
            ha='center', fontsize=9, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Lineage Node
    circle2 = plt.Circle((11, 7.5), 0.8, color=colors['node'], ec='black', linewidth=3)
    ax.add_patch(circle2)
    ax.text(11, 7.5, 'Lineage', ha='center', va='center', fontsize=11, fontweight='bold')
    ax.text(11, 6.3, 'Count: 255\nFeatures: One-hot (255-dim)\nAttributes: Pango lineage name', 
            ha='center', fontsize=9, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Edge Types
    ax.text(7, 5.3, 'Edge Types', ha='center', fontsize=13, fontweight='bold', style='italic')
    
    edge_types = [
        {
            'name': 'Flight',
            'src': 'Airport',
            'dst': 'Airport',
            'count': '1,070,596',
            'attrs': 'Weight: flight_count\nTime: week_index',
            'y': 4.2,
            'color': '#87CEEB'
        },
        {
            'name': 'Sampled_at',
            'src': 'Lineage',
            'dst': 'Airport',
            'count': '5,862',
            'attrs': 'Weight: sample_count\nTime: week_index',
            'y': 2.8,
            'color': '#98FB98'
        },
        {
            'name': 'Evolves_from',
            'src': 'Lineage',
            'dst': 'Lineage',
            'count': '54',
            'attrs': 'Weight: genetic_distance\n(from phylogenetic tree)',
            'y': 1.4,
            'color': '#FFB6C1'
        },
        {
            'name': 'Temporal',
            'src': 'Lineage',
            'dst': 'Lineage',
            'count': '3,434',
            'attrs': 'Source_week, Target_week\nGrowth_rate: log(count_t+1) - log(count_t)',
            'y': 0,
            'color': '#DDA0DD'
        },
    ]
    
    for edge in edge_types:
        # Edge box
        rect = FancyBboxPatch((1, edge['y']), 12, 1, boxstyle="round,pad=0.05", 
                              edgecolor='black', facecolor=edge['color'], linewidth=2, alpha=0.6)
        ax.add_patch(rect)
        
        # Edge info
        ax.text(2, edge['y']+0.7, f"{edge['name']}", fontsize=11, fontweight='bold')
        ax.text(2, edge['y']+0.4, f"{edge['src']} → {edge['dst']}", fontsize=9, style='italic')
        ax.text(6, edge['y']+0.5, f"Count: {edge['count']}", fontsize=9)
        ax.text(9.5, edge['y']+0.5, edge['attrs'], fontsize=8)
    
    plt.tight_layout()
    plt.savefig('3_graph_structure.png', dpi=300, bbox_inches='tight', facecolor='white')
    print("✓ Created: 3_graph_structure.png")
    plt.close()

# ============================================
# DIAGRAM 4: HGT Model Architecture
# ============================================
def create_model_architecture():
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 11)
    ax.axis('off')
    
    ax.text(6, 10.5, 'Heterogeneous Graph Transformer (HGT) Architecture', 
            ha='center', fontsize=16, fontweight='bold')
    
    # Input Layer
    ax.text(6, 9.7, 'Input Layer', ha='center', fontsize=12, fontweight='bold', style='italic')
    
    input_boxes = [
        {'xy': (1, 8.5), 'width': 2, 'height': 0.8, 'label': 'Airport\nFeatures\n[12900, 12900]'},
        {'xy': (4, 8.5), 'width': 2, 'height': 0.8, 'label': 'Lineage\nFeatures\n[255, 255]'},
        {'xy': (7, 8.5), 'width': 4, 'height': 0.8, 'label': 'Edge Indices & Attributes\n(4 edge types)'},
    ]
    
    for box in input_boxes:
        rect = FancyBboxPatch(box['xy'], box['width'], box['height'], 
                              boxstyle="round,pad=0.05", edgecolor='black', 
                              facecolor=colors['data'], linewidth=2)
        ax.add_patch(rect)
        ax.text(box['xy'][0] + box['width']/2, box['xy'][1] + box['height']/2, 
                box['label'], ha='center', va='center', fontsize=9)
    
    # Linear Projection
    ax.text(6, 7.8, 'Linear Projection Layer', ha='center', fontsize=11, fontweight='bold')
    
    proj_box = FancyBboxPatch((2, 6.8), 8, 0.8, boxstyle="round,pad=0.05", 
                              edgecolor='black', facecolor=colors['process'], linewidth=2)
    ax.add_patch(proj_box)
    ax.text(6, 7.2, 'Airport: [12900] → [32]  |  Lineage: [255] → [32]', 
            ha='center', va='center', fontsize=10)
    
    # HGT Layers
    for layer_num in range(2):
        y_base = 5.5 - layer_num * 2
        
        ax.text(6, y_base + 0.7, f'HGT Layer {layer_num + 1}', ha='center', 
                fontsize=11, fontweight='bold')
        
        # HGT Conv box
        hgt_box = FancyBboxPatch((1.5, y_base - 0.5), 9, 1, boxstyle="round,pad=0.1", 
                                 edgecolor='black', facecolor=colors['model'], linewidth=3)
        ax.add_patch(hgt_box)
        
        # Components
        components = [
            'Message Passing (Multi-head Attention: 2 heads)',
            'Type-specific transformations',
            'Aggregation across edge types',
            'ReLU Activation + Dropout (0.6)'
        ]
        
        for i, comp in enumerate(components):
            ax.text(2, y_base + 0.3 - i*0.2, f'• {comp}', fontsize=8)
        
        # Arrow
        if layer_num < 1:
            arrow = FancyArrowPatch((6, y_base - 0.55), (6, y_base - 0.95), 
                                   arrowstyle='->', mutation_scale=20, lw=2, color='#333')
            ax.add_patch(arrow)
    
    # Output Embeddings
    ax.text(6, 1.3, 'Output Embeddings', ha='center', fontsize=11, fontweight='bold')
    
    output_boxes = [
        {'xy': (2, 0.3), 'width': 3, 'height': 0.7, 'label': 'Airport Embeddings\n[12900, 32]'},
        {'xy': (7, 0.3), 'width': 3, 'height': 0.7, 'label': 'Lineage Embeddings\n[255, 32]'},
    ]
    
    for box in output_boxes:
        rect = FancyBboxPatch(box['xy'], box['width'], box['height'], 
                              boxstyle="round,pad=0.05", edgecolor='black', 
                              facecolor=colors['output'], linewidth=2)
        ax.add_patch(rect)
        ax.text(box['xy'][0] + box['width']/2, box['xy'][1] + box['height']/2, 
                box['label'], ha='center', va='center', fontsize=9, fontweight='bold')
    
    # Arrows
    arrow_props = dict(arrowstyle='->', mutation_scale=20, lw=2, color='#333')
    ax.annotate('', xy=(6, 8.5), xytext=(6, 9.3), arrowprops=arrow_props)
    ax.annotate('', xy=(6, 6.8), xytext=(6, 7.6), arrowprops=arrow_props)
    ax.annotate('', xy=(3.5, 1.0), xytext=(3.5, 1.5), arrowprops=arrow_props)
    ax.annotate('', xy=(8.5, 1.0), xytext=(8.5, 1.5), arrowprops=arrow_props)
    
    plt.tight_layout()
    plt.savefig('4_model_architecture.png', dpi=300, bbox_inches='tight', facecolor='white')
    print("✓ Created: 4_model_architecture.png")
    plt.close()

# ============================================
# DIAGRAM 5: Training and Prediction Workflow
# ============================================
def create_training_workflow():
    fig, ax = plt.subplots(figsize=(14, 11))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    ax.text(7, 11.5, 'Training and Prediction Workflow', ha='center', 
            fontsize=16, fontweight='bold')
    
    # Training Phase
    ax.text(3.5, 10.5, 'Training Phase', ha='center', fontsize=13, 
            fontweight='bold', bbox=dict(boxstyle='round', facecolor='#FFE5B4', alpha=0.8))
    
    train_steps = [
        {'y': 9.5, 'label': '1. Forward Pass', 
         'desc': 'Input: x_dict (node features), edge_index_dict\nOutput: Node embeddings (Airport: [12900,32], Lineage: [255,32])'},
        {'y': 8.3, 'label': '2. Edge Embedding', 
         'desc': 'Extract embeddings for positive edges (Lineage → Airport)\nCompute dot product: score = src_emb · dst_emb'},
        {'y': 7.1, 'label': '3. Negative Sampling', 
         'desc': 'Generate random negative edges (non-existent connections)\nSame number as positive edges'},
        {'y': 5.9, 'label': '4. Loss Calculation', 
         'desc': 'Binary Cross-Entropy Loss\nPositive edges → label 1, Negative edges → label 0'},
        {'y': 4.7, 'label': '5. Backpropagation', 
         'desc': 'Optimizer: Adam (lr=0.01)\nUpdate model parameters\nEpochs: 100'},
    ]
    
    for step in train_steps:
        rect = FancyBboxPatch((0.5, step['y']-0.5), 6, 0.9, boxstyle="round,pad=0.05", 
                              edgecolor='black', facecolor=colors['process'], linewidth=2)
        ax.add_patch(rect)
        ax.text(1, step['y']-0.1, step['label'], fontsize=10, fontweight='bold')
        ax.text(1.2, step['y']-0.35, step['desc'], fontsize=8)
        
        if step['y'] > 5:
            arrow = FancyArrowPatch((3.5, step['y']-0.55), (3.5, step['y']-0.85), 
                                   arrowstyle='->', mutation_scale=15, lw=2, color='#333')
            ax.add_patch(arrow)
    
    # Prediction Phase
    ax.text(10.5, 10.5, 'Prediction Phase', ha='center', fontsize=13, 
            fontweight='bold', bbox=dict(boxstyle='round', facecolor='#D4F1D4', alpha=0.8))
    
    pred_steps = [
        {'y': 9.5, 'label': '1. Model Evaluation Mode', 
         'desc': 'Set model.eval()\nDisable dropout'},
        {'y': 8.5, 'label': '2. Generate Embeddings', 
         'desc': 'Forward pass on test graph\nGet airport & lineage embeddings'},
        {'y': 7.5, 'label': '3. Compute Risk Scores', 
         'desc': 'For each (lineage, airport) pair:\nrisk = sigmoid(lineage_emb · airport_emb)'},
        {'y': 6.5, 'label': '4. Aggregate Risks', 
         'desc': 'Sum risks across all active lineages\nIdentify high-risk airports'},
        {'y': 5.5, 'label': '5. Evaluation Metrics', 
         'desc': 'Precision, Recall, F1-Score\nROC-AUC, PR-AUC\nTop-K accuracy'},
    ]
    
    for step in pred_steps:
        rect = FancyBboxPatch((7.5, step['y']-0.4), 6, 0.8, boxstyle="round,pad=0.05", 
                              edgecolor='black', facecolor=colors['output'], linewidth=2)
        ax.add_patch(rect)
        ax.text(8, step['y']-0.05, step['label'], fontsize=10, fontweight='bold')
        ax.text(8.2, step['y']-0.25, step['desc'], fontsize=8)
        
        if step['y'] > 5.7:
            arrow = FancyArrowPatch((10.5, step['y']-0.45), (10.5, step['y']-0.75), 
                                   arrowstyle='->', mutation_scale=15, lw=2, color='#333')
            ax.add_patch(arrow)
    
    # Temporal Split Info
    split_box = FancyBboxPatch((1, 3.5), 12, 1.2, boxstyle="round,pad=0.1", 
                               edgecolor='black', facecolor='#F0F0F0', linewidth=3)
    ax.add_patch(split_box)
    
    ax.text(7, 4.3, 'Temporal Train/Test Split', ha='center', fontsize=12, fontweight='bold')
    ax.text(7, 3.95, 'Training: Weeks 0-13 (Jan-Mar 2020) | Testing: Weeks 14-17 (Apr 2020)', 
            ha='center', fontsize=10)
    ax.text(7, 3.65, 'Train Edges: 3,657 | Test Edges: 2,205 | Prevents data leakage', 
            ha='center', fontsize=9, style='italic')
    
    # Key Insights
    insights_box = FancyBboxPatch((1, 0.3), 12, 2.8, boxstyle="round,pad=0.1", 
                                  edgecolor='black', facecolor='#FFFACD', linewidth=2)
    ax.add_patch(insights_box)
    
    ax.text(7, 2.8, 'Key Methodological Insights', ha='center', fontsize=12, fontweight='bold')
    
    insights = [
        '• Link Prediction Task: Predict future lineage-airport connections (viral spread)',
        '• Heterogeneous Graph: Captures complex relationships between viral lineages and geographic locations',
        '• Temporal Modeling: Weekly aggregation + temporal edges capture evolution dynamics',
        '• Multi-relational Learning: HGT learns from flights, samples, phylogeny, and temporal patterns',
        '• Attention Mechanism: 2-head attention weights different edge types and neighbors',
        '• Negative Sampling: Balances positive/negative examples for robust link prediction'
    ]
    
    for i, insight in enumerate(insights):
        ax.text(1.5, 2.4 - i*0.35, insight, fontsize=9)
    
    plt.tight_layout()
    plt.savefig('5_training_workflow.png', dpi=300, bbox_inches='tight', facecolor='white')
    print("✓ Created: 5_training_workflow.png")
    plt.close()

# ============================================
# Generate all diagrams
# ============================================
if __name__ == "__main__":
    print("Generating flow diagrams for research paper...\n")
    
    create_system_architecture()
    create_data_pipeline()
    create_graph_structure()
    create_model_architecture()
    create_training_workflow()
    
    print("\n" + "="*50)
    print("✓ All diagrams generated successfully!")
    print("="*50)
    print("\nGenerated files:")
    print("1. 1_system_architecture.png - Overall system overview")
    print("2. 2_data_pipeline.png - Data processing steps")
    print("3. 3_graph_structure.png - Heterogeneous graph details")
    print("4. 4_model_architecture.png - HGT model structure")
    print("5. 5_training_workflow.png - Training and prediction process")
    print("\nAll diagrams are saved at 300 DPI for publication quality.")