import React, { useState, useEffect, useContext } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';
import { AuthContext } from '../App';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { 
  DollarSign, 
  Plus, 
  TrendingUp, 
  TrendingDown, 
  CreditCard, 
  PiggyBank,
  Wallet,
  LogOut,
  List,
  BarChart3,
  Settings,
  Activity
} from 'lucide-react';

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const { user, logout, API } = useContext(AuthContext);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await axios.get(`${API}/dashboard`);
      setDashboardData(response.data);
    } catch (error) {
      console.error('Dashboard error:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const getAccountIcon = (type) => {
    switch (type) {
      case 'checking':
        return <Wallet className="w-6 h-6" />;
      case 'savings':
        return <PiggyBank className="w-6 h-6" />;
      case 'credit_card':
        return <CreditCard className="w-6 h-6" />;
      default:
        return <DollarSign className="w-6 h-6" />;
    }
  };

  const getAccountColor = (type) => {
    switch (type) {
      case 'checking':
        return 'from-emerald-500 to-emerald-600';
      case 'savings':
        return 'from-blue-500 to-blue-600';
      case 'credit_card':
        return 'from-amber-500 to-amber-600';
      default:
        return 'from-gray-500 to-gray-600';
    }
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
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl flex items-center justify-center">
                <DollarSign className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Finance Tracker</h1>
                <p className="text-sm text-gray-600">Welcome back, {user?.name}</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <Link to="/add-transaction">
                <Button className="bg-emerald-600 hover:bg-emerald-700">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Transaction
                </Button>
              </Link>
              <Link to="/transactions">
                <Button variant="outline">
                  <List className="w-4 h-4 mr-2" />
                  View All
                </Button>
              </Link>
              <Link to="/analytics">
                <Button variant="outline">
                  <Activity className="w-4 h-4 mr-2" />
                  Analytics
                </Button>
              </Link>
              <Link to="/manage-accounts">
                <Button variant="outline">
                  <Settings className="w-4 h-4 mr-2" />
                  Manage Accounts
                </Button>
              </Link>
              <Button variant="outline" onClick={logout}>
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="bg-gradient-to-br from-emerald-500 to-emerald-600 text-white border-0">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-emerald-100 text-sm font-medium">Total Balance</p>
                  <p className="text-3xl font-bold">{formatCurrency(dashboardData?.total_balance || 0)}</p>
                </div>
                <TrendingUp className="w-8 h-8 text-emerald-200" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white border-0">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-blue-100 text-sm font-medium">Monthly Spending</p>
                  <p className="text-3xl font-bold">{formatCurrency(dashboardData?.monthly_spending || 0)}</p>
                </div>
                <TrendingDown className="w-8 h-8 text-blue-200" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-amber-500 to-amber-600 text-white border-0">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-amber-100 text-sm font-medium">Categories</p>
                  <p className="text-3xl font-bold">{Object.keys(dashboardData?.category_spending || {}).length}</p>
                </div>
                <BarChart3 className="w-8 h-8 text-amber-200" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Accounts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {dashboardData?.accounts?.map((account) => (
            <Card key={account.id} className="hover:shadow-lg transition-shadow duration-300">
              <CardHeader className="pb-3">
                <div className="flex items-center space-x-3">
                  <div className={`w-12 h-12 bg-gradient-to-br ${getAccountColor(account.account_type)} rounded-xl flex items-center justify-center text-white`}>
                    {getAccountIcon(account.account_type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <CardTitle className="text-lg truncate">
                      {account.nickname || account.name}
                    </CardTitle>
                    <CardDescription className="capitalize">
                      {account.bank_name} • {account.account_type.replace('_', ' ')}
                    </CardDescription>
                    {account.nickname && account.nickname !== account.name && (
                      <p className="text-xs text-gray-500 truncate mt-1">{account.name}</p>
                    )}
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="text-right">
                    <p className={`text-2xl font-bold ${account.balance >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                      {formatCurrency(account.balance)}
                    </p>
                  </div>
                  {account.description && (
                    <div className="bg-gray-50 rounded-lg p-2">
                      <p className="text-xs text-gray-600 line-clamp-2">{account.description}</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Recent Transactions */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Transactions List */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                Recent Transactions
                <Link to="/transactions" className="text-sm text-emerald-600 hover:text-emerald-700 font-medium">
                  View All
                </Link>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {dashboardData?.recent_transactions?.slice(0, 5).map((transaction) => (
                <div key={transaction.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{transaction.description}</p>
                    <p className="text-sm text-gray-600">{transaction.category} • {formatDate(transaction.date)}</p>
                  </div>
                  <div className="text-right">
                    <p className={`font-semibold ${transaction.transaction_type === 'credit' ? 'text-emerald-600' : 'text-red-600'}`}>
                      {transaction.transaction_type === 'credit' ? '+' : ''}{formatCurrency(transaction.amount)}
                    </p>
                  </div>
                </div>
              ))}
              {(!dashboardData?.recent_transactions || dashboardData.recent_transactions.length === 0) && (
                <div className="text-center py-8 text-gray-500">
                  <p>No transactions yet</p>
                  <Link to="/add-transaction" className="text-emerald-600 hover:text-emerald-700 font-medium">
                    Add your first transaction
                  </Link>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Category Spending */}
          <Card>
            <CardHeader>
              <CardTitle>Category Spending (This Month)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {Object.entries(dashboardData?.category_spending || {}).slice(0, 6).map(([category, amount]) => (
                  <div key={category} className="flex items-center justify-between">
                    <span className="text-gray-700 font-medium">{category}</span>
                    <span className="text-gray-900 font-semibold">{formatCurrency(amount)}</span>
                  </div>
                ))}
                {Object.keys(dashboardData?.category_spending || {}).length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    <p>No spending data available</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;