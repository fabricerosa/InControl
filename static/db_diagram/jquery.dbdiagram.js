/*  Graph JavaScript framework, version 0.0.1
 *  (c) 2006 Aslak Hellesoy <aslak.hellesoy@gmail.com>
 *  (c) 2006 Dave Hoover <dave.hoover@gmail.com>
 *
 *  Ported from Graph::Layouter::Spring in
 *    http://search.cpan.org/~pasky/Graph-Layderer-0.02/
 *  The algorithm is based on a spring-style layouter of a Java-based social
 *  network tracker PieSpy written by Paul Mutton E<lt>paul@jibble.orgE<gt>.
 *
 *  Graph is freely distributable under the terms of an MIT-style license.
 *  For details, see the Graph web site: http://dev.buildpatternd.com/trac
 *_____________________________________________________________________________
 *
 * Adapted and translated to jQuery by Paolo Caruccio for
 * web2py database diagram representation
 *
 * last modified 30 Jan 2013 by Paolo Caruccio
/*--------------------------------------------------------------------------*/

/*
 * Graph
 */
var Graph = function() {
    this.nodeSet = {};
    this.nodes = [];
    this.edges = [];
};
Graph.prototype = {
    addNode: function(value) {
        var key = value.id;
        var element = value;
        var node = this.nodeSet[key];
        /* testing if node is already existing in the graph */
        if(node == undefined) {
            node = new Graph.Node(element);
            this.nodeSet[key] = node;
            this.nodes.push(node);
        }
        return node;
    },
  
    addEdge: function(source, target) {
        var s = this.addNode(source[0]);
        var t = this.addNode(target[0]);
        var edge = {source: s, target: t};
        this.edges.push(edge);
    }
};

/*
 * Node
 */
Graph.Node = function(value){
    this.value = value;
};
Graph.Node.prototype = {
};

/*
 * Renderer base class
 */
Graph.Renderer = {};
/*
 * Renderer basic implementation
 */
Graph.Renderer.Basic = function(ele, graph) {
  this.width = ele[0].offsetWidth || 400;
  this.height = ele[0].offsetHeight || 400;
  this.graph = graph;
  //this.radius = 40;
  this.radius = (graph.layoutMaxW - graph.layoutMaxH) > 0 ? graph.layoutMaxW/2 : graph.layoutMaxH/2
};
Graph.Renderer.Basic.prototype = {
    translate: function(point) {
        return [
            (point[0] - this.graph.layoutMinX) * this.factorX + this.radius,
            (point[1] - this.graph.layoutMinY) * this.factorY + this.radius
        ];
    },
    
    draw: function() {
        this.factorX = (this.width - 2 * this.radius) / (this.graph.layoutMaxX - this.graph.layoutMinX);
        this.factorY = (this.height - 2 * this.radius) / (this.graph.layoutMaxY - this.graph.layoutMinY);
        for (i in this.graph.nodes) {
            this.drawNode(this.graph.nodes[i]);
        }
    },

    drawNode: function(node) {
        var point = this.translate([node.layoutPosX, node.layoutPosY]);
        node.value.style.position = 'absolute';
        node.value.style.top      = (point[1] - this.radius) + 'px';
        node.value.style.left     = (point[0] - this.radius)  + 'px';
    }
};

/*
 * Layout base class
 */
Graph.Layout = {};
/*
 * Spring layout
 */
