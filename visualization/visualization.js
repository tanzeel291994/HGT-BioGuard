// Advanced D3.js Visualization for Heterogeneous Graph
// Author: AI Assistant for Hackathon Project
// Features: Multiple layouts, animations, interactive controls, and more!

// Global variables
let graphData = null;
let simulation = null;
let svg, g, link, node, label;
let width, height;
let currentLayout = 'force';
let zoom;

// Color schemes
const colors = {
    airport: '#4fc3f7',
    lineage: '#f50057',
    flight: '#ffd700',
    sampled_at: '#00e676',
    evolves_from: '#ff6e40',
    temporal: '#b388ff'
};

// Configuration
const config = {
    chargeStrength: -100,
    linkDistance: 50,
    nodeSize: 5,
    showLabels: true,
    animateEdges: false,
    showArrows: true,
    viewMode: 'all',
    edgeType: 'all'
};

// Initialize
function init() {
    // Set up SVG
    svg = d3.select('#graph-canvas');
    width = window.innerWidth;
    height = window.innerHeight;
    
    svg.attr('width', width)
       .attr('height', height);
    
    // Create main group for zooming/panning
    g = svg.append('g');
    
    // Set up zoom behavior
    zoom = d3.zoom()
        .scaleExtent([0.1, 10])
        .on('zoom', (event) => {
            g.attr('transform', event.transform);
        });
    
    svg.call(zoom);
    
    // Create arrow markers for directed edges
    createArrowMarkers();
    
    // Set up event listeners
    setupEventListeners();
    
    // Load data
    loadData();
}

// Create arrow markers for different edge types
function createArrowMarkers() {
    const defs = svg.append('defs');
    
    Object.keys(colors).forEach(type => {
        if (type !== 'airport' && type !== 'lineage') {
            defs.append('marker')
                .attr('id', `arrow-${type}`)
                .attr('viewBox', '0 -5 10 10')
                .attr('refX', 20)
                .attr('refY', 0)
                .attr('markerWidth', 6)
                .attr('markerHeight', 6)
                .attr('orient', 'auto')
                .append('path')
                .attr('d', 'M0,-5L10,0L0,5')
                .attr('fill', colors[type]);
        }
    });
}

// Load graph data
async function loadData() {
    try {
        const response = await fetch('graph_data.json');
        graphData = await response.json();
        
        console.log('Loaded graph data:', graphData.metadata);
        
        // Update stats
        updateStats();
        
        // Hide loading screen
        document.getElementById('loading').style.display = 'none';
        
        // Create visualization
        createVisualization();
        
    } catch (error) {
        console.error('Error loading data:', error);
        document.getElementById('loading-text').textContent = 
            'Error loading data. Please ensure graph_data.json exists.';
    }
}

// Update statistics panel
function updateStats() {
    const airports = graphData.nodes.filter(n => n.type === 'airport').length;
    const lineages = graphData.nodes.filter(n => n.type === 'lineage').length;
    
    document.getElementById('airportCount').textContent = airports;
    document.getElementById('lineageCount').textContent = lineages;
    document.getElementById('totalNodes').textContent = graphData.nodes.length;
    document.getElementById('totalEdges').textContent = graphData.links.length;
    
    updateVisibleStats();
}

// Update visible node/edge counts
function updateVisibleStats() {
    const visibleNodes = g.selectAll('.node').filter(function() {
        return d3.select(this).style('display') !== 'none';
    }).size();
    
    const visibleEdges = g.selectAll('.link').filter(function() {
        return d3.select(this).style('display') !== 'none';
    }).size();
    
    document.getElementById('visibleNodes').textContent = visibleNodes;
    document.getElementById('visibleEdges').textContent = visibleEdges;
}

