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
      setIsAnimating(true);
      const timer = setTimeout(() => {
        createFlowDiagram();
        setIsAnimating(false);
      }, 200);
      return () => clearTimeout(timer);
    }
  }, [transactions, accounts, categories, viewMode, selectedItem, hoveredItem]);

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

      gradient.append("stop")
        .attr("offset", "0%")
        .attr("stop-color", item.color)
        .attr("stop-opacity", 0.8);

      gradient.append("stop")
        .attr("offset", "100%")
        .attr("stop-color", item.color)
        .attr("stop-opacity", 0.3);
    });

    // Position income items on the RIGHT side of balance box
    const positionedIncome = data.incomeItems.map((item, i) => {
      const totalItems = data.incomeItems.length;
      const spacing = Math.min(80, 300 / Math.max(1, totalItems - 1)); // Dynamic spacing
      const startY = centerY - (totalItems - 1) * spacing / 2;
      
      return {
        ...item,
        x: centerX + centerBoxSize.width/2 + 150, // RIGHT side
        y: startY + i * spacing
      };
    });

    // Position expense items on the LEFT side of balance box
    const positionedExpenses = data.expenseItems.map((item, i) => {
      const totalItems = data.expenseItems.length;
      const spacing = Math.min(80, 300 / Math.max(1, totalItems - 1)); // Dynamic spacing
      const startY = centerY - (totalItems - 1) * spacing / 2;
      
      return {
        ...item,
        x: centerX - centerBoxSize.width/2 - 150, // LEFT side
        y: startY + i * spacing
      };
    });

    // Create curved flow paths
    const createFlowPath = (item, isIncome) => {
      const startX = item.x;
      const startY = item.y;
      const endX = centerX + (isIncome ? centerBoxSize.width/2 : -centerBoxSize.width/2);
      const endY = centerY;
      
      // Create smooth curved path
      const controlX = (startX + endX) / 2;
      const controlY = startY;
      
      return `M ${startX} ${startY} Q ${controlX} ${controlY} ${endX} ${endY}`;
    };

    // Draw income flows (from RIGHT to center)
    positionedIncome.forEach(item => {
      const maxStroke = 15;
      const strokeWidth = Math.max(3, Math.min(maxStroke, (item.amount / data.totalIncome) * maxStroke));
      
      svg.append("path")
        .attr("d", createFlowPath(item, true))
        .attr("stroke", item.color)
        .attr("stroke-width", strokeWidth)
        .attr("fill", "none")
        .attr("opacity", hoveredItem === item.id ? 0.9 : 0.6)
        .style("cursor", "pointer")
        .on("mouseover", function(event) {
          setHoveredItem(item.id);
          d3.select(this).attr("opacity", 0.9);
          
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
            <strong>${item.name}</strong><br>
            Amount: ${formatCurrency(item.amount)}
          `)
          .style("left", (event.pageX + 10) + "px")
          .style("top", (event.pageY - 10) + "px");
        })
        .on("mouseout", function() {
          setHoveredItem(null);
          d3.select(this).attr("opacity", 0.6);
          d3.selectAll(".sankey-tooltip").remove();
        })
        .on("click", function() {
          setSelectedItem(selectedItem === item.id ? null : item.id);
          setViewMode(viewMode === 'category' ? 'bank' : 'category');
        });
    });

    // Draw expense flows (from center to LEFT)
    positionedExpenses.forEach(item => {
      const maxStroke = 15;
      const strokeWidth = Math.max(3, Math.min(maxStroke, (item.amount / data.totalExpenses) * maxStroke));
      
      svg.append("path")
        .attr("d", createFlowPath(item, false))
        .attr("stroke", item.color)
        .attr("stroke-width", strokeWidth)
        .attr("fill", "none")
        .attr("opacity", hoveredItem === item.id ? 0.9 : 0.6)
        .style("cursor", "pointer")
        .on("mouseover", function(event) {
          setHoveredItem(item.id);
          d3.select(this).attr("opacity", 0.9);
          
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
            <strong>${item.name}</strong><br>
            Amount: ${formatCurrency(item.amount)}
          `)
          .style("left", (event.pageX + 10) + "px")
          .style("top", (event.pageY - 10) + "px");
        })
        .on("mouseout", function() {
          setHoveredItem(null);
          d3.select(this).attr("opacity", 0.6);
          d3.selectAll(".sankey-tooltip").remove();
        })
        .on("click", function() {
          setSelectedItem(selectedItem === item.id ? null : item.id);
          setViewMode(viewMode === 'category' ? 'bank' : 'category');
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
        handleViewToggle(viewMode === 'category' ? 'bank' : 'category');
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

    // Draw income items on RIGHT side
    positionedIncome.forEach(item => {
      const itemGroup = svg.append("g")
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
        .attr("r", Math.max(12, Math.min(25, Math.sqrt(item.amount) / 8)))
        .attr("fill", item.color)
        .attr("stroke", selectedItem === item.id ? "#000" : "#fff")
        .attr("stroke-width", selectedItem === item.id ? 3 : 2)
        .attr("opacity", hoveredItem === item.id ? 1.0 : 0.8);

      // Item label (to the right of circle)
      itemGroup.append("text")
        .attr("x", item.x + 35)
        .attr("y", item.y - 5)
        .attr("text-anchor", "start")
        .attr("font-size", "14px")
        .attr("font-weight", "600")
        .attr("fill", "#374151")
        .text(item.name);

      // Item amount (below label)
      itemGroup.append("text")
        .attr("x", item.x + 35)
        .attr("y", item.y + 10)
        .attr("text-anchor", "start")
        .attr("font-size", "12px")
        .attr("fill", "#16a34a")
        .attr("font-weight", "500")
        .text(`+${formatCurrency(item.amount)}`);
    });

    // Draw expense items on LEFT side
    positionedExpenses.forEach(item => {
      const itemGroup = svg.append("g")
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
        .attr("r", Math.max(12, Math.min(25, Math.sqrt(item.amount) / 8)))
        .attr("fill", item.color)
        .attr("stroke", selectedItem === item.id ? "#000" : "#fff")
        .attr("stroke-width", selectedItem === item.id ? 3 : 2)
        .attr("opacity", hoveredItem === item.id ? 1.0 : 0.8);

      // Item label (to the left of circle)
      itemGroup.append("text")
        .attr("x", item.x - 35)
        .attr("y", item.y - 5)
        .attr("text-anchor", "end")
        .attr("font-size", "14px")
        .attr("font-weight", "600")
        .attr("fill", "#374151")
        .text(item.name);

      // Item amount (below label)
      itemGroup.append("text")
        .attr("x", item.x - 35)
        .attr("y", item.y + 10)
        .attr("text-anchor", "end")
        .attr("font-size", "12px")
        .attr("fill", "#dc2626")
        .attr("font-weight", "500")
        .text(`-${formatCurrency(item.amount)}`);
    });

    // Add section headers
    svg.append("text")
      .attr("x", centerX - centerBoxSize.width/2 - 150)
      .attr("y", 40)
      .attr("text-anchor", "middle")
      .attr("font-size", "18px")
      .attr("font-weight", "700")
      .attr("fill", "#dc2626")
      .text("💸 Expenses");

    svg.append("text")
      .attr("x", centerX + centerBoxSize.width/2 + 150)
      .attr("y", 40)
      .attr("text-anchor", "middle")
      .attr("font-size", "18px")
      .attr("font-weight", "700")
      .attr("fill", "#16a34a")
      .text("💰 Income");
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const handleViewToggle = (newMode) => {
    console.log('Switching view mode from', viewMode, 'to', newMode);
    setIsAnimating(true);
    setViewMode(newMode);
    setSelectedItem(null);
    setHoveredItem(null);
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
                  onClick={() => handleViewToggle('category')}
                  className={`${viewMode === 'category' ? 'bg-emerald-600 text-white' : ''} transition-all duration-200`}
                >
                  <PieChart className="w-4 h-4 mr-2" />
                  By Category
                </Button>
                <Button
                  variant={viewMode === 'bank' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => handleViewToggle('bank')}
                  className={`${viewMode === 'bank' ? 'bg-emerald-600 text-white' : ''} transition-all duration-200`}
                >
                  <Building2 className="w-4 h-4 mr-2" />
                  By Bank
                </Button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Flow Diagram */}
          <div className="lg:col-span-3">
            <Card className="relative overflow-hidden">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span className="flex items-center space-x-2">
                    <BarChart3 className="w-5 h-5 text-emerald-600" />
                    <span>
                      Money Flow {viewMode === 'category' ? 'by Category' : 'by Bank'}
                    </span>
                  </span>
                  <div className="text-sm text-gray-600">
                    {transactions.length} transactions analyzed
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent className="relative">
                {isAnimating && (
                  <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center z-10">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600"></div>
                  </div>
                )}
                <div className="w-full overflow-x-auto">
                  <svg
                    ref={svgRef}
                    width={width}
                    height={height}
                    className="border border-gray-200 rounded-lg bg-gradient-to-br from-gray-50 to-white"
                  />
                </div>
                <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                  <h4 className="font-semibold text-blue-900 mb-2">🎯 How It Works:</h4>
                  <ul className="text-sm text-blue-800 space-y-1">
                    <li>• <strong>Toggle Views:</strong> Use "By Category" / "By Bank" buttons to switch perspectives</li>
                    <li>• <strong>Click Items:</strong> Click any income or expense item to switch to the alternate view</li>
                    <li>• <strong>Flow Lines:</strong> Thickness represents money amounts flowing to/from your net worth</li>
                    <li>• <strong>Central Box:</strong> Shows your net worth where all flows converge</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Info Panel */}
          <div className="space-y-6">
            {/* Current View Info */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center">
                  {viewMode === 'category' ? <PieChart className="w-5 h-5 mr-2" /> : <Building2 className="w-5 h-5 mr-2" />}
                  Current View
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="bg-gradient-to-r from-emerald-50 to-blue-50 rounded-lg p-3">
                  <p className="font-semibold text-gray-900">
                    {viewMode === 'category' ? '📊 By Category' : '🏦 By Bank'}
                  </p>
                  <p className="text-sm text-gray-600 mt-1">
                    {viewMode === 'category' 
                      ? 'Grouped by expense and income categories'
                      : 'Grouped by financial institutions'
                    }
                  </p>
                </div>
                <div className="text-center">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleViewToggle(viewMode === 'category' ? 'bank' : 'category')}
                    className="w-full"
                  >
                    Switch to {viewMode === 'category' ? 'Bank' : 'Category'} View
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Selected Item Info */}
            {selectedItem && (
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
                      style={{ backgroundColor: '#10b981' }}
                    />
                    <div>
                      <p className="font-semibold">{selectedItem}</p>
                      <p className="text-sm text-gray-600">Click to switch views</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Interactive Guide */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">💡 Interactive Features</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-emerald-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                      <span className="text-emerald-600 text-xs font-bold">1</span>
                    </div>
                    <div>
                      <p className="font-semibold text-sm">Toggle Views</p>
                      <p className="text-xs text-gray-600">Use header buttons to switch between Category and Bank views</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                      <span className="text-blue-600 text-xs font-bold">2</span>
                    </div>
                    <div>
                      <p className="font-semibold text-sm">Click Items</p>
                      <p className="text-xs text-gray-600">Click any income/expense item to auto-switch views</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                      <span className="text-purple-600 text-xs font-bold">3</span>
                    </div>
                    <div>
                      <p className="font-semibold text-sm">Flow Lines</p>
                      <p className="text-xs text-gray-600">Line thickness shows money amounts</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-amber-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                      <span className="text-amber-600 text-xs font-bold">4</span>
                    </div>
                    <div>
                      <p className="font-semibold text-sm">Central Hub</p>
                      <p className="text-xs text-gray-600">Click net worth box to switch views</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Quick Stats */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center">
                  <TrendingUp className="w-5 h-5 mr-2 text-emerald-600" />
                  Financial Summary
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="bg-gradient-to-r from-emerald-50 to-emerald-100 rounded-lg p-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-emerald-700 font-medium">💰 Total Income</p>
                      <p className="text-lg font-bold text-emerald-800">
                        {formatCurrency(
                          transactions
                            .filter(t => t.transaction_type === 'credit')
                            .reduce((sum, t) => sum + Math.abs(t.amount), 0)
                        )}
                      </p>
                    </div>
                    <TrendingUp className="w-6 h-6 text-emerald-600" />
                  </div>
                </div>
                
                <div className="bg-gradient-to-r from-red-50 to-red-100 rounded-lg p-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-red-700 font-medium">💸 Total Expenses</p>
                      <p className="text-lg font-bold text-red-800">
                        {formatCurrency(
                          transactions
                            .filter(t => t.transaction_type === 'debit')
                            .reduce((sum, t) => sum + Math.abs(t.amount), 0)
                        )}
                      </p>
                    </div>
                    <TrendingDown className="w-6 h-6 text-red-600" />
                  </div>
                </div>
                
                <div className="bg-gradient-to-r from-blue-50 to-indigo-100 rounded-lg p-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-blue-700 font-medium">📊 Net Flow</p>
                      <p className="text-lg font-bold text-blue-800">
                        {formatCurrency(
                          transactions.reduce((sum, t) => 
                            sum + (t.transaction_type === 'credit' ? t.amount : -Math.abs(t.amount)), 0
                          )
                        )}
                      </p>
                    </div>
                    <BarChart3 className="w-6 h-6 text-blue-600" />
                  </div>
                </div>
                
                <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-600 text-center">
                    📈 Data from {transactions.length} recent transactions
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