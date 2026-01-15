# Node Editor Implementation Guide

## Overview

This document explains how the node editor system works, critical implementation details, and common pitfalls to avoid. Use this as a reference when implementing node editors in other applications.

## Architecture

### Core Components

```
gui/node_editor/
├── node_base.py           # Base Node class
├── node_socket.py         # Socket (connection point) class
├── node_edge.py           # Edge (connection line) class
├── node_graphics.py       # GraphicsNode (visual representation)
├── node_scene.py          # NodeScene (manages all nodes/edges)
├── node_view.py           # NodeEditorView (viewport with pan/zoom)
├── node_types.py          # Standard node implementations
├── node_interactive_types.py  # Nodes with UI controls
├── node_condition.py      # Custom multi-socket node
└── node_editor_widget.py  # Main widget with toolbar
```

### Class Hierarchy

```
Node (logical)
  └── GraphicsNode (QGraphicsItem - visual)
      └── Socket (QGraphicsItem - connection points)

Edge (logical)
  └── GraphicsEdge (QGraphicsPathItem - visual line)

NodeScene (logical)
  └── QGraphicsScene (Qt scene)

NodeEditorView (QGraphicsView)
```

## Critical Implementation Details

### 1. Coordinate Systems

**THE BIGGEST PITFALL: Coordinate system confusion**

There are THREE coordinate systems:
- **Local coordinates**: Relative to a node (0,0 = top-left of node)
- **Scene coordinates**: Absolute positions in the scene
- **View coordinates**: Screen pixels

#### ✅ CORRECT: Socket Position Calculation

```python
def get_socket_scene_position(self, index, position):
    """Get scene position of socket"""
    from PyQt6.QtCore import QPointF
    node_pos = self.graphics_node.pos()  # Already in scene coords
    
    if position == 0:  # Input (left)
        return node_pos  # Top-left corner
    else:  # Output (right)
        # Simple addition - node_pos is already scene coordinates
        return QPointF(node_pos.x() + self.graphics_node.width, node_pos.y())
```

#### ❌ WRONG: Using mapToScene

```python
# DON'T DO THIS - mapToScene adds transformation twice!
return node_pos + self.graphics_node.mapToScene(width, 0)
```

**Why it fails**: `node_pos` is already in scene coordinates. `mapToScene()` transforms from local to scene, so you're adding scene coords to scene coords = massive offset!

### 2. Edge Updates When Nodes Move

**CRITICAL: Update edges AFTER position changes, not before**

#### ✅ CORRECT: ItemPositionHasChanged

```python
def itemChange(self, change, value):
    if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
        # Snap to grid BEFORE move
        snap_size = 20
        new_pos = value
        snap_x = round(new_pos.x() / snap_size) * snap_size
        snap_y = round(new_pos.y() / snap_size) * snap_size
        return QPointF(snap_x, snap_y)
    
    if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
        # Update edges AFTER position changed
        if hasattr(self, 'node'):
            self.node.update_connected_edges()
    
    return super().itemChange(change, value)
```

#### ❌ WRONG: Updating in ItemPositionChange

```python
# DON'T DO THIS
if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
    self.node.update_connected_edges()  # Node hasn't moved yet!
    return snapped_pos
```

**Why it fails**: `ItemPositionChange` fires BEFORE the move. Edges update with old position, creating growing offset as you drag.

### 3. Drawing Connection Dots

**CRITICAL: Draw dots in paint(), not as child items**

#### ✅ CORRECT: Paint directly

```python
def paint(self, painter, option, widget=None):
    # Draw the line
    painter.drawPath(self.path())
    
    # Draw dots at exact positions
    painter.setBrush(QBrush(QColor("#00ff00")))
    painter.drawEllipse(self.pos_source, 5, 5)  # Start dot
    painter.drawEllipse(self.pos_destination, 5, 5)  # End dot
```

#### ❌ WRONG: Using QGraphicsEllipseItem children