// Create visualization
function createVisualization() {
    // Clear existing elements
    g.selectAll('*').remove();
    
    // Create link group
    const linkGroup = g.append('g').attr('class', 'links');
    
    // Create node group
    const nodeGroup = g.append('g').attr('class', 'nodes');
    
    // Create label group
    const labelGroup = g.append('g').attr('class', 'labels');
    
    // Set up force simulation
    simulation = d3.forceSimulation(graphData.nodes)
        .force('link', d3.forceLink(graphData.links)
            .id(d => d.id)
            .distance(config.linkDistance))
        .force('charge', d3.forceManyBody()
            .strength(config.chargeStrength))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide()
            .radius(d => getNodeRadius(d) + 2));
    
    // Create links
    link = linkGroup.selectAll('.link')
        .data(graphData.links)
        .enter()
        .append('line')
        .attr('class', 'link')
        .attr('stroke', d => colors[d.type])
        .attr('stroke-width', d => Math.sqrt(d.weight) * 0.5)
        .attr('marker-end', d => config.showArrows ? `url(#arrow-${d.type})` : null)
        .on('mouseover', showEdgeTooltip)
        .on('mouseout', hideTooltip);
    
    // Create nodes
    node = nodeGroup.selectAll('.node')
        .data(graphData.nodes)
        .enter()
        .append('circle')
        .attr('class', 'node')
        .attr('r', getNodeRadius)
        .attr('fill', d => colors[d.type])
        .attr('stroke', '#fff')
        .attr('stroke-width', 2)
        .on('mouseover', showNodeTooltip)
        .on('mouseout', hideTooltip)
        .on('click', highlightConnected)
        .call(drag(simulation));
    
    // Create labels
    label = labelGroup.selectAll('.node-label')
        .data(graphData.nodes)
        .enter()
        .append('text')
        .attr('class', 'node-label')
        .attr('text-anchor', 'middle')
        .attr('dy', d => getNodeRadius(d) + 12)
        .text(d => d.type === 'airport' ? d.code : d.name)
        .style('display', config.showLabels ? 'block' : 'none');
    
    // Update positions on each tick
    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        
        node
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);
        
        label
            .attr('x', d => d.x)
            .attr('y', d => d.y);
    });
    
    // Apply initial filters
    applyFilters();
}

// Get node radius based on type and configuration
function getNodeRadius(d) {
    const baseSize = config.nodeSize;
    return d.type === 'airport' ? baseSize * 1.2 : baseSize;
}

// Drag behavior
function drag(simulation) {
    function dragstarted(event) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
    }
    
    function dragged(event) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
    }
    
    function dragended(event) {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
    }
    
    return d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended);
}

// Show node tooltip
function showNodeTooltip(event, d) {
    const tooltip = d3.select('#tooltip');
    
    let content = `<div class="tooltip-title">${d.type.toUpperCase()}</div>`;
    
    if (d.type === 'airport') {
        content += `
            <div class="tooltip-row"><strong>Code:</strong> ${d.code}</div>
            <div class="tooltip-row"><strong>City:</strong> ${d.city || 'N/A'}</div>
            <div class="tooltip-row"><strong>Country:</strong> ${d.country || 'N/A'}</div>
            <div class="tooltip-row"><strong>Coordinates:</strong> ${d.lat.toFixed(2)}, ${d.lon.toFixed(2)}</div>
        `;
    } else {
        content += `
            <div class="tooltip-row"><strong>Lineage:</strong> ${d.name}</div>
            <div class="tooltip-row"><strong>Index:</strong> ${d.index}</div>
        `;
    }
    
    tooltip
        .html(content)
        .classed('visible', true)
        .style('left', (event.pageX + 10) + 'px')
        .style('top', (event.pageY - 10) + 'px');
    
    // Highlight node
    d3.select(event.currentTarget)
        .transition()
        .duration(200)
        .attr('r', getNodeRadius(d) * 1.5)
        .attr('stroke-width', 4);
}

// Show edge tooltip
function showEdgeTooltip(event, d) {
    const tooltip = d3.select('#tooltip');
    
    const sourceNode = graphData.nodes.find(n => n.id === d.source.id);
    const targetNode = graphData.nodes.find(n => n.id === d.target.id);
    
    let content = `<div class="tooltip-title">${d.type.replace('_', ' ').toUpperCase()}</div>`;
    content += `<div class="tooltip-row"><strong>From:</strong> ${sourceNode.code || sourceNode.name}</div>`;
    content += `<div class="tooltip-row"><strong>To:</strong> ${targetNode.code || targetNode.name}</div>`;
    content += `<div class="tooltip-row"><strong>Weight:</strong> ${d.weight.toFixed(2)}</div>`;
    
    if (d.week !== undefined) {
        content += `<div class="tooltip-row"><strong>Week:</strong> ${d.week}</div>`;
    }
    if (d.time_start !== undefined) {
        content += `<div class="tooltip-row"><strong>Time:</strong> ${d.time_start} → ${d.time_end}</div>`;
    }
    
    tooltip
        .html(content)
        .classed('visible', true)
        .style('left', (event.pageX + 10) + 'px')
        .style('top', (event.pageY - 10) + 'px');
    
    // Highlight edge
    d3.select(event.currentTarget)
        .transition()
        .duration(200)
        .attr('stroke-width', 4)
        .style('stroke-opacity', 1);
}

