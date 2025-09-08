import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';
import { AuthContext } from '../App';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { 
  ArrowLeft, 
  Search, 
  Filter, 
  Plus,
  TrendingUp,
  TrendingDown,
  Calendar
} from 'lucide-react';

const TransactionList = () => {
  const [transactions, setTransactions] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    search: '',
    account_id: '',
    category: '',
    transaction_type: ''
  });
  const { API } = useContext(AuthContext);
  const navigate = useNavigate();

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    fetchTransactions();
  }, [filters]);

  const fetchData = async () => {
    try {
      const [transactionsRes, accountsRes, categoriesRes] = await Promise.all([
        axios.get(`${API}/transactions`),
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

  const fetchTransactions = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.account_id) params.append('account_id', filters.account_id);
      if (filters.category) params.append('category', filters.category);
      
      const response = await axios.get(`${API}/transactions?${params}`);
      let filtered = response.data;
      
      // Client-side filtering for search and transaction type
      if (filters.search) {
        filtered = filtered.filter(t => 
          t.description.toLowerCase().includes(filters.search.toLowerCase()) ||
          t.category.toLowerCase().includes(filters.search.toLowerCase())
        );
      }
      
      if (filters.transaction_type) {
        filtered = filtered.filter(t => t.transaction_type === filters.transaction_type);
      }
      
      setTransactions(filtered);
    } catch (error) {
      console.error('Failed to fetch transactions:', error);
      toast.error('Failed to load transactions');
    }
  };

  const handleFilterChange = (key, value) => {
    // Convert "all-*" values to empty strings for backend compatibility
    const processedValue = value?.startsWith('all-') ? '' : value;
    setFilters(prev => ({
      ...prev,
      [key]: processedValue
    }));
  };

  const clearFilters = () => {
    setFilters({
      search: '',
      account_id: '',
      category: '',
      transaction_type: ''
    });
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(Math.abs(amount));
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const getAccountName = (accountId) => {
    const account = accounts.find(a => a.id === accountId);
    return account ? account.name : 'Unknown Account';
  };

  const getCategoryColor = (categoryName) => {
    const category = categories.find(c => c.name === categoryName);
    return category ? category.color : '#6b7280';
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
              <h1 className="text-xl font-bold text-gray-900">All Transactions</h1>
            </div>
            <Button 
              onClick={() => navigate('/add-transaction')}
              className="bg-emerald-600 hover:bg-emerald-700"
            >
              <Plus className="w-4 h-4 mr-2" />
              Add Transaction
            </Button>
          </div>
        </div>
      </header>

      {/* Filters */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center text-lg">
              <Filter className="w-5 h-5 mr-2" />
              Filters
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {/* Search */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                <Input
                  placeholder="Search transactions..."
                  value={filters.search}
                  onChange={(e) => handleFilterChange('search', e.target.value)}
                  className="pl-10"
                />
              </div>

              {/* Account Filter */}
              <Select 
                value={filters.account_id} 
                onValueChange={(value) => handleFilterChange('account_id', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="All accounts" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all-accounts">All accounts</SelectItem>
                  {accounts.map((account) => (
                    <SelectItem key={account.id} value={account.id || 'no-value'}>
                      {account.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {/* Category Filter */}
              <Select 
                value={filters.category} 
                onValueChange={(value) => handleFilterChange('category', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="All categories" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all-categories">All categories</SelectItem>
                  {categories.map((category) => (
                    <SelectItem key={category.id} value={category.name || 'no-value'}>
                      <div className="flex items-center space-x-2">
                        <div 
                          className="w-3 h-3 rounded-full" 
                          style={{ backgroundColor: category.color }}
                        ></div>
                        <span>{category.name}</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {/* Type Filter */}
              <Select 
                value={filters.transaction_type} 
                onValueChange={(value) => handleFilterChange('transaction_type', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="All types" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all-types">All types</SelectItem>
                  <SelectItem value="credit">Income</SelectItem>
                  <SelectItem value="debit">Expense</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="mt-4">
              <Button variant="outline" onClick={clearFilters}>
                Clear Filters
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Transactions List */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Transactions ({transactions.length})</span>
              <div className="text-sm text-gray-600">
                Total: {formatCurrency(transactions.reduce((sum, t) => sum + Math.abs(t.amount), 0))}
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {transactions.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-500 mb-4">No transactions found</p>
                <Button onClick={() => navigate('/add-transaction')}>
                  <Plus className="w-4 h-4 mr-2" />
                  Add Your First Transaction
                </Button>
              </div>
            ) : (
              <div className="divide-y divide-gray-200">
                {transactions.map((transaction) => (
                  <div key={transaction.id} className="p-6 hover:bg-gray-50 transition-colors">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                          transaction.transaction_type === 'credit' 
                            ? 'bg-emerald-100 text-emerald-600' 
                            : 'bg-red-100 text-red-600'
                        }`}>
                          {transaction.transaction_type === 'credit' ? (
                            <TrendingUp className="w-6 h-6" />
                          ) : (
                            <TrendingDown className="w-6 h-6" />
                          )}
                        </div>
                        <div className="flex-1">
                          <h3 className="font-semibold text-gray-900">{transaction.description}</h3>
                          <div className="flex items-center space-x-4 text-sm text-gray-600 mt-1">
                            <div className="flex items-center space-x-1">
                              <div 
                                className="w-2 h-2 rounded-full" 
                                style={{ backgroundColor: getCategoryColor(transaction.category) }}
                              ></div>
                              <span>{transaction.category}</span>
                            </div>
                            <span>•</span>
                            <span>{getAccountName(transaction.account_id)}</span>
                            <span>•</span>
                            <div className="flex items-center space-x-1">
                              <Calendar className="w-3 h-3" />
                              <span>{formatDate(transaction.date)}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className={`text-xl font-bold ${
                          transaction.transaction_type === 'credit' 
                            ? 'text-emerald-600' 
                            : 'text-red-600'
                        }`}>
                          {transaction.transaction_type === 'credit' ? '+' : '-'}{formatCurrency(transaction.amount)}
                        </div>
                        <div className="text-sm text-gray-500 capitalize">
                          {transaction.transaction_type === 'credit' ? 'Income' : 'Expense'}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default TransactionList;