```python
# DON'T DO THIS
self.start_dot = QGraphicsEllipseItem(-4, -4, 8, 8, self)
self.start_dot.setPos(self.source_x, self.source_y)  # Coordinate hell!
```

**Why it fails**: Child items have their own coordinate system. Setting position creates compounding transformations and offsets.

### 4. Socket Positioning

**Sockets must be positioned in LOCAL node coordinates**

#### ✅ CORRECT: Local positioning

```python
def update_position(self):
    """Position socket on node (local coords)"""
    if self.position == 0:  # Input
        self.setPos(0, 0)  # Top-left in LOCAL coords
    else:  # Output
        self.setPos(self.node.graphics_node.width, 0)  # Top-right in LOCAL
```

**Why it works**: Socket is a child of GraphicsNode, so `setPos()` uses node's local coordinate system. Qt handles the scene transformation automatically.

### 5. Edge Position Updates

**Always pull fresh positions from sockets**

```python
def update_positions(self):
    """Update edge from socket positions"""
    source_pos = QPointF(0, 0)
    dest_pos = QPointF(0, 0)
    
    if self.start_socket:
        source_pos = self.start_socket.get_socket_position()  # Fresh!
        
    if self.end_socket:
        dest_pos = self.end_socket.get_socket_position()  # Fresh!
    
    self.graphics_edge.set_source(source_pos.x(), source_pos.y())
    self.graphics_edge.set_destination(dest_pos.x(), dest_pos.y())
    self.graphics_edge.update()
```

**Key point**: Always call `get_socket_position()` which calculates from current node position. Never cache socket positions.

## Socket System

### Standard Nodes (1 input, 1 output)

```python
class Node:
    def __init__(self, scene, title, inputs=None, outputs=None):
        if inputs is None:
            inputs = [1]  # 1 input socket, type 1
        if outputs is None:
            outputs = [1]  # 1 output socket, type 1
```

**Connection points**:
- Input: Top-left corner `(0, 0)`
- Output: Top-right corner `(width, 0)`

### Custom Multi-Socket Nodes

For nodes with multiple sockets (like Condition node), override `get_socket_scene_position()`:

```python
class ConditionNode(Node):
    def __init__(self, scene, title="Condition"):
        super().__init__(scene, title, inputs=[], outputs=[])
        
        # Create custom sockets
        self.inputs = [
            Socket(node=self, index=0, position=0, socket_type=1),  # Top-left
            Socket(node=self, index=1, position=0, socket_type=1),  # Top-center
        ]
        self.outputs = [
            Socket(node=self, index=0, position=1, socket_type=1),  # Right 1/3
            Socket(node=self, index=1, position=1, socket_type=1),  # Right 2/3
        ]
    
    def get_socket_scene_position(self, index, position):
        from PyQt6.QtCore import QPointF
        node_pos = self.graphics_node.pos()
        width = self.graphics_node.width
        height = self.graphics_node.height
        
        if position == 0:  # Inputs
            if index == 0:
                return node_pos  # Top-left
            else:
                return QPointF(node_pos.x() + width/2, node_pos.y())  # Top-center
        else:  # Outputs
            if index == 0:
                return QPointF(node_pos.x() + width, node_pos.y() + height/3)
            else:
                return QPointF(node_pos.x() + width, node_pos.y() + 2*height/3)
```

**Socket visual positioning** (in `node_socket.py`):

```python
def update_position(self):
    """Position socket visually on node"""
    if isinstance(self.node, ConditionNode):
        # Match the scene position calculation but in local coords
        if self.position == 0:  # Inputs
            if self.index == 0:
                self.setPos(0, 0)
            else:
                self.setPos(width/2, 0)
        else:  # Outputs
            if self.index == 0:
                self.setPos(width, height/3)
            else:
                self.setPos(width, 2*height/3)
```

**CRITICAL**: Socket visual position (local) must match scene position calculation!