// Hide tooltip
function hideTooltip(event, d) {
    d3.select('#tooltip').classed('visible', false);
    
    // Reset node/edge styling
    if (event.currentTarget.tagName === 'circle') {
        d3.select(event.currentTarget)
            .transition()
            .duration(200)
            .attr('r', getNodeRadius(d))
            .attr('stroke-width', 2);
    } else {
        d3.select(event.currentTarget)
            .transition()
            .duration(200)
            .attr('stroke-width', d => Math.sqrt(d.weight) * 0.5)
            .style('stroke-opacity', 0.6);
    }
}

// Highlight connected nodes
function highlightConnected(event, d) {
    // Get connected node IDs
    const connectedNodes = new Set([d.id]);
    const connectedLinks = new Set();
    
    graphData.links.forEach(link => {
        if (link.source.id === d.id) {
            connectedNodes.add(link.target.id);
            connectedLinks.add(link);
        }
        if (link.target.id === d.id) {
            connectedNodes.add(link.source.id);
            connectedLinks.add(link);
        }
    });
    
    // Fade non-connected elements
    node
        .transition()
        .duration(300)
        .style('opacity', n => connectedNodes.has(n.id) ? 1 : 0.1);
    
    link
        .transition()
        .duration(300)
        .style('opacity', l => connectedLinks.has(l) ? 1 : 0.05);
    
    label
        .transition()
        .duration(300)
        .style('opacity', n => connectedNodes.has(n.id) ? 1 : 0.1);
    
    // Reset after 3 seconds
    setTimeout(() => {
        node.transition().duration(500).style('opacity', 1);
        link.transition().duration(500).style('opacity', 0.6);
        label.transition().duration(500).style('opacity', 1);
    }, 3000);
}

// Apply filters based on view mode and edge type
function applyFilters() {
    const viewMode = config.viewMode;
    const edgeType = config.edgeType;
    
    // Filter nodes
    node.style('display', d => {
        if (viewMode === 'all') return 'block';
        if (viewMode === 'airports') return d.type === 'airport' ? 'block' : 'none';
        if (viewMode === 'lineages') return d.type === 'lineage' ? 'block' : 'none';
        if (viewMode === 'flights' || viewMode === 'evolution') return 'block';
        return 'block';
    });
    
    // Filter edges
    link.style('display', d => {
        if (edgeType !== 'all' && d.type !== edgeType) return 'none';
        
        if (viewMode === 'all') return 'block';
        if (viewMode === 'flights') return d.type === 'flight' ? 'block' : 'none';
        if (viewMode === 'evolution') {
            return (d.type === 'evolves_from' || d.type === 'temporal') ? 'block' : 'none';
        }
        if (viewMode === 'airports') {
            return d.type === 'flight' ? 'block' : 'none';
        }
        if (viewMode === 'lineages') {
            return (d.type === 'evolves_from' || d.type === 'temporal') ? 'block' : 'none';
        }
        
        return 'block';
    });
    
    // Filter labels
    label.style('display', d => {
        if (!config.showLabels) return 'none';
        return node.filter(n => n.id === d.id).style('display');
    });
    
    // Update arrow visibility
    link.attr('marker-end', d => {
        if (!config.showArrows) return null;
        if (link.filter(l => l === d).style('display') === 'none') return null;
        return `url(#arrow-${d.type})`;
    });
    
    // Apply edge animation
    if (config.animateEdges) {
        link.classed('animated-edge', true);
    } else {
        link.classed('animated-edge', false);
    }
    
    updateVisibleStats();
}

