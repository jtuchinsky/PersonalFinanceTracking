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

  const createFlowDiagram = () => {
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove(); // Clear previous diagram

    const data = prepareFlowData();
    if (!data.incomeItems.length && !data.expenseItems.length) {
      // Show empty state
      svg.append("text")
        .attr("x", width / 2)
        .attr("y", height / 2)
        .attr("text-anchor", "middle")
        .attr("fill", "#6b7280")
        .text("No transaction data available");
      return;
    }

    // Create gradient definitions
    const defs = svg.append("defs");
    
    // Create gradients for flows
    [...data.incomeItems, ...data.expenseItems].forEach((item, i) => {
      const gradient = defs.append("linearGradient")
        .attr("id", `flow-gradient-${item.id}`)
        .attr("gradientUnits", "userSpaceOnUse");

      if (item.type === 'income') {
        gradient.attr("x1", centerX - centerBoxSize.width/2)
               .attr("y1", centerY)
               .attr("x2", centerX + centerBoxSize.width/2)
               .attr("y2", centerY);
      } else {
        gradient.attr("x1", centerX + centerBoxSize.width/2)
               .attr("y1", centerY)
               .attr("x2", centerX - centerBoxSize.width/2)
               .attr("y2", centerY);
      }

      gradient.append("stop")
        .attr("offset", "0%")
        .attr("stop-color", item.color)
        .attr("stop-opacity", 0.8);

      gradient.append("stop")
        .attr("offset", "100%")
        .attr("stop-color", item.color)
        .attr("stop-opacity", 0.3);
    });

    // Position items in circular layout
    const positionItems = (items, side) => {
      return items.map((item, i) => {
        const totalItems = items.length;
        const angle = (i / Math.max(1, totalItems - 1)) * Math.PI - Math.PI/2; // Spread across semicircle
        const adjustedAngle = side === 'left' ? Math.PI - angle : angle;
        
        return {
          ...item,
          x: centerX + Math.cos(adjustedAngle) * itemRadius,
          y: centerY + Math.sin(adjustedAngle) * itemRadius * 0.6, // Compress vertically
          angle: adjustedAngle
        };
      });
    };

    const positionedIncome = positionItems(data.incomeItems, 'left');
    const positionedExpenses = positionItems(data.expenseItems, 'right');

    // Create curved flow paths
    const createFlowPath = (item, isIncome) => {
      const startX = item.x;
      const startY = item.y;
      const endX = centerX + (isIncome ? -centerBoxSize.width/2 : centerBoxSize.width/2);
      const endY = centerY;
      
      const midX = (startX + endX) / 2;
      const midY = Math.min(startY, endY) - 30; // Create curve above
      
      return `M ${startX} ${startY} Q ${midX} ${midY} ${endX} ${endY}`;
    };

    // Draw income flows
    const incomeFlows = svg.append("g").attr("class", "income-flows");
    
    positionedIncome.forEach(item => {
      const maxStroke = 20;
      const strokeWidth = Math.max(2, Math.min(maxStroke, (item.amount / data.totalIncome) * maxStroke));
      
      incomeFlows.append("path")
        .attr("d", createFlowPath(item, true))
        .attr("stroke", `url(#flow-gradient-${item.id})`)
        .attr("stroke-width", strokeWidth)
        .attr("fill", "none")
        .attr("opacity", hoveredItem === item.id ? 0.9 : 0.6)
        .style("cursor", "pointer")
        .on("mouseover", function() {
          setHoveredItem(item.id);
          d3.select(this).attr("opacity", 0.9);
        })
        .on("mouseout", function() {
          setHoveredItem(null);
          d3.select(this).attr("opacity", 0.6);
        })
        .on("click", function() {
          setSelectedItem(selectedItem === item.id ? null : item.id);
          if (viewMode === 'category') {
            setViewMode('bank');
          } else {
            setViewMode('category');
          }
        });
    });

    // Draw expense flows
    const expenseFlows = svg.append("g").attr("class", "expense-flows");
    
    positionedExpenses.forEach(item => {
      const maxStroke = 20;
      const strokeWidth = Math.max(2, Math.min(maxStroke, (item.amount / data.totalExpenses) * maxStroke));
      
      expenseFlows.append("path")
        .attr("d", createFlowPath(item, false))
        .attr("stroke", `url(#flow-gradient-${item.id})`)
        .attr("stroke-width", strokeWidth)
        .attr("fill", "none")
        .attr("opacity", hoveredItem === item.id ? 0.9 : 0.6)
        .style("cursor", "pointer")
        .on("mouseover", function() {
          setHoveredItem(item.id);
          d3.select(this).attr("opacity", 0.9);
        })
        .on("mouseout", function() {
          setHoveredItem(null);
          d3.select(this).attr("opacity", 0.6);
        })
        .on("click", function() {
          setSelectedItem(selectedItem === item.id ? null : item.id);
          if (viewMode === 'category') {
            setViewMode('bank');
          } else {
            setViewMode('category');
          }
        });
    });

    // Draw central balance box
    const balanceGroup = svg.append("g").attr("class", "balance-box");
    
    balanceGroup.append("rect")
      .attr("x", centerX - centerBoxSize.width/2)
      .attr("y", centerY - centerBoxSize.height/2)
      .attr("width", centerBoxSize.width)
      .attr("height", centerBoxSize.height)
      .attr("rx", 12)
      .attr("fill", data.netWorth >= 0 ? "#dcfce7" : "#fef2f2")
      .attr("stroke", data.netWorth >= 0 ? "#16a34a" : "#dc2626")
      .attr("stroke-width", 2)
      .style("filter", "drop-shadow(0 4px 6px rgba(0, 0, 0, 0.1))")
      .style("cursor", "pointer")
      .on("click", function() {
        setViewMode(viewMode === 'category' ? 'bank' : 'category');
      });

    // Balance box content
    balanceGroup.append("text")
      .attr("x", centerX)
      .attr("y", centerY - 20)
      .attr("text-anchor", "middle")
      .attr("font-size", "14px")
      .attr("font-weight", "600")
      .attr("fill", "#6b7280")
      .text("Net Worth");

    balanceGroup.append("text")
      .attr("x", centerX)
      .attr("y", centerY + 5)
      .attr("text-anchor", "middle")
      .attr("font-size", "18px")
      .attr("font-weight", "700")
      .attr("fill", data.netWorth >= 0 ? "#16a34a" : "#dc2626")
      .text(formatCurrency(data.netWorth));

    balanceGroup.append("text")
      .attr("x", centerX)
      .attr("y", centerY + 25)
      .attr("text-anchor", "middle")
      .attr("font-size", "10px")
      .attr("fill", "#9ca3af")
      .text("Click to switch view");

    // Draw income items
    const incomeGroup = svg.append("g").attr("class", "income-items");
    
    positionedIncome.forEach(item => {
      const itemGroup = incomeGroup.append("g")
        .attr("class", "income-item")
        .style("cursor", "pointer")
        .on("click", function() {
          setSelectedItem(selectedItem === item.id ? null : item.id);
          setViewMode(viewMode === 'category' ? 'bank' : 'category');
        })
        .on("mouseover", function() {
          setHoveredItem(item.id);
        })
        .on("mouseout", function() {
          setHoveredItem(null);
        });

      // Item circle
      itemGroup.append("circle")
        .attr("cx", item.x)
        .attr("cy", item.y)
        .attr("r", Math.max(8, Math.min(25, Math.sqrt(item.amount) / 5)))
        .attr("fill", item.color)
        .attr("stroke", selectedItem === item.id ? "#000" : "#fff")
        .attr("stroke-width", selectedItem === item.id ? 3 : 2)
        .attr("opacity", hoveredItem === item.id ? 0.9 : 0.7);

      // Item label
      itemGroup.append("text")
        .attr("x", item.x)
        .attr("y", item.y - 35)
        .attr("text-anchor", "middle")
        .attr("font-size", "12px")
        .attr("font-weight", "600")
        .attr("fill", "#374151")
        .text(item.name);

      // Item amount
      itemGroup.append("text")
        .attr("x", item.x)
        .attr("y", item.y - 20)
        .attr("text-anchor", "middle")
        .attr("font-size", "10px")
        .attr("fill", "#16a34a")
        .text(`+${formatCurrency(item.amount)}`);
    });

    // Draw expense items
    const expenseGroup = svg.append("g").attr("class", "expense-items");
    
    positionedExpenses.forEach(item => {
      const itemGroup = expenseGroup.append("g")
        .attr("class", "expense-item")
        .style("cursor", "pointer")
        .on("click", function() {
          setSelectedItem(selectedItem === item.id ? null : item.id);
          setViewMode(viewMode === 'category' ? 'bank' : 'category');
        })
        .on("mouseover", function() {
          setHoveredItem(item.id);
        })
        .on("mouseout", function() {
          setHoveredItem(null);
        });

      // Item circle
      itemGroup.append("circle")
        .attr("cx", item.x)
        .attr("cy", item.y)
        .attr("r", Math.max(8, Math.min(25, Math.sqrt(item.amount) / 5)))
        .attr("fill", item.color)
        .attr("stroke", selectedItem === item.id ? "#000" : "#fff")
        .attr("stroke-width", selectedItem === item.id ? 3 : 2)
        .attr("opacity", hoveredItem === item.id ? 0.9 : 0.7);

      // Item label
      itemGroup.append("text")
        .attr("x", item.x)
        .attr("y", item.y - 35)
        .attr("text-anchor", "middle")
        .attr("font-size", "12px")
        .attr("font-weight", "600")
        .attr("fill", "#374151")
        .text(item.name);

      // Item amount
      itemGroup.append("text")
        .attr("x", item.x)
        .attr("y", item.y - 20)
        .attr("text-anchor", "middle")
        .attr("font-size", "10px")
        .attr("fill", "#dc2626")
        .text(`-${formatCurrency(item.amount)}`);
    });

    // Add income/expense section labels
    svg.append("text")
      .attr("x", 80)
      .attr("y", 40)
      .attr("font-size", "16px")
      .attr("font-weight", "700")
      .attr("fill", "#16a34a")
      .text("💰 Income");

    svg.append("text")
      .attr("x", width - 80)
      .attr("y", 40)
      .attr("text-anchor", "end")
      .attr("font-size", "16px")
      .attr("font-weight", "700")
      .attr("fill", "#dc2626")
      .text("💸 Expenses");
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