## Grid Snapping

### Node Snapping

```python
def itemChange(self, change, value):
    if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
        snap_size = 20
        new_pos = value
        snap_x = round(new_pos.x() / snap_size) * snap_size
        snap_y = round(new_pos.y() / snap_size) * snap_size
        return QPointF(snap_x, snap_y)
```

### Connection Snapping

During edge dragging, detect nearby sockets:

```python
def mouseMoveEvent(self, event):
    if self.mode == 'edge_drag':
        pos = self.mapToScene(event.pos())
        
        # Search for nearby sockets
        search_rect = QRectF(pos.x() - 20, pos.y() - 20, 40, 40)
        items = self.scene().items(search_rect)
        
        for item in items:
            if isinstance(item, Socket) and item.position == 0:
                # Snap to socket
                socket_pos = item.get_socket_position()
                self.dragging_edge.graphics_edge.set_destination(
                    socket_pos.x(), socket_pos.y()
                )
                return
```

## Interactive UI Elements in Nodes

Use `QGraphicsProxyWidget` to embed Qt widgets:

```python
class GeneratorNode(Node):
    def __init__(self, scene, title="Generator"):
        super().__init__(scene, title, inputs=[], outputs=[1])
        
        # Create widget
        self.content_widget = QWidget()
        layout = QVBoxLayout(self.content_widget)
        
        # Add controls
        self.time_input = QDoubleSpinBox()
        layout.addWidget(self.time_input)
        
        # Embed in scene
        self.proxy = QGraphicsProxyWidget(self.graphics_node)
        self.proxy.setWidget(self.content_widget)
        self.proxy.setPos(10, self.graphics_node.title_height + 5)
```

**Styling**: Use stylesheets for dark theme:

```python
self.content_widget.setStyleSheet("""
    QWidget { background: transparent; color: #ffffff; }
    QSpinBox { 
        background: #1a1a1a; 
        color: #ffffff;
        border: 1px solid #3a3a3a;
    }
""")
```

## Connection Logic

### Starting a Connection

```python
def left_mouse_button_press(self, event):
    item = self.itemAt(event.pos())
    
    # Can start from socket or node
    if isinstance(item, Socket):
        self.mode = 'edge_drag'
        self.dragging_edge = Edge(self.node_scene, item, None)
    elif isinstance(item, GraphicsNode):
        # Start from first output
        if item.node.outputs:
            self.mode = 'edge_drag'
            self.dragging_edge = Edge(self.node_scene, item.node.outputs[0], None)
```

### Completing a Connection

```python
def left_mouse_button_release(self, event):
    if self.mode == 'edge_drag':
        scene_pos = self.mapToScene(event.pos())
        search_rect = QRectF(scene_pos.x() - 30, scene_pos.y() - 30, 60, 60)
        items = self.scene().items(search_rect)
        
        target_socket = None
        
        # Find socket or node
        for item in items:
            if isinstance(item, Socket):
                target_socket = item
                break
            elif isinstance(item, GraphicsNode):
                if item.node.inputs:
                    target_socket = item.node.inputs[0]
                    break
        
        if target_socket:
            # Complete connection
            self.dragging_edge.end_socket = target_socket
            target_socket.add_edge(self.dragging_edge)
            self.dragging_edge.update_positions()
            self.node_scene.add_edge(self.dragging_edge)
        else:
            # Cancel
            self.dragging_edge.remove()
```

## Save/Load System

### Saving

