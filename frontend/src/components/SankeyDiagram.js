import React, { useState, useEffect, useRef, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';
import { AuthContext } from '../App';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { ArrowLeft, BarChart3, Eye, PieChart, Building2, TrendingUp, TrendingDown } from 'lucide-react';
import * as d3 from 'd3';

const SankeyDiagram = () => {
  const [transactions, setTransactions] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [viewMode, setViewMode] = useState('category'); // 'category' or 'bank'
  const [selectedItem, setSelectedItem] = useState(null);
  const [hoveredItem, setHoveredItem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAnimating, setIsAnimating] = useState(false);
  const svgRef = useRef();
  const { API } = useContext(AuthContext);
  const navigate = useNavigate();

  const width = 900;
  const height = 600;
  const centerX = width / 2;
  const centerY = height / 2;
  const centerBoxSize = { width: 180, height: 120 };
  const itemRadius = 220;

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

  const prepareFlowData = () => {
    const totalIncome = transactions
      .filter(t => t.transaction_type === 'credit')
      .reduce((sum, t) => sum + Math.abs(t.amount), 0);
    
    const totalExpenses = transactions
      .filter(t => t.transaction_type === 'debit')
      .reduce((sum, t) => sum + Math.abs(t.amount), 0);
    
    const netWorth = totalIncome - totalExpenses;

    if (viewMode === 'category') {
      // Group by categories
      const incomeByCategory = {};
      const expensesByCategory = {};
      
      transactions.forEach(transaction => {
        const amount = Math.abs(transaction.amount);
        if (transaction.transaction_type === 'credit') {
          incomeByCategory[transaction.category] = (incomeByCategory[transaction.category] || 0) + amount;
        } else {
          expensesByCategory[transaction.category] = (expensesByCategory[transaction.category] || 0) + amount;
        }
      });

      const incomeItems = Object.entries(incomeByCategory).map(([category, amount]) => ({
        id: `income_${category}`,
        name: category,
        amount,
        type: 'income',
        color: getCategoryColor(category),
        isBank: false
      }));

      const expenseItems = Object.entries(expensesByCategory).map(([category, amount]) => ({
        id: `expense_${category}`,
        name: category,
        amount,
        type: 'expense',
        color: getCategoryColor(category),
        isBank: false
      }));

      return { incomeItems, expenseItems, totalIncome, totalExpenses, netWorth };

    } else {
      // Group by banks
      const incomeByBank = {};
      const expensesByBank = {};
      
      transactions.forEach(transaction => {
        const account = accounts.find(acc => acc.id === transaction.account_id);
        const bankName = account ? account.bank_name : 'Unknown Bank';
        const amount = Math.abs(transaction.amount);
        
        if (transaction.transaction_type === 'credit') {
          incomeByBank[bankName] = (incomeByBank[bankName] || 0) + amount;
        } else {
          expensesByBank[bankName] = (expensesByBank[bankName] || 0) + amount;
        }
      });

      const incomeItems = Object.entries(incomeByBank).map(([bank, amount]) => ({
        id: `income_${bank}`,
        name: bank,
        amount,
        type: 'income',
        color: getBankColor(bank),
        isBank: true
      }));

      const expenseItems = Object.entries(expensesByBank).map(([bank, amount]) => ({
        id: `expense_${bank}`,
        name: bank,
        amount,
        type: 'expense',
        color: getBankColor(bank),
        isBank: true
      }));

      return { incomeItems, expenseItems, totalIncome, totalExpenses, netWorth };
    }
  };

  const getBankColor = (bankName) => {
    const bankColors = {
      'TD Bank': '#00b04f',
      'Chase': '#117aca',
      'Wells Fargo': '#d52b1e',
      'Bank of America': '#e31837',
      'Citibank': '#056dae',
      'Capital One': '#004977',
      'US Bank': '#0f4d92'
    };
    return bankColors[bankName] || '#6b7280';
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