Graph.Layout.Spring = function(graph) {
    this.graph = graph;
    this.iterations = 1500; //default 500
    this.maxRepulsiveForceDistance = 6; //default 6
    this.k = 2; //default 2
    this.c = 0.01; //default 0.01 [min value 0.01 max value 0.1]
    this.maxVertexMovement = 0.5; //default 0.5
    this.layout();
};
Graph.Layout.Spring.prototype = {
    layout: function() {
        this.layoutPrepare();
        for (var i = 0; i < this.iterations; i++) {
            this.layoutIteration();
        }
        this.layoutCalcBounds();
    },

    layoutPrepare: function() {
        for (i in this.graph.nodes) {
            var node = this.graph.nodes[i];
            node.layoutPosX = 0;
            node.layoutPosY = 0;
            node.layoutForceX = 0;
            node.layoutForceY = 0;
        }

    },

    layoutCalcBounds: function() {
        var minx = Infinity, maxx = -Infinity, miny = Infinity, maxy = -Infinity;
        var maxw = 0, maxh = 0;
        for (i in this.graph.nodes) {
            var x = this.graph.nodes[i].layoutPosX;
            var y = this.graph.nodes[i].layoutPosY;
            

            if(x > maxx) {
                maxx = x;
                maxw = this.graph.nodes[i].value.offsetWidth;
            } 
            if(x < minx) minx = x;
            if(y > maxy) {
                maxy = y;
                maxh = this.graph.nodes[i].value.offsetHeight;
            }
            if(y < miny) miny = y;
        }

        this.graph.layoutMinX = minx;
        this.graph.layoutMaxX = maxx;
        this.graph.layoutMinY = miny;
        this.graph.layoutMaxY = maxy;
        this.graph.layoutMaxW = maxw;
        this.graph.layoutMaxH = maxh;
    },

    layoutIteration: function() {
        // Forces on nodes due to node-node repulsions

        var prev = new Array();
        for(var c in this.graph.nodes) {
            var node1 = this.graph.nodes[c];
            for (var d in prev) {
                var node2 = this.graph.nodes[prev[d]];
                this.layoutRepulsive(node1, node2);

            }
            prev.push(c);
        }

        // Forces on nodes due to edge attractions
        for (var i = 0; i < this.graph.edges.length; i++) {
            var edge = this.graph.edges[i];
            this.layoutAttractive(edge);
        }

        // Move by the given force
        for (i in this.graph.nodes) {
            var node = this.graph.nodes[i];
            var xmove = this.c * node.layoutForceX;
            var ymove = this.c * node.layoutForceY;

            var max = this.maxVertexMovement;
            if(xmove > max) xmove = max;
            if(xmove < -max) xmove = -max;
            if(ymove > max) ymove = max;
            if(ymove < -max) ymove = -max;

            node.layoutPosX += xmove;
            node.layoutPosY += ymove;
            node.layoutForceX = 0;
            node.layoutForceY = 0;
        }
    },

    layoutRepulsive: function(node1, node2) {
        if (typeof node1 == 'undefined' || typeof node2 == 'undefined')
            return;
        var dx = node2.layoutPosX - node1.layoutPosX;
        var dy = node2.layoutPosY - node1.layoutPosY;
        var d2 = dx * dx + dy * dy;
        if(d2 < 0.01) {
            dx = 0.1 * Math.random() + 0.1;
            dy = 0.1 * Math.random() + 0.1;
            var d2 = dx * dx + dy * dy;
        }
        var d = Math.sqrt(d2);
        if(d < this.maxRepulsiveForceDistance) {
            var repulsiveForce = this.k * this.k / d;
            node2.layoutForceX += repulsiveForce * dx / d;
            node2.layoutForceY += repulsiveForce * dy / d;
            node1.layoutForceX -= repulsiveForce * dx / d;
            node1.layoutForceY -= repulsiveForce * dy / d;
        }
    },

    layoutAttractive: function(edge) {
        var node1 = edge.source;
        var node2 = edge.target;

        var dx = node2.layoutPosX - node1.layoutPosX;
        var dy = node2.layoutPosY - node1.layoutPosY;
        var d2 = dx * dx + dy * dy;
        if(d2 < 0.01) {
            dx = 0.1 * Math.random() + 0.1;
            dy = 0.1 * Math.random() + 0.1;
            var d2 = dx * dx + dy * dy;
        }
        var d = Math.sqrt(d2);
        if(d > this.maxRepulsiveForceDistance) {
            d = this.maxRepulsiveForceDistance;
            d2 = d * d;
        }
        var attractiveForce = (d2 - this.k * this.k) / this.k;
        if(edge.attraction == undefined) edge.attraction = 1;
        attractiveForce *= Math.log(edge.attraction) * 0.5 + 1;

        node2.layoutForceX -= attractiveForce * dx / d;
        node2.layoutForceY -= attractiveForce * dy / d;
        node1.layoutForceX += attractiveForce * dx / d;
        node1.layoutForceY += attractiveForce * dy / d;
    }
};