```python
def save_graph(self):
    graph_data = {'nodes': [], 'edges': []}
    
    # Save nodes
    for i, node in enumerate(self.scene.nodes):
        node_data = {
            'id': i,
            'type': type(node).__name__,
            'title': node.title,
            'pos_x': node.pos.x(),
            'pos_y': node.pos.y()
        }
        
        # Save node-specific data
        if hasattr(node, 'get_values'):
            node_data['values'] = node.get_values()
            
        graph_data['nodes'].append(node_data)
    
    # Save edges
    for edge in self.scene.edges:
        if edge.start_socket and edge.end_socket:
            edge_data = {
                'start_node': self.scene.nodes.index(edge.start_socket.node),
                'start_socket': edge.start_socket.index,
                'end_node': self.scene.nodes.index(edge.end_socket.node),
                'end_socket': edge.end_socket.index
            }
            graph_data['edges'].append(edge_data)
    
    with open('node_graph.json', 'w') as f:
        json.dump(graph_data, f, indent=2)
```

### Loading

```python
def load_graph(self):
    with open('node_graph.json', 'r') as f:
        graph_data = json.load(f)
    
    self.scene.clear()
    loaded_nodes = []
    
    # Load nodes
    for node_data in graph_data['nodes']:
        node_type = node_data['type']
        
        if node_type == 'GeneratorNode':
            node = GeneratorNode(self.scene, node_data['title'])
            if 'values' in node_data:
                node.set_values(node_data['values'])
        # ... other node types
        
        node.set_pos(node_data['pos_x'], node_data['pos_y'])
        loaded_nodes.append(node)
    
    # Load edges
    for edge_data in graph_data['edges']:
        start_node = loaded_nodes[edge_data['start_node']]
        end_node = loaded_nodes[edge_data['end_node']]
        
        start_socket = start_node.outputs[edge_data['start_socket']]
        end_socket = end_node.inputs[edge_data['end_socket']]
        
        edge = Edge(self.scene, start_socket, end_socket)
        self.scene.add_edge(edge)
```

## Common Pitfalls Summary

### 1. Coordinate System Confusion
- ❌ Using `mapToScene()` on already-scene coordinates
- ✅ Use simple addition: `node_pos.x() + offset`

### 2. Edge Update Timing
- ❌ Updating edges in `ItemPositionChange` (before move)
- ✅ Update in `ItemPositionHasChanged` (after move)

### 3. Connection Dot Positioning
- ❌ Creating child QGraphicsItems for dots
- ✅ Draw dots directly in `paint()` method

### 4. Socket Position Caching
- ❌ Storing socket positions as variables
- ✅ Always call `get_socket_position()` for fresh coords

### 5. Local vs Scene Coordinates
- ❌ Mixing coordinate systems
- ✅ Socket `setPos()` = local, `get_socket_scene_position()` = scene

## Integration Checklist

When adding node editor to existing app:

1. ✅ Create `node_editor/` package structure
2. ✅ Implement base classes (Node, Socket, Edge, Scene, View)
3. ✅ Use QPointF for all position calculations
4. ✅ Never use `mapToScene()` for scene coordinate math
5. ✅ Update edges in `ItemPositionHasChanged`, not `ItemPositionChange`
6. ✅ Draw connection dots in `paint()`, not as child items
7. ✅ Position sockets in local coords, calculate connections in scene coords
8. ✅ Implement grid snapping in `ItemPositionChange`
9. ✅ Add socket detection with `QRectF` search areas
10. ✅ Test with nodes at various positions to verify no offset accumulation

## Performance Considerations

- Set proper Z-values: edges = -1, nodes = 0, sockets = 1
- Use `setFlag(ItemSendsGeometryChanges)` for move notifications
- Call `update()` on edges only when positions actually change
- Use `QGraphicsScene.items(QRectF)` for spatial queries, not iteration

## Debugging Tips

**Offset issues**: Print coordinates at each step:
```python
print(f"Node pos: {node_pos}, Socket scene: {socket_pos}, Edge dest: {edge.dest}")
```

**Missing updates**: Check if `update_connected_edges()` is called

**Invisible items**: Verify `boundingRect()` and Z-values

**Wrong coordinates**: Check if using local vs scene coords correctly

---

**This implementation is battle-tested and solves all major coordinate system pitfalls. Follow these patterns exactly for reliable node editor behavior.**