// Switch layout mode
function switchLayout(mode) {
    currentLayout = mode;
    
    if (mode === 'force') {
        // Standard force-directed layout
        simulation
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('x', null)
            .force('y', null)
            .alpha(1)
            .restart();
    } else if (mode === 'geo') {
        // Geographic layout for airports
        simulation
            .force('center', null)
            .force('x', d3.forceX(d => {
                if (d.type === 'airport') {
                    const x = (d.lon + 180) * (width / 360);
                    return x;
                }
                return width / 2;
            }).strength(d => d.type === 'airport' ? 0.5 : 0.1))
            .force('y', d3.forceY(d => {
                if (d.type === 'airport') {
                    const y = (90 - d.lat) * (height / 180);
                    return y;
                }
                return height / 2;
            }).strength(d => d.type === 'airport' ? 0.5 : 0.1))
            .alpha(1)
            .restart();
    } else if (mode === 'radial') {
        // Radial layout - airports in outer ring, lineages in inner ring
        simulation
            .force('center', null)
            .force('x', d3.forceX(width / 2).strength(0.1))
            .force('y', d3.forceY(height / 2).strength(0.1))
            .force('radial', d3.forceRadial(
                d => d.type === 'airport' ? Math.min(width, height) * 0.4 : Math.min(width, height) * 0.2,
                width / 2,
                height / 2
            ).strength(0.8))
            .alpha(1)
            .restart();
    }
}

// Set up event listeners
function setupEventListeners() {
    // View mode buttons
    document.querySelectorAll('.view-mode-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.view-mode-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            switchLayout(this.dataset.mode);
        });
    });
    
    // View mode select
    document.getElementById('viewMode').addEventListener('change', function() {
        config.viewMode = this.value;
        applyFilters();
    });
    
    // Edge type select
    document.getElementById('edgeType').addEventListener('change', function() {
        config.edgeType = this.value;
        document.getElementById('edgeTypeDisplay').textContent = 
            this.options[this.selectedIndex].text;
        applyFilters();
    });
    
    // Charge strength slider
    document.getElementById('chargeStrength').addEventListener('input', function() {
        config.chargeStrength = parseFloat(this.value);
        document.getElementById('chargeValue').textContent = this.value;
        if (simulation) {
            simulation.force('charge').strength(config.chargeStrength);
            simulation.alpha(0.3).restart();
        }
    });
    
    // Link distance slider
    document.getElementById('linkDistance').addEventListener('input', function() {
        config.linkDistance = parseFloat(this.value);
        document.getElementById('linkValue').textContent = this.value;
        if (simulation) {
            simulation.force('link').distance(config.linkDistance);
            simulation.alpha(0.3).restart();
        }
    });
    
    // Node size slider
    document.getElementById('nodeSize').addEventListener('input', function() {
        config.nodeSize = parseFloat(this.value);
        document.getElementById('nodeSizeValue').textContent = this.value;
        if (node) {
            node.attr('r', getNodeRadius);
            label.attr('dy', d => getNodeRadius(d) + 12);
        }
    });
    
    // Show labels checkbox
    document.getElementById('showLabels').addEventListener('change', function() {
        config.showLabels = this.checked;
        if (label) {
            label.style('display', config.showLabels ? 'block' : 'none');
            applyFilters();
        }
    });
    
    // Animate edges checkbox
    document.getElementById('animateEdges').addEventListener('change', function() {
        config.animateEdges = this.checked;
        applyFilters();
    });
    
    // Show arrows checkbox
    document.getElementById('showArrows').addEventListener('change', function() {
        config.showArrows = this.checked;
        applyFilters();
    });
    
    // Window resize
    window.addEventListener('resize', () => {
        width = window.innerWidth;
        height = window.innerHeight;
        svg.attr('width', width).attr('height', height);
        if (simulation) {
            simulation.force('center', d3.forceCenter(width / 2, height / 2));
            simulation.alpha(0.3).restart();
        }
    });
}

// Restart simulation
function restartSimulation() {
    if (simulation) {
        // Reset node positions
        graphData.nodes.forEach(node => {
            delete node.x;
            delete node.y;
            delete node.vx;
            delete node.vy;
        });
        
        simulation.alpha(1).restart();
    }
}

// Center graph
function centerGraph() {
    const bounds = g.node().getBBox();
    const fullWidth = width;
    const fullHeight = height;
    const midX = bounds.x + bounds.width / 2;
    const midY = bounds.y + bounds.height / 2;
    
    const scale = 0.8 / Math.max(bounds.width / fullWidth, bounds.height / fullHeight);
    const translate = [fullWidth / 2 - scale * midX, fullHeight / 2 - scale * midY];
    
    svg.transition()
        .duration(750)
        .call(zoom.transform, d3.zoomIdentity.translate(translate[0], translate[1]).scale(scale));
}

// Export current view as SVG
function exportView() {
    const svgData = document.getElementById('graph-canvas').outerHTML;
    const blob = new Blob([svgData], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `graph_view_${Date.now()}.svg`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);

