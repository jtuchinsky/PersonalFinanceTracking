import React, { useState, useEffect, useRef, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';
import { AuthContext } from '../App';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { ArrowLeft, BarChart3, Eye, ToggleLeft, ToggleRight } from 'lucide-react';
import * as d3 from 'd3';
import { sankey, sankeyLinkHorizontal } from 'd3-sankey';

const SankeyDiagram = () => {
  const [transactions, setTransactions] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [viewMode, setViewMode] = useState('category'); // 'category' or 'account'
  const [selectedNode, setSelectedNode] = useState(null);
  const [loading, setLoading] = useState(true);
  const svgRef = useRef();
  const { API } = useContext(AuthContext);
  const navigate = useNavigate();

  const width = 800;
  const height = 500;
  const margin = { top: 20, right: 120, bottom: 20, left: 120 };

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    if (transactions.length > 0 && accounts.length > 0 && categories.length > 0) {
      createSankeyDiagram();
    }
  }, [transactions, accounts, categories, viewMode, selectedNode]);

  const fetchData = async () => {
    try {
      const [transactionsRes, accountsRes, categoriesRes] = await Promise.all([
        axios.get(`${API}/transactions?limit=100`),
        axios.get(`${API}/accounts`),
        axios.get(`${API}/categories`)
      ]);
      
      setTransactions(transactionsRes.data);
      setAccounts(accountsRes.data);
      setCategories(categoriesRes.data);
    } catch (error) {
      console.error('Failed to fetch data:', error);
      toast.error('Failed to load transaction data');
    } finally {
      setLoading(false);
    }
  };

  const getCategoryColor = (categoryName) => {
    const category = categories.find(c => c.name === categoryName);
    return category ? category.color : '#6b7280';
  };

  const getAccountColor = (accountType) => {
    switch (accountType) {
      case 'checking': return '#10b981';
      case 'savings': return '#3b82f6';
      case 'credit_card': return '#f59e0b';
      default: return '#6b7280';
    }
  };

  const prepareDataForSankey = () => {
    const nodes = [];
    const links = [];
    const nodeMap = new Map();

    if (viewMode === 'category') {
      // Category view: Income Categories -> Accounts -> Expense Categories
      
      // Create nodes for income categories
      const incomeTransactions = transactions.filter(t => t.transaction_type === 'credit');
      const incomeCategories = [...new Set(incomeTransactions.map(t => t.category))];
      
      incomeCategories.forEach(category => {
        const nodeId = `income_${category}`;
        nodes.push({
          id: nodeId,
          name: category,
          type: 'income_category',
          color: getCategoryColor(category),
          value: incomeTransactions
            .filter(t => t.category === category)
            .reduce((sum, t) => sum + Math.abs(t.amount), 0)
        });
        nodeMap.set(nodeId, nodes.length - 1);
      });

      // Create nodes for accounts
      accounts.forEach(account => {
        const nodeId = `account_${account.id}`;
        nodes.push({
          id: nodeId,
          name: account.nickname || account.name,
          type: 'account',
          color: getAccountColor(account.account_type),
          accountData: account,
          value: Math.abs(account.balance)
        });
        nodeMap.set(nodeId, nodes.length - 1);
      });

      // Create nodes for expense categories
      const expenseTransactions = transactions.filter(t => t.transaction_type === 'debit');
      const expenseCategories = [...new Set(expenseTransactions.map(t => t.category))];
      
      expenseCategories.forEach(category => {
        const nodeId = `expense_${category}`;
        nodes.push({
          id: nodeId,
          name: category,
          type: 'expense_category',
          color: getCategoryColor(category),
          value: expenseTransactions
            .filter(t => t.category === category)
            .reduce((sum, t) => sum + Math.abs(t.amount), 0)
        });
        nodeMap.set(nodeId, nodes.length - 1);
      });

      // Create links for income -> accounts
      incomeTransactions.forEach(transaction => {
        const sourceId = `income_${transaction.category}`;
        const targetId = `account_${transaction.account_id}`;
        
        if (nodeMap.has(sourceId) && nodeMap.has(targetId)) {
          links.push({
            source: nodeMap.get(sourceId),
            target: nodeMap.get(targetId),
            value: Math.abs(transaction.amount),
            category: transaction.category,
            type: 'income_flow'
          });
        }
      });

      // Create links for accounts -> expenses
      expenseTransactions.forEach(transaction => {
        const sourceId = `account_${transaction.account_id}`;
        const targetId = `expense_${transaction.category}`;
        
        if (nodeMap.has(sourceId) && nodeMap.has(targetId)) {
          links.push({
            source: nodeMap.get(sourceId),
            target: nodeMap.get(targetId),
            value: Math.abs(transaction.amount),
            category: transaction.category,
            type: 'expense_flow'
          });
        }
      });

    } else {
      // Account view: Source Accounts -> Target Accounts (transfers)
      // For now, we'll show account -> category flows more clearly
      
      accounts.forEach(account => {
        const nodeId = `source_${account.id}`;
        nodes.push({
          id: nodeId,
          name: `${account.nickname || account.name} (Source)`,
          type: 'source_account',
          color: getAccountColor(account.account_type),
          accountData: account,
          value: transactions
            .filter(t => t.account_id === account.id)
            .reduce((sum, t) => sum + Math.abs(t.amount), 0)
        });
        nodeMap.set(nodeId, nodes.length - 1);
      });

      // Create category nodes
      const allCategories = [...new Set(transactions.map(t => t.category))];
      allCategories.forEach(category => {
        const nodeId = `category_${category}`;
        nodes.push({
          id: nodeId,
          name: category,
          type: 'category',
          color: getCategoryColor(category),
          value: transactions
            .filter(t => t.category === category)
            .reduce((sum, t) => sum + Math.abs(t.amount), 0)
        });
        nodeMap.set(nodeId, nodes.length - 1);
      });

      // Create links from accounts to categories
      transactions.forEach(transaction => {
        const sourceId = `source_${transaction.account_id}`;
        const targetId = `category_${transaction.category}`;
        
        if (nodeMap.has(sourceId) && nodeMap.has(targetId)) {
          links.push({
            source: nodeMap.get(sourceId),
            target: nodeMap.get(targetId),
            value: Math.abs(transaction.amount),
            transactionType: transaction.transaction_type,
            type: 'account_category_flow'
          });
        }
      });
    }

    // Aggregate links with same source and target
    const linkMap = new Map();
    links.forEach(link => {
      const key = `${link.source}-${link.target}`;
      if (linkMap.has(key)) {
        linkMap.get(key).value += link.value;
      } else {
        linkMap.set(key, { ...link });
      }
    });

    return {
      nodes,
      links: Array.from(linkMap.values())
    };
  };

  const createSankeyDiagram = () => {
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove(); // Clear previous diagram

    const data = prepareDataForSankey();
    if (data.nodes.length === 0 || data.links.length === 0) {
      // Show empty state
      svg.append("text")
        .attr("x", width / 2)
        .attr("y", height / 2)
        .attr("text-anchor", "middle")
        .attr("fill", "#6b7280")
        .text("No transaction data available");
      return;
    }

    const sankeyGenerator = sankey()
      .nodeWidth(15)
      .nodePadding(10)
      .extent([[margin.left, margin.top], [width - margin.right, height - margin.bottom]]);

    const sankeyData = sankeyGenerator({
      nodes: data.nodes.map(d => ({ ...d })),
      links: data.links.map(d => ({ ...d }))
    });

    // Create gradient definitions for links
    const defs = svg.append("defs");
    
    sankeyData.links.forEach((link, i) => {
      const gradient = defs.append("linearGradient")
        .attr("id", `gradient-${i}`)
        .attr("gradientUnits", "userSpaceOnUse")
        .attr("x1", link.source.x1)
        .attr("y1", (link.source.y0 + link.source.y1) / 2)
        .attr("x2", link.target.x0)
        .attr("y2", (link.target.y0 + link.target.y1) / 2);

      gradient.append("stop")
        .attr("offset", "0%")
        .attr("stop-color", link.source.color);

      gradient.append("stop")
        .attr("offset", "100%")
        .attr("stop-color", link.target.color);
    });

    // Draw links
    const links = svg.append("g")
      .selectAll("path")
      .data(sankeyData.links)
      .enter()
      .append("path")
      .attr("d", sankeyLinkHorizontal())
      .attr("stroke", (d, i) => `url(#gradient-${i})`)
      .attr("stroke-width", d => Math.max(1, d.width))
      .attr("fill", "none")
      .attr("opacity", 0.6)
      .on("mouseover", function(event, d) {
        d3.select(this).attr("opacity", 0.8);
        
        // Show tooltip
        const tooltip = d3.select("body").append("div")
          .attr("class", "sankey-tooltip")
          .style("position", "absolute")
          .style("background", "rgba(0, 0, 0, 0.8)")
          .style("color", "white")
          .style("padding", "8px")
          .style("border-radius", "4px")
          .style("font-size", "12px")
          .style("pointer-events", "none")
          .style("z-index", 1000);

        tooltip.html(`
          <strong>${d.source.name}</strong> → <strong>${d.target.name}</strong><br>
          Amount: $${d.value.toFixed(2)}
        `)
        .style("left", (event.pageX + 10) + "px")
        .style("top", (event.pageY - 10) + "px");
      })
      .on("mouseout", function(event, d) {
        d3.select(this).attr("opacity", 0.6);
        d3.selectAll(".sankey-tooltip").remove();
      });

    // Draw nodes
    const nodes = svg.append("g")
      .selectAll("rect")
      .data(sankeyData.nodes)
      .enter()
      .append("rect")
      .attr("x", d => d.x0)
      .attr("y", d => d.y0)
      .attr("height", d => d.y1 - d.y0)
      .attr("width", d => d.x1 - d.x0)
      .attr("fill", d => d.color)
      .attr("stroke", d => selectedNode?.id === d.id ? "#000" : "none")
      .attr("stroke-width", 2)
      .attr("rx", 3)
      .style("cursor", "pointer")
      .on("click", function(event, d) {
        setSelectedNode(selectedNode?.id === d.id ? null : d);
        
        // If clicking on an account node, could switch to account view
        if (d.type === 'account' || d.type === 'source_account') {
          // Optional: auto-switch view mode
          // setViewMode('account');
        }
      })
      .on("mouseover", function(event, d) {
        d3.select(this).attr("stroke", "#000").attr("stroke-width", 1);
        
        // Highlight connected links
        links.attr("opacity", link => 
          (link.source === d || link.target === d) ? 0.8 : 0.3
        );
      })
      .on("mouseout", function(event, d) {
        d3.select(this).attr("stroke", selectedNode?.id === d.id ? "#000" : "none");
        
        // Reset link opacity
        links.attr("opacity", 0.6);
      });

    // Add node labels
    svg.append("g")
      .selectAll("text")
      .data(sankeyData.nodes)
      .enter()
      .append("text")
      .attr("x", d => d.x0 < width / 2 ? d.x1 + 6 : d.x0 - 6)
      .attr("y", d => (d.y1 + d.y0) / 2)
      .attr("dy", "0.35em")
      .attr("text-anchor", d => d.x0 < width / 2 ? "start" : "end")
      .attr("font-size", "12px")
      .attr("font-weight", d => selectedNode?.id === d.id ? "bold" : "normal")
      .text(d => d.name)
      .style("cursor", "pointer")
      .on("click", function(event, d) {
        setSelectedNode(selectedNode?.id === d.id ? null : d);
      });

    // Add value labels below node names
    svg.append("g")
      .selectAll("text")
      .data(sankeyData.nodes)
      .enter()
      .append("text")
      .attr("x", d => d.x0 < width / 2 ? d.x1 + 6 : d.x0 - 6)
      .attr("y", d => (d.y1 + d.y0) / 2 + 15)
      .attr("dy", "0.35em")
      .attr("text-anchor", d => d.x0 < width / 2 ? "start" : "end")
      .attr("font-size", "10px")
      .attr("fill", "#6b7280")
      .text(d => `$${d.value.toFixed(2)}`);
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center space-x-4">
              <Button 
                variant="ghost" 
                onClick={() => navigate('/dashboard')}
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Dashboard
              </Button>
              <div className="flex items-center space-x-2">
                <BarChart3 className="w-5 h-5 text-emerald-600" />
                <h1 className="text-xl font-bold text-gray-900">Money Flow Analysis</h1>
              </div>
            </div>
            
            {/* View Toggle */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 bg-gray-100 rounded-lg p-1">
                <Button
                  variant={viewMode === 'category' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setViewMode('category')}
                  className={viewMode === 'category' ? 'bg-emerald-600 text-white' : ''}
                >
                  Category View
                </Button>
                <Button
                  variant={viewMode === 'account' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setViewMode('account')}
                  className={viewMode === 'account' ? 'bg-emerald-600 text-white' : ''}
                >
                  Account View
                </Button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sankey Diagram */}
          <div className="lg:col-span-3">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>
                    {viewMode === 'category' ? 'Category Flow' : 'Account Flow'} Diagram
                  </span>
                  <div className="text-sm text-gray-600">
                    {transactions.length} transactions analyzed
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="w-full overflow-x-auto">
                  <svg
                    ref={svgRef}
                    width={width}
                    height={height}
                    className="border border-gray-200 rounded-lg"
                  />
                </div>
                <div className="mt-4 text-sm text-gray-600">
                  <p>
                    <strong>How to use:</strong> Click on nodes to highlight them, hover over flows to see amounts. 
                    Toggle between Category and Account views to see different perspectives of your money flow.
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Info Panel */}
          <div className="space-y-6">
            {/* Selected Node Info */}
            {selectedNode && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center">
                    <Eye className="w-5 h-5 mr-2" />
                    Selected Item
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center space-x-3">
                    <div 
                      className="w-4 h-4 rounded-full"
                      style={{ backgroundColor: selectedNode.color }}
                    />
                    <div>
                      <p className="font-semibold">{selectedNode.name}</p>
                      <p className="text-sm text-gray-600 capitalize">{selectedNode.type.replace('_', ' ')}</p>
                    </div>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-3">
                    <p className="text-sm text-gray-600">Total Value</p>
                    <p className="text-lg font-bold text-emerald-600">
                      {formatCurrency(selectedNode.value)}
                    </p>
                  </div>
                  {selectedNode.accountData && (
                    <div className="text-xs text-gray-500 space-y-1">
                      <p><strong>Bank:</strong> {selectedNode.accountData.bank_name}</p>
                      <p><strong>Type:</strong> {selectedNode.accountData.account_type.replace('_', ' ')}</p>
                      <p><strong>Balance:</strong> {formatCurrency(selectedNode.accountData.balance)}</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Legend */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Legend</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {viewMode === 'category' ? (
                  <>
                    <div className="space-y-2">
                      <h4 className="font-semibold text-sm text-gray-700">Income Categories</h4>
                      {categories.filter(cat => 
                        transactions.some(t => t.category === cat.name && t.transaction_type === 'credit')
                      ).map(category => (
                        <div key={category.id} className="flex items-center space-x-2 text-sm">
                          <div 
                            className="w-3 h-3 rounded-full"
                            style={{ backgroundColor: category.color }}
                          />
                          <span>{category.name}</span>
                        </div>
                      ))}
                    </div>
                    <div className="space-y-2">
                      <h4 className="font-semibold text-sm text-gray-700">Expense Categories</h4>
                      {categories.filter(cat => 
                        transactions.some(t => t.category === cat.name && t.transaction_type === 'debit')
                      ).map(category => (
                        <div key={category.id} className="flex items-center space-x-2 text-sm">
                          <div 
                            className="w-3 h-3 rounded-full"
                            style={{ backgroundColor: category.color }}
                          />
                          <span>{category.name}</span>
                        </div>
                      ))}
                    </div>
                  </>
                ) : (
                  <div className="space-y-2">
                    <h4 className="font-semibold text-sm text-gray-700">Account Types</h4>
                    <div className="flex items-center space-x-2 text-sm">
                      <div className="w-3 h-3 rounded-full bg-emerald-500" />
                      <span>Checking</span>
                    </div>
                    <div className="flex items-center space-x-2 text-sm">
                      <div className="w-3 h-3 rounded-full bg-blue-500" />
                      <span>Savings</span>
                    </div>
                    <div className="flex items-center space-x-2 text-sm">
                      <div className="w-3 h-3 rounded-full bg-amber-500" />
                      <span>Credit Card</span>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Quick Stats */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Quick Stats</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="bg-emerald-50 rounded-lg p-3">
                  <p className="text-sm text-emerald-700">Total Income</p>
                  <p className="text-lg font-bold text-emerald-800">
                    {formatCurrency(
                      transactions
                        .filter(t => t.transaction_type === 'credit')
                        .reduce((sum, t) => sum + Math.abs(t.amount), 0)
                    )}
                  </p>
                </div>
                <div className="bg-red-50 rounded-lg p-3">
                  <p className="text-sm text-red-700">Total Expenses</p>
                  <p className="text-lg font-bold text-red-800">
                    {formatCurrency(
                      transactions
                        .filter(t => t.transaction_type === 'debit')
                        .reduce((sum, t) => sum + Math.abs(t.amount), 0)
                    )}
                  </p>
                </div>
                <div className="bg-blue-50 rounded-lg p-3">
                  <p className="text-sm text-blue-700">Net Flow</p>
                  <p className="text-lg font-bold text-blue-800">
                    {formatCurrency(
                      transactions.reduce((sum, t) => 
                        sum + (t.transaction_type === 'credit' ? t.amount : -Math.abs(t.amount)), 0
                      )
                    )}
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
};

export default SankeyDiagram;